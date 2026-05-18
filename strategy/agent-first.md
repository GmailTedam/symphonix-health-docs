# AI Agent-First Strategy — Symphonix Health Ecosystem

## Executive Summary

Symphonix Health already owns the building blocks of a healthcare AI-agent platform. What is missing is the connecting narrative: which primitives compose into an agent stack, which services should migrate behind that stack, in what order, and under what governance. This document supplies that narrative.

The strategy rests on three observations surfaced by a full-workspace audit:

1. **The agent platform exists but is unconsolidated.** Ten repos already provide identity (GHARRA), coordination (Nexus A2A), orchestration (CAID), reasoning (Prompt Engine), attestation (SignalBox), protocol translation (Bridge SDK), emulation (Emulator Kit), integration fabric (BulletTrain), safety gating (CSAA), and research grounding (Health Agent Workspace). No single document wires them into a coherent platform story today.
2. **Not every service should become an agent.** Deterministic rule engines (ERP GL posting), stateless routers (scheduling-gateway), and observability harnesses (triage-api) are better left as traditional software. Agent-first is a property to be earned, not applied uniformly.
3. **A small number of clinical and administrative workflows — insurance claims adjudication, clinical pathway deviation, pharmacy prior-auth, ambulance dispatch, clinician inbox triage — have outsized agent-fit.** These align with both GHARRA Tier-A market priorities and the Gates/OpenAI Horizon 1000 funding thesis, and they are the right first targets.

This document defines the scoring framework, the prioritised transition list, the governance posture, and a phased roadmap to move from scattered primitives to a named, competitive, auditable agent platform.

### Design Principles

The following principles are load-bearing and should be cited when future decisions appear to deviate from this strategy.

1. **Agents augment the API surface; they never replace it.** The existing REST / FHIR / X12 EDI / HL7v2 / DICOM / event-bus API surfaces across every repo must remain fully intact and functional for their intended consumers. An agent is **one** way to interact with a service; the API is **another**, and the API is not deprecated, thinned, or silently routed-through-agent. Agent-first is strictly additive — a value-add layer for capable consumers, not a gate everyone has to pass through. Cross-sibling platform data exchange remains BulletTrain-mediated per [BulletTrain Integration Doctrine](bullettrain-integration-doctrine.md). See §3.1 for what this rules out.
2. **Agent-fit is measurable.** A service becomes a candidate when it scores on reasoning density, orchestration need, signal richness, and governance fit (see §4). Aesthetic "this feels agentic" is not a justification.
3. **Every clinical agent runs behind CSAA + GHARRA + Nexus A2A.** Safety classification, identity, and coordination are non-negotiable pre-conditions for any patient-facing agent. Administrative agents may relax Nexus A2A but never CSAA.
4. **Agents replace judgement, not CRUD.** If the work is "write row, read row, update row," it is not a candidate. If the work is "given these signals, decide which of N actions to take and justify it to an audit chain," it is.
5. **Human-in-the-loop is the default.** Full autonomy is an earned privilege granted by measured false-positive rate and regulatory review, not the launch configuration.
6. **Reference agent before scale.** One canonical agent (`insurance-eclaims` adjudication) is built end-to-end through the full stack before a second candidate is started. Patterns extracted from the reference agent drive all subsequent migrations.
7. **Emulator-first validation.** No agent goes into a real integration until [symphonix-emulator-kit](../../symphonix-emulator-kit) scenarios exercise its decision surface across at least the happy path plus three adversarial cases.

---

## 1. Current State — the Platform You Already Own

| Layer | Repo | What it provides |
|---|---|---|
| Identity / trust / routing | [global-agent-registry](../../global-agent-registry) | GHARRA federated registry; 13-point route admission; DID trust; discovery |
| Coordination protocol | [nexus-a2a-protocol](../../nexus-a2a-protocol) | JSON-RPC 2.0 A2A with task lifecycle; 25 reference clinical agents; Clinician Avatar; Command Centre |
| Multi-role orchestrator | [caid-agent](../../caid-agent) | 10 base + 3 meta + 6 conditional engineer roles; 440-pattern advisory; V-model verification |
| Prompt / reasoning layer | [prompt-engine](../../prompt-engine) | 18-clause DSL; 8 reasoning modes; 4 governance policies; healthcare renderer |
| Protocol translation | [symphonix-bridge-sdk](../../symphonix-bridge-sdk) | FHIR-canonical pivot over HL7v2, DICOM, X12, CDA, MCP, A2A, Kafka, gRPC, WS, SSE |
| Browser-attested evidence | [signalbox-mcp](../../signalbox-mcp) | 20 MCP tools; GHARRA-signed clinical signal capture; replay; visual QA |
| Integration fabric + events | [BulletTrain](../../BulletTrain) | FHIR EventBus; 160+ microservices; design system; emulator substrate |
| External-system emulation | [symphonix-emulator-kit](../../symphonix-emulator-kit) | Fixture / LLM / proxy backends; `@touchpoint` coverage; scenario loader |
| Clinical safety gatekeeper | [csaa](../../csaa) | DCB0129/0160 scope classifier; hazard-log seeding; CSO sign-off gate |
| Governance research | [health-agent-workspace](../../health-agent-workspace) | GHARRA Tier-A inventory; Horizon 1000 alignment; SE-agent literature review |

**Interpretation.** This is a functioning agent platform — it just hasn't been described as one in a single place. The strategic act is less "build" and more "name, sequence, and govern."

---

## 2. What "Agent-First" Means Here

Agent-first is not a rewrite mandate. It is a **default disposition**: when a new capability or a significant change is considered, the first architectural question is "does this belong behind an agent?" and the bar to answer "no" is stated, scored, and recorded.

Concretely, a Symphonix Health agent is:

- **Discoverable** via GHARRA with a signed capability card.
- **Reachable** via Nexus A2A (clinical) or an equivalent governed transport (administrative).
- **Grounded** by Prompt Engine clauses and FHIR-canonical inputs from Bridge SDK.
- **Gated** by CSAA classification before deployment.
- **Observable** via SignalBox attestation for clinical outputs and a standard metric set for administrative ones.
- **Reversible** — every autonomous decision is either idempotent, carries a compensating action, or is staged behind a HITL checkpoint.

Services that do not meet this shape are either (a) not candidates or (b) candidates that still need platform work before migration.

---

## 3. Non-Goals

This strategy explicitly does not pursue the following in its first two phases. They are called out to prevent scope drift.

- **Agent-ifying deterministic logic.** ERP general-ledger posting, FHIR IG publication, and UI kits remain traditional code.
- **Rewriting elocute.** The RL-driven curriculum is already an agentic architecture; it is a pattern donor, not a migration target.
- **Competing with Epic on feature count.** Differentiation is architecture and auditability, not a breadth race.
- **Full autonomy at launch.** Every Tier 1 agent launches with a HITL checkpoint. Autonomy is earned per-metric, per-agent.
- **Multiple reference agents in parallel.** One canonical reference (§6) is completed before a second Tier 1 agent begins.

### 3.1 Legacy-Compatibility Invariant (rules out)

Per design principle #1, the existing API surface of every repo stays fully functional for non-agent consumers. This explicitly rules out the following as agent-first work:

- **Deprecating or removing existing REST / FHIR / X12 EDI / HL7v2 / DICOM endpoints.** The endpoints ship as they are today and continue to serve their original consumers with unchanged semantics, payloads, and latency profiles.
- **Modifying existing ORM tables beyond additive nullable columns.** Agents write to **new** sibling tables (e.g., `AgentRecommendation` alongside `AdjudicationVerdict`); they never mutate, rename, or drop existing columns.
- **Turning an existing endpoint into a façade that secretly invokes an agent.** Legacy callers must not pay an LLM's latency or cost budget unless they opt in explicitly through a distinct agent-facing route.
- **Forcing every integration through GHARRA / Nexus A2A.** These layers exist for agent-to-agent trust. Traditional external clients continue to call the service's own public REST / EDI gateway directly where that gateway is explicitly part of the service contract, authenticated by its own pre-agent mechanisms (JWT, AS2, SFTP, mTLS as applicable). This does not weaken the BulletTrain rule: sibling-to-sibling platform data exchange is still mediated through BulletTrain.
- **Any change that requires a pre-existing integration test to be modified.** If an agent-landing PR cannot keep the legacy suite green unchanged, the design is wrong and needs a re-think, not a test update.

The practical check before every agent-landing PR: **does the pre-existing integration test suite pass unmodified?** If yes, the additive invariant is likely satisfied. If a test had to change, that is a red flag requiring explicit justification in the PR description.

---

## 4. Transition Framework — the ROSG Score

Each service is scored 1–5 on four axes. Candidates with total ≥ 16 enter Tier 1; 12–15 enter Tier 2; below 12 are not candidates in the current horizon.

| Axis | Question | Low (1) | High (5) |
|---|---|---|---|
| **R — Reasoning density** | Does the workflow need judgement beyond CRUD? | Pure entity CRUD | Multi-factor decision with defensible rationale |
| **O — Orchestration need** | Does it coordinate across services or actors? | Single service, single actor | Multi-service, multi-actor, time-sensitive |
| **S — Signal richness** | Is there enough grounded data to decide? | Thin fields, no FHIR context | FHIR bundle + event stream + historical context |
| **G — Governance fit** | Can CSAA classify, GHARRA route, HITL gate it? | Ambiguous scope, no audit trail | Closed action vocabulary, clean audit, clear HITL point |

Scores are recorded in each candidate's tier entry in §5 and reviewed at each roadmap phase gate.

---

## 5. Candidate Inventory

### 5.1 Tier 1 — Strongest Candidates (≥ 16)

These are pursued in Phases 1–2. Each is mapped to a GHARRA Tier-A priority where applicable.

| Rank | Repo | Candidate agent | R | O | S | G | Total | GHARRA anchor |
|---|---|---|---|---|---|---|---|---|
| 1 | [insurance-eclaims](../../insurance-eclaims) | Claims adjudication + appeals agent | 5 | 4 | 5 | 5 | **19** | Tier-A #4 Prior Auth |
| 2 | [clinical-pathways](../../clinical-pathways) | Pathway-deviation + escalation agent | 5 | 5 | 4 | 4 | **18** | Tier-A #2 Triage (adjacent) |
| 3 | [pharmacy-system](../../pharmacy-system) | Prior-auth + interaction-reasoning agent | 5 | 4 | 4 | 5 | **18** | Tier-A #4 Prior Auth |
| 4 | [ambulance-ems](../../ambulance-ems) | Dispatch optimisation + severity-triage agent | 4 | 5 | 4 | 4 | **17** | Tier-A #2 Multilingual Triage |
| 5 | [provider-portal](../../provider-portal) | Clinician inbox-triage + ambient-scribe agent | 4 | 4 | 4 | 4 | **16** | Tier-A #3 Ambient Scribe |

**Why this ordering.** `insurance-eclaims` leads because it has the cleanest closed action vocabulary (CARC/RARC codes), the strongest audit story (X12 835/837 lifecycle), and the most regulator-friendly HITL story (human-in-loop on denials). Every downstream Tier 1 agent will reuse the reference pattern built here.

### 5.2 Tier 2 — Structural Fit, Integration Work Needed (12–15)

These wait for the reference pattern from Tier 1, then migrate using the extracted playbook.

| Repo | Candidate agent | Notes |
|---|---|---|
| [analytics-bi](../../analytics-bi) | NL→SQL BI agent + MV freshness sweeper | Closed query domain; rich signals |
| [etps](../../etps) | Prescription routing + race-reconciliation agent | Nomination-churn and cancel-vs-dispense races |
| [supply-chain-erp](../../supply-chain-erp) | Auto-reorder + 3PL exception-handler agent | Min/max sweeper + webhook reconciliation |
| [lis](../../lis) | Reflex-testing + critical-value escalation agent | Tight feedback loop; clear escalation thresholds |
| [pacs-ris](../../pacs-ris) | Worklist prioritisation + critical-finding notifier | DICOM + worklist signal rich |
| [appointment-system](../../appointment-system) | Modality negotiation + waiting-list optimisation | Already event-driven; A2A adjacent |
| [kenya-uhc-implementation](../../kenya-uhc-implementation) | County-reconciliation + means-test eligibility | Country-specific, donor-aligned |
| [africa-marketplace](../../africa-marketplace) | Listing creation (photo/voice) + fraud velocity + payout sweep | Non-clinical; useful governance rehearsal |

### 5.3 Tier 3 — Keep as Traditional Services

Listed to prevent them being swept into a future agent-ification drive without a re-score.

- [HMIS](../../HMIS) — surveillance possible but ROI lags Tier 1–2; revisit after Phase 3.
- [scheduling-gateway](../../scheduling-gateway) — already optimal as a stateless router; agentification adds latency.
- [triage-api](../../triage-api) — observability demo harness; not a product surface.
- [elocute](../../elocute) — already agentic via RL curriculum; harvest patterns instead.
- [erp](../../erp) — deterministic GL logic; a rule engine outperforms an agent.

### 5.4 Not Candidates (docs, contracts, UI)

Called out explicitly because they occasionally get confused with services.

- [symphonix-eps-ig](../../symphonix-eps-ig) — FHIR implementation guide; a contract, not a system.
- [csaa](../../csaa) — a gatekeeper **for** agents, not a host.
- [frontend](../../frontend), [design-system](../../design-system) — UI assets.
- [symphonix-health-docs](../../symphonix-health-docs), [symphonix-public](../../symphonix-public), [symphonix-health.github.io](../../symphonix-health.github.io), [healthcare-pain-points-plan](../../healthcare-pain-points-plan), [health-agent-workspace](../../health-agent-workspace) — docs/strategy/research.

---

## 6. The Reference Agent — `insurance-eclaims` Adjudication

The first Tier 1 agent is built end-to-end as the canonical pattern. Every subsequent Tier 1 and Tier 2 migration references this one. The deliverable is both a working agent and a playbook.

### 6.1 Why this first

- **Closed output vocabulary** — CARC/RARC denial codes plus a small set of workflow routes.
- **Strong audit story** — X12 837 → adjudication → 835 remittance is already auditable; agent decisions drop cleanly into that chain.
- **Regulator-friendly HITL** — denials can route to human reviewers without breaking throughput expectations.
- **High-volume, repeatable** — prior auth is explicitly called out as a 10× YoY growth market in the GHARRA Tier-A report.
- **Administrative scope** — CSAA classifies it outside clinical-workflow scope in the baseline configuration, keeping regulatory burden lower during the pattern-extraction phase.

### 6.2 Shape of the agent (to be detailed in a follow-up design note)

- **Input.** Pending-queue claim (FHIR Claim + X12 837 canonical envelope via Bridge SDK).
- **Reasoning.** Prompt Engine assembly over eligibility + coverage + duplicate-therapy + medical-necessity clauses; healthcare renderer; adaptive-thinking mode.
- **Output.** One of {approve, deny-with-CARC, request-information, route-to-human}. Every decision carries a rationale and cited policy reference.
- **Governance.** CSAA classification recorded; GHARRA capability card registered; Nexus A2A card exposed for payer-side integration; SignalBox attestation only for clinically-sensitive sub-cases (e.g., medical-necessity review).
- **HITL.** All denials ≥ threshold-$ and all medical-necessity decisions route to human reviewer before release.
- **Metrics.** Decision-time p50/p95, auto-approval rate, denial-overturn-on-appeal rate, HITL queue depth, per-decision token cost.

### 6.3 Pattern extraction deliverables

Once the reference agent lands, the following are promoted into reusable artefacts:

1. **Agent scaffold template** under [caid-agent](../../caid-agent) — "agent-ify a CRUD service" generator.
2. **GHARRA capability-card schema** formalised and versioned.
3. **HITL checkpoint library** — decision-threshold patterns, reviewer UI primitives, escalation timer defaults.
4. **SignalBox attestation recipe** for administrative vs clinical output differentiation.
5. **Emulator kit recipes** covering happy path + ≥ 3 adversarial cases per decision branch.

---

## 7. Governance

### 7.1 The four gates

Every clinical agent passes four gates before production:

1. **CSAA classification** — scope recorded (out_of_scope / administrative / clinical_workflow / CDS / medical_device). Anything at `CDS` or above triggers hazard-log seeding and CSO sign-off.
2. **GHARRA registration** — signed capability card; 13-point route admission configured.
3. **Emulator-kit coverage** — happy path + ≥ 3 adversarial scenarios per decision branch; `@touchpoint` decorators report coverage to CI.
4. **HITL checkpoint** — at least one named human-review path per autonomous decision class; reviewer SLA recorded.

Administrative agents pass gates 1, 3, and 4; gate 2 is recommended but may be deferred if no cross-org call is made in the launch configuration.

### 7.2 HITL patterns

The reference agent establishes four patterns that subsequent agents reuse:

- **Threshold gate** — decisions above a $-, risk-, or confidence-threshold always route to human.
- **Cohort gate** — decisions for named patient cohorts (paediatric, oncology, etc.) always route to human.
- **Shadow mode** — agent runs behind existing process and produces decisions for audit without acting, until false-positive and false-negative rates meet the promotion bar.
- **Break-glass notify** — any human override of an agent decision fires a GHARRA-signed event to an audit topic; provider-portal subscribes to surface these to the clinician who initiated.

### 7.3 Regulatory posture

Covered by a separate forthcoming note (`regulatory-agents.md`); the pointer here is that Tier 1 administrative agents launch under an administrative-software posture, while clinical Tier 1 agents (pathway deviation, pharmacy prior-auth medical-necessity branches) require the regulatory note landed before their HITL-off promotion.

---

## 8. Roadmap

Each phase has a single reference deliverable plus a short list of supporting artefacts. Phase gates require the prior phase's exit criteria met.

### Phase 1 — Name the Platform (weeks 0–2)

- **Deliverable.** This document, accepted.
- **Supporting.** One-page ecosystem diagram placed in `symphonix-public`. Cross-links added from each primitive repo's README back here.
- **Exit.** Every primitive repo links to this document from its README.

### Phase 2 — Reference Agent (weeks 2–8)

- **Deliverable.** `insurance-eclaims` adjudication agent in production-shadow mode behind a HITL queue.
- **Supporting.** Pattern-extraction deliverables (§6.3). Emulator recipes. SignalBox attestation recipe.
- **Exit.** Auto-approval rate and denial-overturn rate measured over ≥ 10 000 shadow-mode decisions; HITL queue burn-down within target SLA.

### Phase 3 — Governance Hardening (weeks 6–10, overlaps Phase 2)

- **Deliverable.** `governance-agents.md` — HITL patterns, escalation matrices, break-glass recipes formalised.
- **Supporting.** Regulatory posture note (`regulatory-agents.md`). CSAA integration contract versioned.
- **Exit.** Governance doc accepted; regulatory posture note accepted; CSAA gate wired into CAID engineer agent as default pre-commit check for any new agent.

### Phase 4 — Tier 1 Fan-out (weeks 10–24)

- **Deliverable.** Tier 1 ranks 2–5 migrated using the reference pattern.
- **Supporting.** Per-agent cost-per-decision model entries. Cross-agent capability-card catalogue.
- **Exit.** All five Tier 1 agents running in at least shadow mode; two of five promoted past HITL-always into threshold-HITL.

### Phase 5 — Tier 2 Selection (weeks 24–32)

- **Deliverable.** Tier 2 re-scored against post-Phase-4 learnings; top two selected for migration.
- **Supporting.** Cost/ROI model formalised using Phase 4 data; competitive positioning note drafted.
- **Exit.** Two Tier 2 migrations underway; cost/ROI model published; competitive note accepted.

### Phase 6 — Platform Productisation (weeks 32+)

- **Deliverable.** Named platform SKU with published capability card catalogue, governance posture, and onboarding guide for third-party agent authors.
- **Supporting.** Horizon 1000 alignment dossier; regulator engagement pack.

Phases 2 and 3 overlap deliberately — governance hardening must not lag the first agent's production entry.

---

## 9. Gaps the Strategy Closes (and the ones it doesn't)

### Closed by this document

1. No consolidated strategy narrative.
2. No agent transition roadmap.
3. No candidate-scoring framework.
4. No named reference agent.

### To be closed by Phase 2–3 supporting artefacts

5. HITL / escalation / break-glass formalisation (Phase 3 deliverable).
6. Regulatory posture for multi-agent clinical systems (Phase 3 supporting).
7. Cost / ROI model (Phase 5 supporting).
8. Capability-advertisement schema (Phase 6 supporting).

### Deferred — flagged and tracked

- **Competitive positioning** vs Epic, Amazon prior-auth agent, Babylon post-mortem — drafted in Phase 5.
- **Agent observability** (token budgets, drift detection, hallucination guardrails) — design begins after Phase 4 learnings.
- **Third-party agent onboarding** — explicit Phase 6 work; not before a stable internal capability-card schema exists.

---

## 10. Success Metrics

Two categories, tracked from Phase 2 onwards.

**Platform-level.**

- Number of production agents meeting all four gates.
- Mean HITL queue burn-down vs SLA.
- Cost per agent decision (p50, p95).
- Cross-agent GHARRA route-admission latency.
- Emulator-kit coverage per agent (target: ≥ 90% of decision branches).

**Per-agent (reference agent sets the template).**

- Decision-time p50 / p95.
- Auto-resolution rate (decisions that did not require HITL).
- Overturn rate (human override / total autonomous decisions).
- Drift indicator (rolling week-over-week change in decision distribution).
- Per-decision token cost.

---

## 11. Cross-references

- [BulletTrain Integration Doctrine](bullettrain-integration-doctrine.md) - no point-to-point sibling integration; BulletTrain owns cross-system exchange.
- [Prompt Engineering System](prompt-engineering-system.md) — the reasoning-layer contract every agent conforms to.
- [GHARRA Market Intelligence](../../health-agent-workspace/GHARRA_Healthcare_AI_Agent_Market_Intelligence.md) — Tier-A priorities and Horizon 1000 alignment.
- [SE-Agent Literature Review](../../health-agent-workspace/literature_review_SE_agents_2024_2026.md) — academic grounding for the multi-role orchestrator.
- [CAID](../../caid-agent/README.md) — the orchestrator used to scaffold new agents.
- [Nexus A2A](../../nexus-a2a-protocol/README.md) — the coordination protocol reference.
- [GHARRA](../../global-agent-registry/README.md) — the identity / trust / routing layer.
- [SignalBox MCP](../../signalbox-mcp/README.md) — clinical attestation.
- [CSAA](../../csaa/README.md) — clinical safety gate.
- [Symphonix Bridge SDK](../../symphonix-bridge-sdk/README.md) — FHIR-canonical protocol translation.
- [Symphonix Emulator Kit](../../symphonix-emulator-kit/README.md) — external-system simulation.

---

## Status

Draft — awaiting acceptance as the Phase 1 deliverable. On acceptance, update the `symphonix-health-docs/README.md` structure block to list this file alongside `prompt-engineering-system.md` under `strategy/`.
