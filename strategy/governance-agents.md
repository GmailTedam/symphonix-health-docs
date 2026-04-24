# Agent Governance — HITL, Escalation, Break-Glass

Phase 3 deliverable for the Symphonix Health agent-first strategy. Companion to [agent-first.md](agent-first.md) §7 (four gates) and [agent-eclaims-reference.md](agent-eclaims-reference.md) §7 (per-agent HITL UI).

## Purpose

The reference agent establishes that an agent can ship safely. This document establishes the rules that keep the **second**, **fifth**, and **fiftieth** agent safe. Once more than one clinical agent is live, HITL patterns, escalation ladders, and break-glass recipes need to be codified, not emergent.

Everything here is enforceable — each pattern maps to a runtime check, a metric, or a review gate that blocks promotion. Aspirational governance without enforcement is governance fiction.

## Scope

Applies to every agent registered through GHARRA whose capability card declares `scope=internal` or `scope=cross_org`. Does **not** apply to:

- Deterministic rule engines ([insurance-eclaims](../../insurance-eclaims) adjudication steps 1–10 except 7).
- UI code, design-system components, FHIR IG publication, other doc/contract repos.
- Traditional APIs serving legacy consumers (per the backward-compat invariant in [agent-first.md §3.1](agent-first.md)).

## 1. The HITL Spectrum

Agent autonomy is **never binary**. Every agent has a documented position on the following spectrum, recorded in its capability card's `healthcare.safety.decision_type` field:

| Level | Name | Who decides | Card value |
|---|---|---|---|
| 0 | Shadow | Human — agent output invisible to reviewer | `shadow` |
| 1 | HITL-always | Human — agent output advisory | `advisory` |
| 2 | Threshold-HITL | Human above threshold, agent below | `threshold_advisory` |
| 3 | Threshold-autonomy | Agent above confidence floor, human below | `threshold_autonomous` |
| 4 | Full autonomy | Agent — human audit only | `autonomous` |

**Launch is always level 1.** No agent launches at level 2 or higher. The reference agent in [agent-eclaims-reference.md §9](agent-eclaims-reference.md) specifies the promotion path; this document specifies the **gate criteria** for each step on that path.

### 1.1 Promotion gate criteria

Moving from level N to N+1 requires **all** of the following for the specific denial-category (or decision class):

| From → To | Agreement rate over N≥10 000 decisions | Overturn rate stable (week-over-week variance) | Stop-loss monitor configured | Regulatory re-classification if clinical |
|---|---|---|---|---|
| 0 → 1 | n/a — enabled on ship | n/a | n/a | n/a |
| 1 → 2 | ≥ 0.90 | variance ≤ 2 percentage points | threshold-HITL reversion on sustained breach | — |
| 2 → 3 | ≥ 0.95 for the auto-decided sub-class | variance ≤ 1 percentage point | same, tighter reversion SLA | CSAA re-classification from `administrative` to `CDS` if clinical reasoning |
| 3 → 4 | not permitted at any level without explicit regulator engagement | — | — | required |

Promotion is **per-class, not per-agent**. A pharmacy prior-auth agent may be level 2 for benzodiazepines and level 1 for oncology — the same agent, different decision classes.

### 1.2 Demotion

Any of the following demote an agent **one full level** automatically, with a logged event, and require re-earning promotion:

- Rolling 7-day agreement rate drops below the current level's threshold.
- Overturn rate variance exceeds the configured limit for two consecutive weeks.
- A break-glass event (§3) occurs and is sustained (not rolled back inside the grace window).
- A regulatory notice, legal hold, or incident-review finding requires it.

Demotion is a runtime automatic action, not a manual process. The system owns this — no human approval is required to make an agent safer.

## 2. Escalation Ladder

Every agent decision has a named route to a human. The ladder is not aspirational — each rung has a contact, an SLA, and a fallback.

### 2.1 The four rungs

| Rung | Who | When | SLA | Fallback if rung times out |
|---|---|---|---|---|
| 1 | Primary reviewer | Every advisory / threshold-HITL decision | 2 h clinical, 4 h admin | Reassign to rung 2 queue |
| 2 | Reviewer team lead | Rung 1 timeout, or explicit reviewer escalation | 4 h | Page rung 3 on-call |
| 3 | Clinical / operational director | Rung 2 timeout, or policy-edge decision | 24 h | Invoke break-glass (§3) |
| 4 | Chief Safety Officer | Rung 3 timeout, recurring break-glass, regulatory notice | 48 h | Freeze the agent (§4) |

### 2.2 What escalation actually does

Escalation is not just routing to a human — it carries context forward. At each rung, the escalation payload must include:

- Agent recommendation (action, CARC/RARC where applicable, rationale, cited policies, confidence).
- Every human touch so far (reviewer decisions, comments, time-in-queue).
- The full `RuleContext` that fed the agent, redacted per the agent's capability card.
- A stable `escalation_id` so the same decision re-entering the ladder deduplicates rather than forking.

Escalation that drops context is escalation that re-asks the human to reconstruct the problem. That is a governance failure, not an operational convenience.

## 3. Break-Glass

Break-glass is not "autonomy override" — it is "this decision cannot wait; I am taking the action and accepting the audit consequence." It exists because real clinical situations do not pause for reviewer SLAs.

### 3.1 Who may invoke

- Clinician personas whose IAM group carries `break_glass=true` in the GHARRA registry.
- Automated rules triggered by defined operational conditions (e.g., mass-casualty event, declared outage) only when the agent in question has `healthcare.safety.break_glass_supported=true` in its card.

The reference agent ([agent-eclaims-reference.md](agent-eclaims-reference.md)) sets `break_glass_supported=false` because launch posture is HITL-always. Break-glass is meaningless without autonomy.

### 3.2 What invocation does

1. **Marks the event** — emits a GHARRA-signed event to the `agent.break_glass` topic with the invoker identity, reason code, and decision payload.
2. **Notifies the audit chain** — the claim / case record carries a `break_glass_ref` pointing at the event hash.
3. **Notifies downstream** — provider-portal (or the relevant UI) surfaces the break-glass flag on the case; the reviewer team lead is paged.
4. **Does not disable HITL** — break-glass is a specific decision; the agent's HITL posture for subsequent decisions is unchanged.
5. **Starts the grace clock** — the invoker has a configured window (typically 24 h) to produce a retrospective rationale. Missing the window auto-escalates to rung 3 (§2.1).

### 3.3 What invocation does NOT do

- **Does not flip an agent to higher autonomy.** The agent's promotion level is unchanged; only this one decision bypasses the normal gate.
- **Does not expand PHI access.** Break-glass callers see what their IAM group permits. If they need more, that is a separate, audited elevation.
- **Does not amend history.** A break-glass record, once written, is immutable like any audit entry. Correction is by compensating entry, not by edit.

### 3.4 Review

Every break-glass event is reviewed within 7 days by the Chief Safety Officer or delegate. Review outcomes are one of:

- **Justified** — the event closes; the agent's posture is unchanged.
- **Justified-with-finding** — the event closes; a pattern finding is added to the agent's change backlog.
- **Unjustified** — the invoker's break-glass entitlement is reviewed; a pattern finding is added; if repeated, the entitlement is revoked.

## 4. Freeze

Freeze is the nuclear rollback: the agent's sweeper stops firing, its GHARRA capability card flips to `status=frozen`, and its reviewer UI panel is replaced with a freeze notice pointing at the incident record.

### 4.1 Triggers

- Recurring break-glass events (≥ 3 in a rolling 30-day window for the same agent).
- Overturn rate breaching the hard safety threshold (2× the promotion-gate limit).
- A regulatory notice, legal hold, or incident-review direction.
- A PHI-leak guardrail trip rate above the hard threshold (see [agent-eclaims-reference.md §8](agent-eclaims-reference.md)).
- Chief Safety Officer discretion.

### 4.2 What freeze preserves

Freeze is reversible. No data is dropped. Specifically:

- The `AgentRecommendation` table (or equivalent) is preserved — historical decisions stay queryable for the incident investigation.
- The agent's capability card is retained in `status=frozen` so consumers discover the state, not a 404.
- The deterministic pipeline the agent augments continues to run. Legacy consumers see no change — the backward-compat invariant holds through freeze.

### 4.3 Thaw

Unfreezing requires: a written incident report, a regression test covering the freeze trigger, and an explicit CSAA re-classification where a clinical agent has been frozen for > 30 days. Thaw is always to level 0 (shadow) first, regardless of the agent's pre-freeze level. Promotion runs again from zero.

## 5. Audit Chain

Every governance action above is an event on a hash-chained audit log. The chain is append-only and carries:

- `actor_role` — `system`, `clinician`, `reviewer`, `admin`, `cso`.
- `agent_id` — the GHARRA URI of the agent.
- `event_type` — one of `decision`, `override`, `escalation`, `break_glass`, `demotion`, `freeze`, `thaw`, `promotion`.
- `payload_sha256` — hash of the structured payload.
- `prev_hash` — chain link.
- `correlation_id` — per-claim / per-case.

The chain is what makes the governance surface **enforceable**. A rule no one can verify is a rule no one follows. Consumers of the chain include: the CSO review dashboard, the regulator evidence pack, the promotion-gate computation, and the incident-response runbook.

## 6. Mapping to the Four Gates

Cross-reference to [agent-first.md §7.1](agent-first.md):

| Gate | What this document adds |
|---|---|
| CSAA classification | §1.1 demands re-classification at level 2→3; §4 demands re-classification after > 30-day freeze |
| GHARRA registration | §1 requires the autonomy level live in the capability card; §4.2 requires `status=frozen` to be observable |
| Emulator-kit coverage | §1.1 promotion metric requires ≥ 10 000 decisions — emulator scenarios seed the first thousand before production shadow does the rest |
| HITL checkpoint | This whole document. §2 is the escalation ladder; §3 is the break-glass recipe; §4 is the rollback |

## 7. What Is Explicitly Not Defined Here

Called out to prevent scope drift:

- **Reviewer UI primitives.** A React component library for threshold gates, review panels, and freeze notices is a separate deliverable under [agent-eclaims-reference.md §7](agent-eclaims-reference.md). This document specifies the contract; the UI implements it.
- **Regulatory posture** (FDA SaMD, MHRA, EMA, NMPA, TGA). That lives in `regulatory-agents.md` — the next Phase 3 doc. This document assumes that posture exists but does not specify it.
- **Billing and metering.** GHARRA handles per-agent billing. Nothing in this document changes billing posture.
- **Performance / latency SLOs.** An agent that meets every governance rule and misses its latency budget is still failing — but that is operations, not governance.

## 8. Enforcement Checklist

A new agent landing PR is not complete until every row below is either ticked or explicitly justified:

- [ ] Capability card declares `decision_type` on the §1 spectrum (launch = `advisory`).
- [ ] Capability card declares `break_glass_supported` (launch = `false` unless explicitly justified).
- [ ] Escalation ladder §2 has a named primary reviewer queue configured.
- [ ] Escalation payload §2.2 carries all four required fields.
- [ ] Demotion monitor §1.2 is configured with concrete thresholds.
- [ ] Freeze trigger §4.1 thresholds are concrete, not placeholders.
- [ ] Audit-chain events §5 are emitted for every governance action.
- [ ] Backward-compat: no pre-existing API contract or test has been modified.

The enforcement check is run at PR time; passing it is a merge gate.

---

## Status

Draft — Phase 3 deliverable #1. Companion `regulatory-agents.md` is next.
