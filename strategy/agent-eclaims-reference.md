# Reference Agent — `insurance-eclaims` Adjudication Reasoner

Companion to [agent-first.md](agent-first.md) §6. This document is the engineering spec for the first Tier 1 agent in the Symphonix Health agent-first migration.

## 0. TL;DR

Existing state: [insurance-eclaims/backend/src/adjudication.py](../../insurance-eclaims/backend/src/adjudication.py) already runs a deterministic 10-step rules engine. Step 7 — `step_medical_necessity` — already marks `deterministic=False` on fail and pends the claim to human review.

The reference agent **does not replace** the rules engine. It augments the single non-deterministic breakpoint (`medical_necessity` pend) with a reasoning layer that produces a structured rationale, cited policy, and recommended action for the human reviewer. Everything else stays deterministic. This is the least-risky way to land agent-first: the agent touches only the decisions a human was already going to make, and it produces evidence, not verdicts.

Shadow-mode → threshold-HITL → threshold-autonomy is the promotion path. Launch configuration is HITL-always on every agent decision.

## 1. Why This Shape

Four reasons the agent augments rather than replaces:

1. **Regulatory posture stays low.** An agent that only writes rationales for human reviewers is not a Clinical Decision Support tool in most regulatory regimes. The human is still the decider. CSAA classification stays at `administrative` for launch.
2. **The deterministic engine is the audit anchor.** Every verdict row already carries `actor_role='system'` with a reproducible rule trace. Layering an agent under the rules engine would muddy that anchor.
3. **Promotion path is clean.** Agent → human-override logs are the training signal. You promote the agent past HITL-always only when its recommendations agree with human reviewers above a measured threshold, per denial-category.
4. **No schema change.** The existing `AdjudicationVerdict` row persists `pended_for_review` already. The agent writes a new sibling row (`AgentRecommendation`) that links to the verdict but does not replace it.

## 2. Agent Boundaries

This section satisfies the legacy-compatibility invariant in [agent-first.md §3.1](agent-first.md). The agent **only adds**; it does not touch any code path a legacy EDI or REST consumer relies on.

### In scope

- Read the `RuleContext` for a claim that the rules engine pended to review (currently only `medical_necessity` branch).
- Read the CARC/RARC code space plus the clinical LCD / benefit-criteria references for the pended line(s).
- Produce a structured recommendation: `{approve, deny-with-carc, request-information}` plus rationale, cited policy, and confidence.
- Emit a GHARRA-signed `AgentRecommendation` record and a SignalBox attestation.
- Expose a Nexus A2A capability card for external payer-side callers (v2 scope; v1 is internal-only).

### Out of scope

- Any auto-approval or auto-denial without a human in the loop at launch.
- Any branch of the 10-step engine other than `medical_necessity`. If a future branch becomes non-deterministic (e.g., COB), it is a **new** agent configuration, not a quiet extension of this one.
- Any modification to the existing `adjudicate_claim` or `persist_outcome` code paths. The agent hooks via a new sweeper, not by editing the rules engine.
- Any modification to the existing X12 837 / 835 / 270 / 271 / 278 / 277CA EDI pipeline, REST routes, or their response payloads. Legacy provider AR systems and payer integrations keep talking to the service exactly as they do today.
- Any modification to existing ORM tables (`Claim`, `ClaimLine`, `AdjudicationVerdict`, `Denial`, etc.). The agent writes one new sibling table (`AgentRecommendation`). No existing column is renamed, dropped, or has its semantics changed.
- Any re-routing that makes a legacy REST / EDI call pay for LLM latency or tokens. Legacy callers do not opt into agent reasoning by accident.

**Compliance check for this agent:** the pre-existing backend test suite must continue to pass unmodified after the agent lands. The agent's own tests are additive. If a legacy test needs to change, the design is wrong.

## 3. Decision Surface

Closed action vocabulary (no free text):

| Action | When | Downstream |
|---|---|---|
| `recommend_approve` | Agent believes the service is medically necessary | Human reviewer sees "agent: approve" with rationale; reviewer decides |
| `recommend_deny` | Agent believes denial is warranted; must cite CARC + policy | Human reviewer sees "agent: deny CARC-50" with rationale |
| `recommend_request_information` | Agent cannot decide with evidence on file | Human reviewer sees "agent: RFI" with the missing-field list |
| `abstain` | Agent confidence below floor | Recommendation is elided from reviewer UI; only logged |

`abstain` is a first-class outcome. It prevents noise in the reviewer UI and is the correct response to out-of-distribution claims.

## 4. Reasoning Contract

### 4.1 Inputs

All inputs already exist as typed dataclasses or ORM rows — no new schema needed:

- `RuleContext` from `backend/src/adjudication.py` (claim, member, plan, eligibility, prior_auths, contracted_rates, prior_claim_ccns).
- The offending `ClaimLine` (the one triggering `medical_necessity` pend).
- The CARC/RARC catalogue (`shared/codes`).
- A prompt-pack of policy references keyed by CPT range (v1 is a stub dict; v2 pulls from an LCD knowledge store).

### 4.2 Prompt assembly

Use [prompt-engine](../../prompt-engine) `PromptEngine.assemble` with:

- **Role** — `payer_medical_director_advisor` (new role; written to the prompt-engine healthcare bundle).
- **Clauses** — `context_first`, `structured_examples` (3 examples: one approve, one deny, one RFI), `cite_policy`, `adaptive_thinking`, `confidence_floor`, `abstention_allowed`, `phi_redacted_output`.
- **Reasoning mode** — `evidence_then_decision` (clauses enforce: state evidence → cite policy → state decision → state confidence).
- **Policies** — `no_free_text_action`, `carc_vocabulary_closed`, `no_patient_identifiers_in_rationale`.

### 4.3 Outputs

Strict JSON, validated before persistence:

```json
{
  "action": "recommend_approve|recommend_deny|recommend_request_information|abstain",
  "carc_code": "CARC_50|null",
  "rarc_code": "N115|null",
  "rationale": "string (no PHI; policy-cited)",
  "cited_policies": ["LCD-L35000", "CMS NCD 220.2"],
  "missing_fields": ["operative_note", "pathology_report"],
  "confidence": 0.0,
  "model_version": "claude-opus-4-7",
  "prompt_hash": "sha256:..."
}
```

Validation rejects:
- `action="recommend_deny"` with no `carc_code`.
- `action="recommend_request_information"` with empty `missing_fields`.
- `confidence < 0.55` with any action other than `abstain`.
- Any PHI token in `rationale` (name, MRN, DOB, full address) — detected with a pre-flight regex + Bridge SDK PHI detector.

## 5. Where the Code Lives

New module in the existing backend, no cross-repo imports:

```
backend/src/agent/
  __init__.py                   — public: run_agent_for_pended_claim
  recommender.py                — the core: prompt assembly, model call, output validation
  pending_sweeper.py            — periodic sweeper: find pended claims, dispatch agent
  attestation.py                — SignalBox + GHARRA signing hook (v1 stub, v2 real)
  models.py                     — AgentRecommendation ORM row (new table)
  prompts/
    medical_necessity.yaml      — prompt-engine PromptSpec
    examples.yaml               — 3 few-shot examples per CPT family
tests/agent/
  test_recommender.py           — unit
  test_pending_sweeper.py       — integration
  test_output_validation.py     — schema + PHI guardrails
  scenarios/                    — emulator-kit scenarios (JSON, per
                                  the symphonix_emulator_kit.scenarios
                                  loader contract — that loader reads
                                  *.json only; YAML is not supported)
    medical_necessity_approve.json
    medical_necessity_deny.json
    medical_necessity_rfi.json
    medical_necessity_abstain_ood.json  — out-of-distribution
    phi_leak_guardrail.json             — adversarial
```

One new ORM table (`AgentRecommendation`): `id`, `claim_id` FK, `verdict_id` FK (nullable; may precede verdict), `action`, `carc_code`, `rarc_code`, `rationale`, `cited_policies_json`, `missing_fields_json`, `confidence`, `model_version`, `prompt_hash`, `created_at`, `human_decision` (nullable, filled later), `human_decision_at` (nullable), `override` (bool, computed).

The `human_decision` fields are the training-signal columns. Everything the promotion path needs is recoverable from this one table.

## 6. Governance — the Four Gates

Mapping to the four gates in [agent-first.md §7.1](agent-first.md):

| Gate | How it is satisfied for this agent |
|---|---|
| CSAA classification | `administrative` at launch (agent writes rationale, human decides). Re-classify to `CDS` only when the agent is promoted past HITL-always — that triggers hazard-log seeding automatically. |
| GHARRA registration | Capability card published with `capability=adjudication.medical_necessity.recommend`, `scope=internal`, `phi=redacted_output_only`, `autonomy=recommendation_only`. v2 adds `scope=cross_org` for payer-side A2A callers. |
| Emulator-kit coverage | Five scenarios in `tests/agent/scenarios/` — happy-approve, happy-deny, RFI, abstain (OOD), PHI-leak adversarial. Target ≥ 90% branch coverage on `recommender.py`. |
| HITL checkpoint | Launch = HITL-always. Reviewer UI lives in the existing payer-adjudicator console (new panel only). Break-glass is N/A at launch because no autonomy. |

## 7. HITL UI Contract

Minimal change to the existing payer-adjudicator console:

- On a pended claim row, a new sidebar panel `Agent recommendation` shows: action, CARC if any, rationale, cited policies, missing fields, confidence bar.
- The reviewer's existing verdict buttons are unchanged. Their click is the decision. The agent recommendation is advisory.
- A checkbox records whether the reviewer's final verdict matched the agent recommendation; it defaults to auto-computed on submit.

No new reviewer workflow. The agent slot is additive.

## 8. Metrics

All metrics are per-denial-category and per-agent-version. Recorded from commit of the first shadow-mode run.

**Decision-quality**
- `agent_reviewer_agreement_rate` — how often reviewer's final verdict matches `action`.
- `agent_overturn_rate` — how often reviewer goes the other way.
- `agent_abstain_rate` — share of claims where agent declined to decide.
- `agent_confidence_calibration` — observed agreement rate binned by confidence decile.

**Operational**
- `agent_latency_p50 / p95` — prompt assembly + model + validation.
- `agent_cost_per_decision_usd` — tokens in + out × model price.
- `hitl_queue_depth` and `hitl_burn_down_time`.

**Safety**
- `phi_leak_guardrail_trips` — count of times the PHI guard rejected output.
- `schema_validation_failures` — count of times output failed validation.

Dashboards land in `analytics-bi` once it comes online under Tier 2; until then metrics are scraped from the `AgentRecommendation` table and emitted as JSONL.

## 9. Promotion Path

Agent moves from HITL-always through two gates:

1. **Threshold-HITL (first promotion).** When `agent_reviewer_agreement_rate ≥ 0.90` over ≥ 10 000 decisions in a denial-category, with `agent_overturn_rate` stable, the agent may auto-approve claims in that category where `confidence ≥ 0.85`. All other decisions still route to human.
2. **Threshold-autonomy (second promotion).** When Threshold-HITL has sustained the above metrics for an additional 10 000 decisions, the category's auto-approval confidence floor may be relaxed to `0.75`, subject to a rolling overturn-rate monitor that reverts to Threshold-HITL automatically if the rate drifts.

No agent is ever autonomous on `deny`. Denials always require a human. This is the single hard rule.

## 10. Rollback

Three levers, smallest blast-radius first:

1. **Kill-switch config flag** (`ECLAIMS_AGENT_ENABLED=0`) disables the sweeper. Deterministic engine still runs; pended claims just sit in review with no agent recommendation attached. Reversible in seconds.
2. **Rollback to last model version** by updating `ECLAIMS_AGENT_MODEL_VERSION`. Every recommendation is tagged with the version that produced it, so historical analysis is unaffected.
3. **Full rollback**: drop the `AgentRecommendation` table and remove the `agent/` package. The deterministic engine is untouched; the rollback cannot regress claim adjudication.

## 11. Acceptance Criteria for Phase 2 Exit

Phase 2 of [agent-first.md](agent-first.md) §8 exits when:

- [ ] All files under `backend/src/agent/` and `tests/agent/` exist, type-check, and lint clean.
- [ ] Five emulator-kit scenarios pass in CI.
- [ ] PHI-leak guardrail test passes adversarially (agent cannot be induced to echo patient name).
- [ ] `AgentRecommendation` table migrates up and down cleanly.
- [ ] Kill-switch config flag verified end-to-end.
- [ ] The agent is running in shadow mode against the seeded claim set with measurable (non-zero, non-100%) agreement rate — i.e., it really is deciding, not always-approving.
- [ ] At least one of each action (`approve`, `deny`, `rfi`, `abstain`) has been produced on the seeded set.
- [ ] Prompt-pack YAML and role `payer_medical_director_advisor` are published back to [prompt-engine](../../prompt-engine) healthcare bundle.

## 12. Status

Draft — this is the Phase-2 spec. On acceptance, code scaffold proceeds in the order listed in §5, with tests arriving alongside each module per the "test every step" discipline.
