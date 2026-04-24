# Agent Pattern Extraction — from Reference Agent to Platform

Phase 2 close-out deliverable for the Symphonix Health agent-first strategy. Companion to [agent-eclaims-reference.md](agent-eclaims-reference.md) §6.3, which promised the pattern-extraction artefacts once the reference agent landed.

## Purpose

The reference agent ([insurance-eclaims](../../insurance-eclaims) medical-necessity advisor) is the single canonical implementation through which every Tier 1 and Tier 2 agent migration flows. This document extracts the patterns so the next agent is not a one-off reimplementation — and the one after that is not another one.

Five artefacts are extracted. Each one has a name, a home, an interface, and an enforcement check so it cannot rot into suggestion.

## 1. Agent Scaffold Template (CAID-Driven)

**Home:** [caid-agent](../../caid-agent) — a new skill `agent-ify-service` that takes a target repo, an entry point, and a capability-card stub, and emits the scaffold that the reference agent shipped with.

**What it emits** (mirrors [insurance-eclaims/backend/src/agent/](../../insurance-eclaims/backend/src/agent/)):

```
<repo>/backend/src/agent/
  __init__.py                — public surface
  models.py                  — AgentRecommendation ORM sibling table
  schemas.py                 — Pydantic AgentOutput with closed-vocabulary invariants
  phi_guard.py               — regex PHI detector (SSN / MRN / DOB / phone / email / known names)
  recommender.py             — Recommender protocol + StubRecommender + LLMRecommender seam
  pending_sweeper.py         — kill-switch-gated sweeper (ECLAIMS_AGENT_ENABLED)
  card.py                    — capability-card loader
  agent_card.json            — A2A HealthcareAgentCard (one file, two registries)
  attestation.py             — SignalBox envelope builder
  prompts/
    <domain>.yaml            — prompt-engine PromptSpec
<repo>/backend/tests/
  test_agent_schemas.py      — output-contract invariants
  test_agent_phi_guard.py    — PHI detection
  test_agent_recommender.py  — stub branches + LLMRecommender mock-tested seam
  test_agent_sweeper.py      — sweeper dispatch + idempotency + kill-switch
  test_agent_seed_shadow.py  — integration against seeded DB
  test_agent_card_and_attestation.py
  test_agent_scenarios.py    — loads scenarios/*.json via emulator-kit
  agent/scenarios/
    <domain>_approve.json
    <domain>_deny.json
    <domain>_rfi.json
    <domain>_abstain_ood.json
    phi_leak_guardrail.json
```

**Template variables:** `<domain>` (e.g., `medical_necessity`), `<action_vocabulary>` (closed list of actions), `<carc_vocabulary>` (closed-code list appropriate to the domain), `<sweeper_entry_predicate>` (how to detect claims / cases the agent should pick up), `<hitl_level>` (launch always `advisory`).

**Enforcement:** the CAID skill refuses to emit the scaffold unless the capability-card stub passes [card.py](../../insurance-eclaims/backend/src/agent/card.py) `card_minimum_fields()` and the sweeper predicate returns a non-empty set for the seed fixtures.

**What the template deliberately does NOT emit:** live LLM wiring (the `LLMRecommender` stays a seam with pluggable Protocols), GHARRA registration calls, SignalBox runtime hooks. Those are per-deployment, not per-repo — see §4 and §5.

## 2. GHARRA Capability-Card JSON Schema

**Home:** [global-agent-registry](../../global-agent-registry) `schemas/healthcare-agent-card.schema.json` — JSON Schema 2020-12, matching the `HealthcareAgentCard` Pydantic model in `src/gharra/core/monetisation_models.py:371`.

**What it adds beyond what the model already enforces:**

- Pattern constraint on `capabilities.autonomy` — must be one of the [governance-agents.md §1](governance-agents.md) levels (`shadow` / `advisory` / `threshold_advisory` / `threshold_autonomous` / `autonomous`).
- Pattern constraint on `healthcare.regulatory_status.classification` — must be one of [regulatory-agents.md §7](regulatory-agents.md) levels (`administrative` / `CDS` / `SaMD` / `medical_device`).
- Cross-field invariant: if `capabilities.autonomy` is level 3+, `healthcare.regulatory_status.classification` must be `CDS` or above.
- Cross-field invariant: if `healthcare.safety.break_glass_supported=true`, `capabilities.autonomy` must be level 2+.
- Cross-field invariant: if `healthcare.safety.phi_egress=true`, `authentication.schemes` must include at least one of `mtls` or `oauth2`.

**Enforcement:** validated at agent-registration time by GHARRA's gateway middleware. Registration rejects cards that violate the invariants. The existing runtime validation in [card.py](../../insurance-eclaims/backend/src/agent/card.py) adds a matching client-side check so a broken card surfaces in CI before the deployment.

**Schema versioning:** semver on the `$id`; GHARRA accepts any card validated against schema 1.x. Breaking changes (2.0) require a coordinated migration — the registry rejects 1.x cards at the version boundary, not silently.

## 3. HITL Checkpoint Library

**Home:** a new package `hitl-checkpoints` published as a source-only library under `symphonix-bridge-sdk/src/hitl/` (it is genuinely cross-cutting; it belongs next to the other cross-cutting primitives). The React primitives it exposes live under `design-system/src/hitl/`.

**What it ships — three Python-side primitives:**

| Primitive | Purpose | Contract |
|---|---|---|
| `ThresholdGate(confidence_floor, dollar_floor, risk_floor)` | "Human above threshold, agent below" rule | `.decide(recommendation) -> {"auto": bool, "reason": str}` |
| `CohortGate(cohort_predicate)` | Named cohorts always route to human | `.decide(patient_context) -> bool` |
| `ReviewerSLA(primary_hours, team_lead_hours, director_hours)` | Escalation-ladder clock | `.tick_timeout(escalation) -> NextRung \| None` |

These mirror the patterns in [governance-agents.md §1–2](governance-agents.md) but are reusable code rather than prose. Every new agent instantiates them with its own thresholds; the governance surface is the same.

**What it ships — two React primitives (in design-system):**

| Component | Purpose | Props |
|---|---|---|
| `<AgentRecommendationPanel>` | The sidebar shown on a pended case | `{ recommendation, onAccept, onOverride, allowedActions, showConfidenceBar }` |
| `<BreakGlassNotice>` | The banner on a case that was break-glassed | `{ event, grace_window_hours, onComposeRationale }` |

**Enforcement:** the reference agent's reviewer panel (next deliverable after this doc) is the first consumer. Every subsequent agent's UI uses the same primitives or justifies why not. The design-system Storybook has an `agent-hitl` story section specifically for these primitives.

## 4. SignalBox Attestation Recipe

**Home:** extends [signalbox-mcp/docs/](../../signalbox-mcp) with `docs/attestation-recipes.md`. The Python-side envelope builder already exists ([attestation.py](../../insurance-eclaims/backend/src/agent/attestation.py)) and is the first recipe.

**Recipe 1: backend-only admin decision (reference agent)**

- Produced by: `build_recommendation_envelope(rec)` at decision-persist time.
- Contains: structured codes, payload hash, `fhir_fragments` with agent-tagged `ClaimResponse`.
- Does NOT contain: rationale text (by design — the envelope is structural evidence, not narrative).
- Signed by: SignalBox at reviewer-capture time. The backend envelope is a **draft** that SignalBox merges into a full `CaptureManifest`.

**Recipe 2: clinical decision with UI-reviewer capture (future Tier 1 agents)**

- Produced by: SignalBox's `capture_clinical_signal` MCP tool during the reviewer session.
- Contains: screenshot + DOM + FHIR fragments + GHARRA ledger anchor + Ed25519 signature.
- Used when: the agent's `decision_type` is `advisory` or above AND the decision is clinical (CSAA classification `CDS` or higher).

**Recipe 3: admin decision with no UI capture (background sweepers)**

- Produced by: `build_recommendation_envelope(rec)` alone; the envelope stands on its own.
- Signed by: a deploy-time signing key rather than SignalBox. Requires a deployed `ECLAIMS_AGENT_SIGNING_KEY` and a mirror in GHARRA's JWKS.
- Used when: a decision is persisted but no reviewer session will ever open it (e.g., auto-approvals after threshold-autonomy promotion).

**Enforcement:** the agent capability card's `healthcare.safety.phi_egress=false` for the reference agent, which implicitly selects recipes 1 and 3. An agent cannot ship recipe 2 without `decision_type >= advisory` and a CSAA `CDS+` classification — the schema invariants in §2 enforce this.

## 5. Emulator-Kit Scenario Recipe

**Home:** a short recipe doc under `symphonix-emulator-kit/docs/scenario-recipe.md` plus the reference scenarios under [insurance-eclaims/backend/tests/agent/scenarios/](../../insurance-eclaims/backend/tests/agent/scenarios/).

**The recipe:**

1. One JSON file per scenario. Top-level object; loader [`scenarios.load_scenarios`](../../symphonix-emulator-kit/src/symphonix_emulator_kit/scenarios.py:23) reads `*.json` only. (Design-note wording was "YAML"; the real loader is JSON — fixed in the design note.)
2. Every scenario declares `scenario_id`, `uc_id`, `requirements`, `dependencies.{emulator,operation_id}`, `harness`, `input`, `expected`.
3. `harness` is one of `sweeper` (end-to-end through the pend-reason filter), `recommender` (bypass sweeper for stub-coverage), or a named adversarial path (`phi_leak` in the reference).
4. `expected` uses the keys `action`, `carc_code`, `rarc_code_present`, `min_confidence`, `confidence_equals`, `missing_fields_len`, `missing_fields_min`, `rationale_contains`, `rationale_excludes`. Unrecognised keys are a test error, not silently ignored.
5. Five scenarios minimum per agent: one per action in the closed vocabulary + one PHI-leak adversarial. Corpus-level invariants (closed-vocabulary coverage, all-actions-covered, UC+requirements declared) are tested automatically — see [test_agent_scenarios.py](../../insurance-eclaims/backend/tests/test_agent_scenarios.py).

**Enforcement:** the CAID `agent-ify-service` skill (§1) emits five scenarios by default. The test harness fails if the closed-vocabulary or all-actions invariants break. The emulator-kit's `extract_expectations` projects the scenarios into touchpoint coverage — the coverage diff is the PR-time signal.

## 6. What Is Promoted When

The five artefacts land at different points in the Phase-2 close-out. This table makes the ordering explicit so nothing is assumed-done.

| Artefact | Landing point | Blocker for |
|---|---|---|
| Agent scaffold template (§1) | Before Tier 1 agent rank 2 (pharmacy prior-auth) begins | Tier 1 rank 2+ |
| GHARRA card schema (§2) | Before any agent talks to a second GHARRA peer | Cross-org deployments |
| HITL checkpoint library (§3) | Before reviewer-UI panel lands | Reviewer-UI panel |
| SignalBox attestation recipe (§4) | Before any clinical-classified agent ships | Tier 1 ranks 2–5 that are clinical |
| Emulator-kit scenario recipe (§5) | Already landed with the reference agent | Nothing — but it is the contract every Tier 1+ agent tests against |

Four of the five land before Tier 1 rank 2 (pharmacy prior-auth) begins. The fifth (scenario recipe) is already in.

## 7. Anti-Patterns — Not to be Extracted

Called out so the pattern-extraction does not accidentally lift these:

- **A shared "AgentBase" class that every agent inherits.** Resist. Each agent's decision logic is different; sharing a base class couples their release cadence. The shared surface is the **capability-card schema**, not a class.
- **A single prompt-engine YAML reused across agents.** Resist. Each agent is a different role; sharing a prompt means sharing a hallucination. Reuse clauses, not specs.
- **A generic "LLM fallback" wrapper that retries across providers transparently.** Resist. Provider diversity is a config choice, not a runtime transparency. A specific deployment picks a specific provider. Cross-provider fallback hides failure modes that the audit chain needs to surface.
- **Auto-promotion of an agent past HITL-always without human sign-off.** Forbidden outright by [governance-agents.md §1.1](governance-agents.md). This is a runtime check, not just a doc.

## 8. Enforcement Checklist

A new Tier 1+ agent landing PR is not complete until every row below is either ticked or explicitly justified:

- [ ] Scaffold generated via CAID `agent-ify-service` skill (§1), or the deviation is documented in the PR.
- [ ] Capability card validates against the JSON Schema (§2).
- [ ] HITL checkpoints use the library primitives (§3) unless the agent's launch posture is `shadow`.
- [ ] Attestation envelope uses recipe 1, 2, or 3 (§4) — explicitly chosen in the PR.
- [ ] Scenarios follow the recipe (§5); corpus-level invariants pass.

---

## Status

Draft — Phase 2 close-out deliverable. Extracts the five promised artefacts from [agent-eclaims-reference.md](agent-eclaims-reference.md) §6.3. The reviewer-UI panel remains the one un-landed Phase 2 item; it is the first consumer of §3.
