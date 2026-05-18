# HelixCare Closed-Loop System — Software Requirements Specification (SRS)

**Status:** v0.1 draft — 2026-05-14
**Standard:** ISO/IEC/IEEE 29148:2018 (requirements) | IEEE 29148 §9.5 (use cases)
**Companion to:** [helixcare-business-case.md](helixcare-business-case.md) (commercial brief) | [helixcare-rl-implementation-plan.md](helixcare-rl-implementation-plan.md) (sequencing) | [agent-first.md](agent-first.md) (architecture principles) | [regulatory-agents.md](regulatory-agents.md) (compliance posture)
**Authoring agents in scope:** [REA-Agent-MCP](../../REA-Agent-mcp) (requirements engineering — 18 MCP tools, ISO 29148 / ISO 25010 / INCOSE), [caid-agent](../../caid-agent) (development orchestration — 10 base + 3 meta + 6 conditional engineer roles, 440-pattern advisory, V-model verification)

---

## 1. Scope, Purpose, and Definitions

### 1.1 Purpose

This SRS specifies the **HelixCare Closed-Loop System** — the cross-repo machinery that turns clinician and patient actions on the Symphonix Health platform into measured outcomes, attestable reward signals, and on-policy reinforcement-learning updates that improve clinical care, operational efficiency, and the agent platform itself. It is the formal companion to the eight RL surfaces named in [helixcare-business-case.md §5](helixcare-business-case.md) and sequenced in [helixcare-rl-implementation-plan.md](helixcare-rl-implementation-plan.md).

### 1.2 What "closed loop" means here

A loop is **closed** when all four links exist and are auditable:

1. **Sense.** A state observation captures the relevant clinical, operational, or agent context as a FHIR-canonical record (via Bridge SDK) plus auxiliary signals.
2. **Decide.** A policy (rule-based baseline, contextual bandit, or constrained RL policy) selects an action from a bounded action space.
3. **Act.** The action is dispatched through the BulletTrain Integration Engine (`bullettrain.connectors.*` or the `api_gateway` hub) to the appropriate sibling app, where it has a real clinical, operational, or agent-system effect.
4. **Feedback.** An outcome is measured, attested through SignalBox with a GHARRA-signed provenance chain, written to the reward log, and used to update the policy through an off-policy-evaluation-gated promotion cycle.

A loop that lacks any one link is **open** and is explicitly out of scope for this SRS. An advisor agent that produces a recommendation but does not measure adoption or outcome is open-loop. An adherence reminder that fires but does not log delivery and dose-taken is open-loop. Open-loop work is permitted in the platform but cannot claim to participate in the HelixCare closed-loop system.

### 1.3 Two classes of loop

| Class | Subject | Examples | Reward measurement window |
|---|---|---|---|
| **Clinical / operational loops** | Patient or clinic | scheduling, pathway routing, triage, prior-auth, inbox-triage, adherence, diagnosis support, resourcing | Encounter-level minutes to 90-day windows |
| **Meta loops (agent self-improvement)** | REA-Agent-MCP, CAID-agent, the eight clinical RL policies, prompt-engine clauses | requirements quality, generated-code defect rate, OPE-promotion success rate, prompt clause refinement | Sprint-level days to release-quarter |

The clinical loops deliver the demonstrable value to clinicians and patients. The meta loops compound platform velocity over time. Both are governed by the same OPE-gate, bias-monitoring, and CSAA-sign-off discipline (§7, §8).

### 1.4 Glossary (selected)

- **SPID** — Symphonix Patient Identity, the single internal patient identifier enforced by [symphonix-bridge-sdk patient identity contract](../../symphonix-bridge-sdk/tests/harness/patient_identity).
- **OPE** — Off-policy evaluation. Doubly-robust, importance-weighted, or fitted-Q evaluation that estimates a candidate policy's expected return from data collected under a different policy, without on-line patient exposure.
- **CPCP** — Closed-loop Predetermined Change Control Plan. The HelixCare term for the FDA / MHRA PCCP applied to closed-loop policies; pre-registers the model-update envelope, performance bounds, and HITL regressions.
- **Reward hacking** — Behaviour where a policy increases its proxy reward without improving the underlying outcome. Goodhart's law in clinical-ops form.
- **HITL** — Human-in-the-loop checkpoint; the default disposition for every clinical action surface.
- **DIR** — Disparate Impact Ratio; the four-fifths-rule metric used for bias monitoring per insurance-eclaims UC-EC-BIAS-001.

---

## 2. Research Foundation

The closed-loop design is informed by, and conservative against, the published clinical-RL and closed-loop-medical-device literature. Citations are real and verifiable; the design avoids known failure modes named in these sources.

### 2.1 Closed-loop reinforcement learning in clinical care — published reference points

| Domain | Reference | Lesson incorporated |
|---|---|---|
| Sepsis treatment | Komorowski M, Celi LA, Badawi O, Gordon AC, Faisal AA. "The Artificial Intelligence Clinician learns optimal treatment strategies for sepsis in intensive care." *Nature Medicine* 2018;24(11):1716–1720. | Off-policy evaluation must be doubly-robust; reward shape must encode short-term and long-term outcomes; clinician override is non-negotiable. |
| ICU mechanical ventilation weaning | Prasad N, Cheng L-F, Chivers C, Draugelis M, Engelhardt BE. "A reinforcement learning approach to weaning of mechanical ventilation in intensive care units." *UAI* 2017. | Action-space discretisation matters; safety-constrained policies outperform unconstrained on real-world deployment. |
| HIV antiretroviral therapy | Parbhoo S, Bogojeska J, Zazzi M, Roth V, Doshi-Velez F. "Combining kernel and model based learning for HIV therapy selection." *AMIA Joint Summits on Translational Science* 2017. | Hybrid model-based + kernel approaches handle sparse, high-dimensional state better than pure deep RL in the typical clinical sample regime. |
| Just-in-time adaptive interventions | Klasnja P, Hekler EB, Shiffman S, Boruvka A, Almirall D, Tewari A, Murphy SA. "Microrandomized trials: an experimental design for developing just-in-time adaptive interventions." *Health Psychology* 2015;34(S):1220–1228. | Microrandomised trials provide the cleanest path to causal evidence for adherence and engagement bandits; design the data plane to support MRT from day one. |
| mHealth contextual bandits | Tewari A, Murphy SA. "From ads to interventions: contextual bandits in mobile health." In *Mobile Health* (Springer), 2017. | LinUCB / Thompson sampling with engineered features is sufficient for most adherence and engagement loops; deep policies overfit at typical sample sizes. |
| Healthcare RL safety | Gottesman O, Johansson F, Komorowski M, et al. "Guidelines for reinforcement learning in healthcare." *Nature Medicine* 2019;25:16–18. | Eleven discipline points: confounding, off-policy evaluation, action heterogeneity, exploration limits — all encoded as constraints in §6 and §7. |
| Healthcare RL survey | Yu C, Liu J, Nemati S, Yin G. "Reinforcement learning in healthcare: a survey." *ACM Computing Surveys* 2021;55(1). | Taxonomy of clinical-RL applications mapped onto our eight surfaces; no surface launches with a method weaker than peer-reviewed state-of-the-art for that class. |
| Generalisability | Futoma J, Simons M, Panch T, Doshi-Velez F, Celi LA. "The myth of generalisability in clinical machine learning." *Lancet Digital Health* 2020;2(9):e489–e492. | Per-tenant fine-tuning or shared-base-with-tenant-features is the default; we never assume a policy trained on one tenant generalises blindly. |
| Reproducibility | Beam AL, Manrai AK, Ghassemi M. "Challenges to the reproducibility of machine learning models in health care." *JAMA* 2020;323(4):305–306. | Every policy version is reproducible from the policy-registry capability card and the reward log; SignalBox attestation is non-optional. |
| Scheduling bias | Samorani M, Harris S, Blount LG, Lu H, Santoro MA. "Overbooked and overlooked: machine learning and racial bias in medical appointment scheduling." *Manufacturing & Service Operations Management* 2022;24(6):2825–2842. | Scheduling RL must monitor and constrain disparate impact across protected groups; we extend the eclaims four-fifths-rule guard to scheduling. |
| ED RL | Lee J, Yang S, Holland-Hall C, et al. "Prediction of length of stay in the emergency department." *Health Informatics Journal* 2021. | Triage RL must hard-constrain on Manchester / ESI category floors. |
| Physician inbox burden | Tai-Seale M, Olson CW, Li J, et al. "Electronic health record logs indicate that physicians split time evenly between seeing patients and desktop medicine." *Health Affairs* 2017;36(4):655–662. | Inbox-triage bandits target the largest single source of physician administrative burden as measured in the field; the reward must include clinician time saved as a primary signal. |

### 2.2 FDA-cleared and CE-marked closed-loop medical devices — pattern donors

Three classes of cleared closed-loop devices inform the safety-case template for HelixCare clinical loops, even though HelixCare does not initially launch a Class II / Class IIa medical device:

- **Closed-loop insulin (artificial pancreas).** Medtronic MiniMed 780G with SmartGuard (FDA cleared 2023); Tandem t:slim X2 with Control-IQ (FDA cleared 2019); Insulet Omnipod 5. Lessons: bounded action space; failure-mode classification; predetermined-change-control framework; explicit hypoglycaemia-avoidance constraint; user-driven mode switching.
- **Closed-loop anaesthesia.** Bispectral-index-driven propofol target-controlled infusion (McSleepy, Hemmerling et al.); ongoing closed-loop sedation trials. Lessons: continuous physiological feedback with PID + RL hybrid; clinician at the bedside is the safety layer.
- **Algorithmic cardiac monitoring.** Boston Scientific HeartLogic (FDA cleared 2017); Medtronic TriageHF. Lessons: alert thresholds tuned per-patient; outcome-anchored validation; explicit reporting on positive and negative predictive value.

The HelixCare position is: a closed-loop **policy** (software-as-medical-device, SaMD) launches as Clinical Decision Support under §520(o)(1)(E) CDS exclusion (HITL always); the closed-loop **safety case** is borrowed structurally from the device class so that progression to autonomous SaMD has a credible regulatory glide path.

### 2.3 Closed-loop regulatory frameworks

- FDA Predetermined Change Control Plan guidance for AI/ML SaMD (2024 final guidance) — informs CPCP structure.
- EU AI Act 2024/1689 high-risk system requirements, Annex IV technical documentation — informs the per-policy model card.
- MHRA AI Airlock (active 2025+) — accepts pre-market submissions for closed-loop clinical decision-support systems.
- IMDRF SaMD framework, IEC 62304 software lifecycle, ISO 14971 risk management — adopted unchanged.
- DCB0129 (clinical safety case) and DCB0160 (deployment) — enforced through [csaa](../../csaa) gating.

---

## 3. Inventory of Contributing Repos (Symphonix Health platform — forks excluded)

The closed-loop system spans the following repos. **Forks of upstream OSS (claw-code-parity, openclaw, Liquid4Allcookbook) and non-platform scratch directories (_*, tools, tool-library, frontend, services, infra, prototypes, dashboards, alerting) are explicitly out of scope.**

### 3.1 Platform layer (agent stack)

| Repo | Role in closed loop |
|---|---|
| [global-agent-registry](../../global-agent-registry) | GHARRA registry. Issues capability cards for every policy version; provides the signed identity for sense → decide → act dispatch. |
| [nexus-a2a-protocol](../../nexus-a2a-protocol) | A2A coordination protocol. Carries cross-agent tasks during the decide and act phases. |
| [caid-agent](../../caid-agent) | Multi-role development orchestrator. Builds and refactors the policy / connector / route code that implements each loop; itself subject to meta-RL (§9). |
| [REA-Agent-mcp](../../REA-Agent-mcp) | Pattern-driven requirements-engineering agent (18 MCP tools, ISO 29148 / ISO 25010 / INCOSE). Generates, QA's, traces, and reverse-engineers the requirements that govern every loop; itself subject to meta-RL (§9). |
| [prompt-engine](../../prompt-engine) | 18-clause reasoning DSL with healthcare renderer. Hosts the reasoning clauses each clinical agent uses; clauses are tuned via meta-RL on clinician acceptance signal. |
| [symphonix-bridge-sdk](../../symphonix-bridge-sdk) | FHIR-canonical pivot. Carries every sense observation into a canonical state vector; enforces the SPID-only-internal patient-identity contract. |
| [signalbox-mcp](../../signalbox-mcp) | Browser-attested evidence + 20 MCP tools. Captures and signs every reward event with GHARRA provenance; replay, visual QA, capture verification. |
| [BulletTrain](../../BulletTrain) | Integration hub. Hosts the new `bullettrain.rl` module (feature store, reward log, OPE gate, policy registry, reward-hacking guard, HITL router). Every act dispatch routes through `bullettrain.connectors.*` per Integration Constitution. |
| [symphonix-emulator-kit](../../symphonix-emulator-kit) | Emulator substrate. Replays the offline RL training data through scenario fixtures; enables CPCP regression packs. |
| [csaa](../../csaa) | Clinical Safety Algorithm Assurance. Owns the OPE-promotion gate for any clinical loop; DCB0129/0160 scope classification; CSO sign-off. |
| [health-agent-workspace](../../health-agent-workspace) | GHARRA Tier-A inventory + Horizon 1000 alignment + research grounding for the eight RL surfaces. |

### 3.2 Sibling clinical action surfaces

Each sibling owns one or more of the action spaces a closed-loop policy can dispatch into. Every dispatch goes through `bullettrain.connectors.<sibling>` per Integration Constitution; no closed-loop code ever calls a sibling directly.

| Repo | Closed-loop action surface |
|---|---|
| [provider-portal](../../provider-portal) | Encounter manager + inbox + e-prescribing + dual-chain audit. Inbox-triage RL acts here; clinician HITL approvals happen here. |
| [citizen-portal](../../citizen-portal) | Patient timeline + consent + SAR. Adherence-RL nudges and patient-side decisions land here. |
| [picis-system](../../picis-system) | Acute / ICU / theatre. Resourcing RL and pathway RL act here for inpatient cohorts. |
| [gp-system](../../gp-system) | General-practice encounter. Pathway RL and diagnosis-support RL act here. |
| [eps](../../eps), [etps](../../etps) | Electronic prescribing and transfer. Adherence RL + prior-auth RL act here. |
| [pharmacy-system](../../pharmacy-system) | Dispensing and inventory. Adherence RL acts here for refill timing. |
| [lis](../../lis) | Laboratory order + result. Diagnosis-support RL acts on next-test recommendations here. |
| [pacs-ris](../../pacs-ris) | Imaging order + report. Diagnosis-support RL acts here for next-imaging recommendations. |
| [ambulance-ems](../../ambulance-ems) | EMS dispatch + Manchester triage. Triage RL acts on dispatch routing. |
| [triage-api](../../triage-api) | Triage classification. Triage RL acts here for ED and virtual cohorts. |
| [insurance-eclaims](../../insurance-eclaims) | X12 EDI claims and prior auth. Prior-auth RL acts here. Bias-audit and four-fifths-rule infra extends to all clinical loops. |
| [supply-chain-erp](../../supply-chain-erp) | Inventory, cold chain, UDI. Resourcing RL acts on stock allocation. |
| [scheduling-gateway](../../scheduling-gateway), [appointment-system](../../appointment-system) | Scheduling fabric. Scheduling RL acts here. |
| [clinical-pathways](../../clinical-pathways) | Pathway authoring + dispatch. Pathway RL acts on next-node recommendations within evidence-based guideline DAGs. |
| [maternity-system](../../maternity-system) | Maternity care. Pathway RL with maternity guideline DAG. |
| [screening-recall](../../screening-recall) | Screening invites + recall. Adherence RL acts on invitation cadence. |
| [cancer-pathway-tracker](../../cancer-pathway-tracker) | Oncology pathway. Pathway RL with NICE / NCCN guideline DAG. |
| [genomics-interpretation](../../genomics-interpretation) | Variant annotation + report. Diagnosis-support RL for next-variant test recommendations. |
| [mortuary-and-me](../../mortuary-and-me) | Mortuary and bereavement. Out of clinical-loop scope; CRUD only. |
| [mha-administration](../../mha-administration) | Mental Health Act administration. Pathway RL with MHA guideline DAG; high-risk surface. |
| [community-nursing](../../community-nursing) | Community / district nursing. Pathway RL + adherence RL for housebound cohorts. |
| [blood-transfusion](../../blood-transfusion) | Transfusion workflow. Out of initial clinical-loop scope; safety-critical hard constraints only. |
| [epaccs](../../epaccs) | Electronic palliative care coordination. Pathway RL with palliative guideline DAG. |
| [symphonix-eps-ig](../../symphonix-eps-ig) | FHIR Implementation Guide for EPS. Constrains the canonical-state vector for prescribing-loop sense observations. |
| [HMIS](../../HMIS) | Hospital management. Resourcing RL acts here for hospital-tier tenants. |
| [analytics-bi](../../analytics-bi) | Population-health analytics. Closed-loop reward computation cross-tenant aggregation surface. |
| [erp](../../erp) | Enterprise resource planning. Out of clinical scope; financial loops only. |
| [africa-marketplace](../../africa-marketplace) | Ghana-first marketplace. Out of HelixCare clinical scope; payment-rail pattern donor. |
| [kenya-uhc-implementation](../../kenya-uhc-implementation) | Kenya UHC implementation. Donor-funded deployment substrate for Africa Bronze tier. |
| [healthcare-pain-points-plan](../../healthcare-pain-points-plan) | Cross-repo audit + pain-point catalogue. Source for FR derivation. |

### 3.3 Brand and documentation

| Repo | Role |
|---|---|
| [symphonix-health-docs](../../symphonix-health-docs) | This SRS, the business case, the RL implementation plan, and the rest of the strategy canon live here. |
| [symphonix-health.github.io](../../symphonix-health.github.io) | Public marketing site. |
| [symphonix-public](../../symphonix-public) | Public-facing release assets. |
| [design-system](../../design-system) | Symphonix design system. Closed-loop control surfaces (HITL approval queue, reward-log explorer, policy registry browser) consume this system per [feedback_design_system_and_caid_agent_for_new_components](../../../.claude/projects/c--Users-hgeec-github/memory/feedback_design_system_and_caid_agent_for_new_components.md). |

### 3.4 Explicitly out of scope

- **claw-code-parity, openclaw** — forks confirmed via `gh repo view --json isFork` (`GmailTedam` org, `fork=true`).
- **Liquid4Allcookbook** — community cookbook (`Liquid4All/cookbook.git`), not Symphonix-Health.
- **\_\* output directories** — scratch screenshot / capture / visual-baseline directories produced by browser-test runs; not source.
- **tools, services, alerting;R** — empty / typo-artefact directories (verified by directory inspection: `tools` empty, `services` empty, `alerting;R` is a PowerShell-typo empty dir).
- **frontend** — single `buyer-web` subdir, likely overflow from `africa-marketplace`; not a HelixCare clinical surface.
- **tool-library** — `symphonix-health/tool-library.git`, fork=false, but its CLAUDE.md states explicitly: "non-healthcare, non-payments — a deliberately small civic-domain app used to stress-test the CAID pipeline." Symphonix-owned but out of HelixCare clinical scope.
- **prototypes** — `loading-globe` only; visual prototypes, not platform code.

**Operational underlay (real config, out of clinical FR / UC scope but in scope of operational SLA):**
- `infra/` — `prometheus.yml`, `alertmanager.yml`. Observability platform for the SLA captured in NFR-CL-OBS-001 / NFR-CL-LAT-001.
- `dashboards/` — `symphonix-service-template.json`. Grafana / observability dashboards consumed by the SLA.
- `alerting/` — `symphonix-base-rules.yml`. Alertmanager rules for closed-loop platform health and policy-freeze events (FR-CL-OPE-002, FR-CL-RHG-001).

These directories support the closed-loop platform but are not clinical action surfaces; they are referenced here so reviewers do not mistake them for scratch.
- **elocute** — Tedam Technologies sibling product (accent acquisition); pattern donor for RL infra (per [agent-first.md §3](agent-first.md) non-goal #2) but not a HelixCare clinical action surface.
- **BulletTrain-visual** — asset / output directory, not a git repository (no `.git`).

**Worktrees (in-scope of canonical repo, not separate exclusions):** `BulletTrain-gap-2-signatures` is a legitimate `git worktree` of canonical `BulletTrain` on branch `gap/signatures` (verified via `git worktree list`). For SRS-versioning purposes it is part of the canonical BulletTrain inventory in §3.1; whether its in-progress changes affect closed-loop scope is determined when its branch merges to `main`. The platform's worktree topology is the correct shape per workspace policy: one working tree per branch under the canonical repo.

---

## 4. System Topology

```
                                         HelixCare Closed Loop
                                         ─────────────────────

   ┌──────────────────┐   sense    ┌──────────────────┐  decide   ┌──────────────────┐
   │  Patient signal  │───────────▶│  Bridge SDK +    │──────────▶│  Policy via      │
   │  (FHIR via       │            │  Feature Store   │           │  bullettrain.rl  │
   │   sibling app)   │            │  (canonicalise)  │           │  policy registry │
   └──────────────────┘            └──────────────────┘           └──────────────────┘
            ▲                                                              │
            │                                                              │ act
            │ feedback                                                     ▼
            │                       ┌──────────────────┐           ┌──────────────────┐
            └───────────────────────│  SignalBox       │◀──────────│  bullettrain.    │
                                    │  reward log      │  attest   │  connectors.X    │
                                    │  GHARRA-signed   │           │  (Integration    │
                                    └──────────────────┘           │   Engine hub)    │
                                          │                        └──────────────────┘
                                          │ OPE                              │
                                          ▼                                  │ dispatch
                                    ┌──────────────────┐           ┌──────────────────┐
                                    │  CSAA OPE gate   │           │  Sibling app     │
                                    │  + reward-hack   │           │  action surface  │
                                    │  guard + DIR     │           │  (provider-      │
                                    │  monitor         │           │   portal, eps,   │
                                    │                  │           │   pharmacy, …)   │
                                    └──────────────────┘           └──────────────────┘
                                          │                                  │
                                          │ promote                          │ effect
                                          ▼                                  ▼
                                    ┌─────────────────────────────────────────┐
                                    │  Policy registry (GHARRA capability)    │
                                    │  + Clinician HITL queue (provider-      │
                                    │   portal) + Outcome capture (sibling    │
                                    │   app event stream → BulletTrain        │
                                    │   FHIR EventBus)                        │
                                    └─────────────────────────────────────────┘
                                                       │
                                                       │ outcome event
                                                       ▼
                                              (sense, next cycle)


                          Meta loop (agent self-improvement) — runs over the same plane
                          ────────────────────────────────────────────────────────────

   ┌──────────────────┐   sense    ┌──────────────────┐  decide   ┌──────────────────┐
   │ Requirements    │───────────▶│  REA-Agent-MCP   │──────────▶│  caid-agent      │
   │ usage signal    │            │  pattern         │           │  build + verify  │
   │ (FR adoption,   │            │  derivation      │           │  generated code  │
   │  defect rate,   │            └──────────────────┘           └──────────────────┘
   │  ISO coverage)  │                                                   │
   └──────────────────┘                                                   │ act
            ▲                                                             ▼
            │                                                    ┌──────────────────┐
            │ feedback                                           │  Closed-loop     │
            │  (defect log, OPE                                  │  artefact lands  │
            │  pass rate, clinician                              │  in target repo  │
            │  acceptance signal)                                └──────────────────┘
            │                                                             │
            │                       ┌──────────────────┐                  │
            └───────────────────────│  Reward log:     │◀─────────────────┘
                                    │  CAID-engineer   │   verify (V-model)
                                    │  + REA-derive    │
                                    │  outcomes        │
                                    └──────────────────┘
```

---

## 5. Functional Requirements (FR)

Each requirement follows the Elocute ISO/IEC/IEEE 29148:2018 table format. Trace links use REQ IDs; NFR aspects refer to §6.

### 5.1 Sense plane

#### FR-CL-SNS-001: FHIR-canonical state vector

| Attribute | Value |
|---|---|
| REQ ID | FR-CL-SNS-001 |
| Title | FHIR-canonical state vector for every loop |
| Statement | The system shall compute, for every closed-loop policy invocation, a FHIR-canonical state vector via [symphonix-bridge-sdk](../../symphonix-bridge-sdk), keyed by SPID and never by an external patient identifier. |
| Category | functional |
| Priority | CRITICAL |
| Source | Closed-loop topology §4; symphonix-bridge-sdk patient-identity contract |
| Owner | BulletTrain RL platform |
| Component | `bullettrain.rl.feature_store` |
| Verification | Test case + integration test against Bridge SDK |
| Dependencies | (none) |
| Regulatory | EU AI Act Annex IV §3 (data governance); GDPR Art. 5(1)(c) data minimisation |
| Risk | Stale or mis-canonicalised state produces wrong action; mitigated by Bridge SDK contract test |
| Status | draft |
| Version | 1.0 |
| Trace Links | FR-CL-DEC-001, FR-CL-FBK-001, NFR-CL-PRV-001 |
| NFR Aspects | privacy, reproducibility, latency |

**Rationale.** The patient-identity invariant ([feedback_review_codebase_first_no_duplication](../../../.claude/projects/c--Users-hgeec-github/memory/feedback_review_codebase_first_no_duplication.md)) requires the SPID as the only internal identifier. Every closed loop reads through the same canonical state surface so policy decisions are reproducible and auditable across siblings.

**Acceptance Criteria.**
1. **[FRCLSNS001-AC01]** [Positive] [Automated] GIVEN a sibling-app event referencing an external identifier, WHEN `bullettrain.rl.feature_store.observe(event)` is called, THEN the returned state vector uses SPID and external identifiers appear only as aliases.
2. **[FRCLSNS001-AC02]** [Negative] [Automated] GIVEN an event with no resolvable SPID, WHEN observation is attempted, THEN the call returns a typed error and the policy invocation is short-circuited to the rule-based baseline.

#### FR-CL-SNS-002: Deterministic snapshot for replay

| Attribute | Value |
|---|---|
| REQ ID | FR-CL-SNS-002 |
| Title | Deterministic state snapshot for offline replay |
| Statement | The system shall persist each state vector as an append-only, content-addressable snapshot so any past policy decision can be reproduced bit-for-bit. |
| Category | functional |
| Priority | HIGH |
| Source | Reproducibility (Beam 2020) |
| Owner | BulletTrain RL platform |
| Component | `bullettrain.rl.feature_store` |
| Verification | Test case |
| Dependencies | FR-CL-SNS-001 |
| Regulatory | EU AI Act Annex IV §4; UK MHRA AI Airlock evidence pack |
| Risk | Without bit-reproducibility, regulator cannot reconstruct decisions; mitigated by SHA-256 content addressing |
| Status | draft |
| Version | 1.0 |
| Trace Links | FR-CL-FBK-002, NFR-CL-REP-001 |
| NFR Aspects | reproducibility, auditability |

**Acceptance Criteria.**
1. **[FRCLSNS002-AC01]** [Positive] [Automated] GIVEN a recorded snapshot SHA, WHEN `feature_store.replay(sha)` is called, THEN the returned state vector hashes to the same SHA.

### 5.2 Decide plane

#### FR-CL-DEC-001: Policy invocation through registry

| Attribute | Value |
|---|---|
| REQ ID | FR-CL-DEC-001 |
| Title | Every action is selected by a registered policy |
| Statement | The system shall require every closed-loop action to be selected by a policy registered in the `bullettrain.rl.policy_registry` with a GHARRA capability card; ad-hoc policy code is rejected at write time. |
| Category | functional |
| Priority | CRITICAL |
| Source | BulletTrain Integration Constitution; GHARRA capability cards |
| Owner | BulletTrain RL platform + GHARRA |
| Component | `bullettrain.rl.policy_registry` |
| Verification | Test case + semgrep rule + write-time hook (`~/.claude/hooks/bullettrain_integration_guard.py`) |
| Dependencies | FR-CL-SNS-001 |
| Regulatory | FDA PCCP; EU AI Act Annex IV §2 |
| Risk | Unregistered policy escapes OPE gate and bias audit; mitigated by registry-mandatory hook |
| Status | draft |
| Version | 1.0 |
| Trace Links | FR-CL-DEC-002, FR-CL-ACT-001, NFR-CL-GOV-001 |
| NFR Aspects | governance, auditability |

**Acceptance Criteria.**
1. **[FRCLDEC001-AC01]** [Positive] [Automated] GIVEN a state vector and a registered policy ID, WHEN `policy_registry.select_action(policy_id, state)` is called, THEN an action is returned and the (policy_id, state_sha, action) triple is logged.
2. **[FRCLDEC001-AC02]** [Negative] [Automated] GIVEN an unregistered policy ID, WHEN selection is attempted, THEN the call raises `UnregisteredPolicyError` and falls back to the named baseline policy.

#### FR-CL-DEC-002: Constrained action space

| Attribute | Value |
|---|---|
| REQ ID | FR-CL-DEC-002 |
| Title | Action space constrained per surface |
| Statement | The system shall constrain each policy's action space to the surface-specific allowlist defined in `helixcare-rl-implementation-plan.md` (e.g. Manchester triage floors, NICE pathway DAG, never-auto-deny for prior auth). |
| Category | functional |
| Priority | CRITICAL |
| Source | Gottesman 2019 guideline #6 |
| Owner | CSAA |
| Component | `bullettrain.rl.policy_registry` constraint enforcer |
| Verification | Test case per surface; CSAA pre-deployment sign-off |
| Dependencies | FR-CL-DEC-001 |
| Regulatory | DCB0129 hazard log; EU AI Act Annex IV §3 |
| Risk | Out-of-envelope action; mitigated by allowlist + CSAA review |
| Status | draft |
| Version | 1.0 |
| Trace Links | FR-CL-ACT-002 |
| NFR Aspects | safety, governance |

**Acceptance Criteria.**
1. **[FRCLDEC002-AC01]** [Negative] [Automated] GIVEN a policy that proposes an out-of-allowlist action, WHEN selection is attempted, THEN the proposal is rejected and the baseline action is substituted.

### 5.3 Act plane

#### FR-CL-ACT-001: Dispatch through BulletTrain Integration Engine

| Attribute | Value |
|---|---|
| REQ ID | FR-CL-ACT-001 |
| Title | All closed-loop actions dispatch through `bullettrain.connectors.*` |
| Statement | The system shall dispatch every closed-loop action through `bullettrain.connectors.<sibling>` or the `api_gateway` hub; direct sibling-to-sibling calls from closed-loop code are prohibited and enforced at write time. |
| Category | functional |
| Priority | CRITICAL |
| Source | [BulletTrain Integration Constitution](../../caid-agent/docs/architecture/bullettrain-integration-constitution.md); ADR-004 |
| Owner | BulletTrain |
| Component | `bullettrain.connectors.*` |
| Verification | Semgrep rule + write-time hook; integration test |
| Dependencies | FR-CL-DEC-001 |
| Regulatory | UK NHS DSPT (data flow control); GDPR Art. 32 |
| Risk | Direct sibling calls bypass audit and rate limit; mitigated by hook + PR template |
| Status | draft |
| Version | 1.0 |
| Trace Links | FR-CL-ACT-002, FR-CL-FBK-001, NFR-CL-GOV-002 |
| NFR Aspects | governance, audit, reliability |

**Acceptance Criteria.**
1. **[FRCLACT001-AC01]** [Positive] [Automated] GIVEN a selected action and a sibling target, WHEN dispatch is attempted, THEN the call routes through `bullettrain.connectors.<sibling>` and the dispatch is recorded with policy_id and action_sha.
2. **[FRCLACT001-AC02]** [Negative] [Automated] GIVEN closed-loop code that imports a sibling client directly, WHEN it is written or staged, THEN the write-time hook rejects it.

#### FR-CL-ACT-002: HITL queue for sub-confidence actions

| Attribute | Value |
|---|---|
| REQ ID | FR-CL-ACT-002 |
| Title | Sub-confidence actions route to HITL queue |
| Statement | The system shall route any selected action whose policy confidence is below the per-surface HITL threshold to the [provider-portal](../../provider-portal) HITL queue for clinician approval before dispatch; HITL approval is the default disposition for all clinical loops until autonomy is earned per CPCP. |
| Category | functional |
| Priority | CRITICAL |
| Source | [agent-first.md §"Human-in-the-loop is the default"](agent-first.md) |
| Owner | provider-portal + BulletTrain RL |
| Component | provider-portal HITL queue; `bullettrain.rl.hitl_router` |
| Verification | E2E test; clinician-acceptance scenarios |
| Dependencies | FR-CL-DEC-001 |
| Regulatory | FDA CDS exclusion §520(o)(1)(E) condition 4 |
| Risk | Autopilot escape; mitigated by default-on routing |
| Status | draft |
| Version | 1.0 |
| Trace Links | UC-HC-CL-005 |
| NFR Aspects | safety, governance |

**Acceptance Criteria.**
1. **[FRCLACT002-AC01]** [Positive] [Automated] GIVEN an action with confidence below the threshold, WHEN dispatch is attempted, THEN the action is enqueued in provider-portal HITL queue and a clinician notification is fired.
2. **[FRCLACT002-AC02]** [Positive] [Manual] GIVEN a clinician approves an HITL action, WHEN the approval is recorded, THEN dispatch proceeds and the approval is captured in the reward log.

### 5.4 Feedback plane

#### FR-CL-FBK-001: Reward log via SignalBox attestation

| Attribute | Value |
|---|---|
| REQ ID | FR-CL-FBK-001 |
| Title | Every (state, action, reward) tuple is SignalBox-attested |
| Statement | The system shall record every (state_sha, policy_id, action, reward, outcome_window) tuple via [signalbox-mcp](../../signalbox-mcp), Ed25519-signed under the GHARRA-issued policy identity, in an append-only reward log. |
| Category | functional |
| Priority | CRITICAL |
| Source | Gottesman 2019 guideline #2; Beam 2020 reproducibility |
| Owner | SignalBox + BulletTrain RL |
| Component | `bullettrain.rl.reward_log` |
| Verification | Test case + integration test with SignalBox capture verification |
| Dependencies | FR-CL-ACT-001 |
| Regulatory | EU AI Act Annex IV §4 (record-keeping); FDA PCCP §B |
| Risk | Tampered reward stream; mitigated by hash-chained signed log |
| Status | draft |
| Version | 1.0 |
| Trace Links | FR-CL-FBK-002, FR-CL-OPE-001, NFR-CL-AUD-001 |
| NFR Aspects | auditability, tamper-evidence |

**Acceptance Criteria.**
1. **[FRCLFBK001-AC01]** [Positive] [Automated] GIVEN a dispatched action and a measured outcome, WHEN reward is computed, THEN the tuple is written to the log with a valid signature chained to the previous entry.
2. **[FRCLFBK001-AC02]** [Negative] [Automated] GIVEN a tuple with broken hash chain, WHEN log verification runs, THEN the verifier returns `ChainBroken` and the affected policy is frozen pending CSAA review.

#### FR-CL-FBK-002: PHI redaction at write

| Attribute | Value |
|---|---|
| REQ ID | FR-CL-FBK-002 |
| Title | Reward log contains SPID only; PHI redacted at write |
| Statement | The system shall redact PHI fields from reward-log entries at write time; only SPID, policy ID, action ID, and reward scalar are persisted, with external aliases stripped per the patient-identity contract. |
| Category | functional |
| Priority | CRITICAL |
| Source | symphonix-bridge-sdk patient-identity contract; HIPAA §164.312; GDPR Art. 5(1)(c) |
| Owner | SignalBox |
| Component | `bullettrain.rl.reward_log` redactor; existing SignalBox pipeline |
| Verification | Test case; redaction unit tests; bridge SDK contract test |
| Dependencies | FR-CL-FBK-001 |
| Regulatory | HIPAA Privacy Rule; GDPR Art. 9 |
| Risk | PHI leak via reward stream; mitigated by deny-by-default field set |
| Status | draft |
| Version | 1.0 |
| Trace Links | NFR-CL-PRV-001 |
| NFR Aspects | privacy |

**Acceptance Criteria.**
1. **[FRCLFBK002-AC01]** [Negative] [Automated] GIVEN a candidate reward tuple containing `nhs_number`, `dob`, `name`, `email`, or `address`, WHEN it is presented for write, THEN the redactor strips those fields before persistence.

### 5.5 OPE gate

#### FR-CL-OPE-001: Doubly-robust off-policy evaluation gate

| Attribute | Value |
|---|---|
| REQ ID | FR-CL-OPE-001 |
| Title | No policy promotes without doubly-robust OPE clearing threshold |
| Statement | The system shall require every candidate policy to pass a doubly-robust off-policy evaluation against the production reward log, with the 95% confidence-interval lower bound meeting or exceeding the per-surface pre-registered threshold, before being marked promotable in the policy registry. |
| Category | functional |
| Priority | CRITICAL |
| Source | Komorowski 2018; Gottesman 2019 guideline #4 |
| Owner | CSAA |
| Component | `bullettrain.rl.ope_gate` |
| Verification | Test case using `econml` / `dowhy` doubly-robust estimators; CSAA sign-off |
| Dependencies | FR-CL-FBK-001 |
| Regulatory | FDA PCCP §C; EU AI Act Annex IV §6 |
| Risk | Promoting a policy worse than baseline; mitigated by CI lower-bound gate |
| Status | draft |
| Version | 1.0 |
| Trace Links | FR-CL-OPE-002, UC-HC-CL-006 |
| NFR Aspects | safety, scientific-validity |

**Acceptance Criteria.**
1. **[FRCLOPE001-AC01]** [Positive] [Automated] GIVEN a candidate policy with an OPE lower-bound clearing threshold, WHEN promotion is requested, THEN the registry marks the policy promotable and a CSAA review ticket is opened.
2. **[FRCLOPE001-AC02]** [Negative] [Automated] GIVEN a candidate policy with OPE lower-bound below threshold, WHEN promotion is requested, THEN promotion is denied and the result is logged.

#### FR-CL-OPE-002: Four-fifths-rule disparate-impact monitor

| Attribute | Value |
|---|---|
| REQ ID | FR-CL-OPE-002 |
| Title | DIR ≥ 0.80 across protected groups |
| Statement | The system shall compute per-policy disparate impact ratios across age, sex, ethnicity, plan type, and ZIP-income (extending the [insurance-eclaims UC-EC-BIAS-001 monitor](../../insurance-eclaims/docs/USE_CASES.md)) to every closed-loop policy, and shall freeze any policy whose rolling 90-day DIR falls below 0.80 pending CSAA review. |
| Category | functional |
| Priority | CRITICAL |
| Source | EEOC four-fifths rule; Samorani 2022 (scheduling bias) |
| Owner | CSAA + insurance-eclaims bias-audit team |
| Component | `bullettrain.rl.bias_monitor` (extends eclaims monitor) |
| Verification | Test case; rolling-window simulation |
| Dependencies | FR-CL-FBK-001 |
| Regulatory | EU AI Act Art. 10; UK Equality Act 2010; US ADA |
| Risk | Disparate impact on protected group; mitigated by rolling monitor + freeze |
| Status | draft |
| Version | 1.0 |
| Trace Links | UC-HC-CL-007 |
| NFR Aspects | fairness, governance |

**Acceptance Criteria.**
1. **[FRCLOPE002-AC01]** [Negative] [Automated] GIVEN a rolling-90-day window with DIR < 0.80 on any protected group, WHEN the monitor runs, THEN the affected policy is automatically frozen and a CSAA review ticket is opened.

### 5.6 Reward-hacking guard

#### FR-CL-RHG-001: Adversarial reward-hacking pack pre-promotion

| Attribute | Value |
|---|---|
| REQ ID | FR-CL-RHG-001 |
| Title | Adversarial reward-hacking pack runs before every promotion |
| Statement | The system shall execute the per-surface adversarial reward-hacking pack (documented Goodhart vectors) against any candidate policy before promotion; divergence between proxy reward and ground-truth outcome above the per-surface threshold blocks promotion. |
| Category | functional |
| Priority | HIGH |
| Source | Gottesman 2019 guideline #9; AI safety reward-hacking literature |
| Owner | CSAA |
| Component | `bullettrain.rl.reward_hacking_guard` |
| Verification | Test case per surface |
| Dependencies | FR-CL-OPE-001 |
| Regulatory | EU AI Act Annex IV §3.6 |
| Risk | Policy gaming proxy reward; mitigated by adversarial pack + post-promotion shadow |
| Status | draft |
| Version | 1.0 |
| Trace Links | UC-HC-CL-008 |
| NFR Aspects | safety, scientific-validity |

**Acceptance Criteria.**
1. **[FRCLRHG001-AC01]** [Negative] [Automated] GIVEN a candidate policy that exhibits proxy/ground-truth divergence above threshold on any pack scenario, WHEN promotion is requested, THEN promotion is blocked.

### 5.7 Rollback

#### FR-CL-RBK-001: Sub-60-second policy rollback

| Attribute | Value |
|---|---|
| REQ ID | FR-CL-RBK-001 |
| Title | Policy rollback completes within 60 seconds |
| Statement | The system shall support rollback of any active policy to its previous registered version within 60 seconds of operator command; the reward log shall capture the rollback event with operator identity and reason. |
| Category | functional |
| Priority | HIGH |
| Source | helixcare-rl-implementation-plan §2 |
| Owner | BulletTrain RL platform |
| Component | `bullettrain.rl.policy_registry` |
| Verification | Test case + drill |
| Dependencies | FR-CL-DEC-001 |
| Regulatory | DCB0160 deployment safety |
| Risk | Stuck rollback; mitigated by feature-flag flip + drill |
| Status | draft |
| Version | 1.0 |
| Trace Links | UC-HC-CL-009 |
| NFR Aspects | reliability, recoverability |

**Acceptance Criteria.**
1. **[FRCLRBK001-AC01]** [Positive] [Automated] GIVEN an operator-initiated rollback, WHEN the rollback completes, THEN end-to-end wall time is below 60 seconds and the next dispatch uses the previous policy version.

### 5.8 Multi-tenancy

#### FR-CL-MT-001: Per-tenant policy scope

| Attribute | Value |
|---|---|
| REQ ID | FR-CL-MT-001 |
| Title | Policy activation is per-tenant scoped |
| Statement | The system shall scope policy activation to one or more tenants in the policy registry; a policy may run as the shared base for all tenants, as a tenant-fine-tuned variant, or as a tenant-specific dedicated policy. |
| Category | functional |
| Priority | HIGH |
| Source | helixcare-business-case §6.1; Futoma 2020 generalisability |
| Owner | BulletTrain RL platform |
| Component | `bullettrain.rl.policy_registry` |
| Verification | Test case; cross-tenant isolation test |
| Dependencies | FR-CL-DEC-001 |
| Regulatory | GDPR Art. 5(1)(f); data residency per jurisdiction |
| Risk | Policy leakage across tenants; mitigated by registry scope key |
| Status | draft |
| Version | 1.0 |
| Trace Links | UC-HC-CL-010 |
| NFR Aspects | isolation, governance |

**Acceptance Criteria.**
1. **[FRCLMT001-AC01]** [Negative] [Automated] GIVEN a policy scoped to tenant A, WHEN tenant B requests action selection, THEN the registry returns the tenant-B-scoped policy or the shared base, never the tenant-A-specific one.

### 5.9 Meta loops (REA-Agent-MCP and caid-agent self-improvement)

#### FR-CL-META-001: Requirements-agent reward signal

| Attribute | Value |
|---|---|
| REQ ID | FR-CL-META-001 |
| Title | REA-Agent-MCP usage feedback feeds a meta reward log |
| Statement | The system shall capture (requirement_id, derivation_pattern, downstream_acceptance, defect_event, ISO-25010-coverage-delta) tuples whenever a REA-Agent-MCP-derived requirement is used, accepted, modified, or implicated in a defect; these tuples form the REA-Agent meta reward log. |
| Category | functional |
| Priority | HIGH |
| Source | User direction 2026-05-14 — "these agents may evolve based on their usage" |
| Owner | REA-Agent-MCP + BulletTrain RL |
| Component | `rea_agent.feedback` module (new); reuse `bullettrain.rl.reward_log` infra |
| Verification | Test case; meta-OPE pack |
| Dependencies | FR-CL-FBK-001 |
| Regulatory | EU AI Act Annex IV §6 (oversight of AI-driven development) |
| Risk | Requirements drift from clinician needs; mitigated by usage-anchored reward |
| Status | draft |
| Version | 1.0 |
| Trace Links | FR-CL-META-002, UC-HC-CL-014 |
| NFR Aspects | adaptability, governance |

**Acceptance Criteria.**
1. **[FRCLMETA001-AC01]** [Positive] [Automated] GIVEN a REA-Agent-MCP-derived requirement that is accepted into an SRS and later passes verification, WHEN the verification event occurs, THEN the corresponding meta-reward tuple is appended to the REA-Agent meta reward log.

#### FR-CL-META-002: CAID-agent generated-code feedback

| Attribute | Value |
|---|---|
| REQ ID | FR-CL-META-002 |
| Title | CAID-agent generated-code outcomes feed a meta reward log |
| Statement | The system shall capture (task_id, pattern_invoked, generated-code-diff, V-model verification result, post-merge defect rate, clinician acceptance signal) tuples for every caid-agent generation episode; these tuples form the CAID-agent meta reward log. |
| Category | functional |
| Priority | HIGH |
| Source | User direction 2026-05-14; caid-agent V-model verification |
| Owner | caid-agent + BulletTrain RL |
| Component | `caid_agent.feedback` module (new); reuse `bullettrain.rl.reward_log` infra |
| Verification | Test case; meta-OPE pack |
| Dependencies | FR-CL-FBK-001, FR-CL-META-001 |
| Regulatory | EU AI Act Annex IV §6 |
| Risk | Generated-code regressions; mitigated by V-model gate + meta reward signal |
| Status | draft |
| Version | 1.0 |
| Trace Links | UC-HC-CL-015 |
| NFR Aspects | adaptability, governance |

**Acceptance Criteria.**
1. **[FRCLMETA002-AC01]** [Positive] [Automated] GIVEN a caid-agent generation episode that lands a verified PR, WHEN the verification completes, THEN the meta-reward tuple is appended to the CAID-agent meta reward log.

#### FR-CL-META-004: Prompt-engine clause feedback

| Attribute | Value |
|---|---|
| REQ ID | FR-CL-META-004 |
| Title | prompt-engine clause refinement is closed-loop |
| Statement | The system shall capture (clause_id, clause_version, agent_invocation, downstream_action_accepted, downstream_outcome, clinician_override_event) tuples whenever a [prompt-engine](../../prompt-engine) clause is rendered into a clinical or operational agent's reasoning; these tuples form the prompt-engine clause-refinement meta reward log. Clause-level updates are subject to the same OPE gate as clinical and meta policies via FR-CL-META-003. |
| Category | functional |
| Priority | HIGH |
| Source | User direction 2026-05-14 — "the prompt-engine to help improve the prompts if required"; prompt-engine 18-clause DSL |
| Owner | prompt-engine + BulletTrain RL |
| Component | `prompt_engine.feedback` module (new); reuse `bullettrain.rl.reward_log` infra |
| Verification | Test case; meta-OPE pack with clause regression |
| Dependencies | FR-CL-FBK-001, FR-CL-META-003 |
| Regulatory | EU AI Act Annex IV §6 (oversight of AI-driven reasoning); FDA PCCP §B (locked / unlocked model envelope — clause versions count as model parameters for this purpose) |
| Risk | Clause drift away from clinically-grounded reasoning; mitigated by clause OPE + clinician-acceptance reward |
| Status | draft |
| Version | 1.0 |
| Trace Links | UC-HC-CL-017 |
| NFR Aspects | adaptability, governance, scientific-validity |

**Rationale.** Prompt clauses are themselves a learned artefact — wording choices, clause ordering, the 4 governance policies, the healthcare renderer — that determine how every clinical and operational agent reasons. Treating clauses as fixed forfeits compound improvement; treating them as freely-edited forfeits regulatory traceability. The middle path is: clauses are versioned, attested, and their refinements promote through the same OPE gate as clinical policies, with a clause-specific Goodhart-vector catalogue maintained by CSAA.

**Acceptance Criteria.**
1. **[FRCLMETA004-AC01]** [Positive] [Automated] GIVEN a prompt-engine clause version invoked by a clinical agent and an accepted downstream action with measured outcome, WHEN the outcome window closes, THEN the corresponding meta-reward tuple is appended to the prompt-engine meta reward log.
2. **[FRCLMETA004-AC02]** [Negative] [Automated] GIVEN a clause update that regresses the clause-OPE pack, WHEN promotion is requested, THEN promotion is denied and the previous clause version remains active.

#### FR-CL-META-003: Meta-policy OPE gate

| Attribute | Value |
|---|---|
| REQ ID | FR-CL-META-003 |
| Title | Meta-policy promotion uses the same OPE gate as clinical policies |
| Statement | The system shall route REA-Agent-MCP pattern-selection-policy, caid-agent role-routing-policy, and prompt-engine clause-refinement updates through the same `bullettrain.rl.ope_gate` as clinical policies, with surface-specific thresholds. |
| Category | functional |
| Priority | MEDIUM |
| Source | helixcare-rl-implementation-plan §2 |
| Owner | CSAA (extended scope) |
| Component | `bullettrain.rl.ope_gate` with `meta` thresholds |
| Verification | Test case; CSAA sign-off |
| Dependencies | FR-CL-META-001, FR-CL-META-002, FR-CL-META-004, FR-CL-OPE-001 |
| Regulatory | EU AI Act Annex IV §6 |
| Risk | Meta-policy regress without notice; mitigated by gate |
| Status | draft |
| Version | 1.0 |
| Trace Links | UC-HC-CL-016 |
| NFR Aspects | safety, governance |

**Acceptance Criteria.**
1. **[FRCLMETA003-AC01]** [Negative] [Automated] GIVEN a candidate REA pattern-selection update with meta-OPE below threshold, WHEN promotion is requested, THEN promotion is denied.

---

## 6. Non-Functional Requirements (NFR)

Each NFR derives from ISO/IEC 25010:2023 quality characteristics and is enforceable through the verification pack named in §8.

| NFR ID | Quality characteristic | Statement | Threshold | Source |
|---|---|---|---|---|
| NFR-CL-LAT-001 | Performance: time behaviour | Closed-loop sense → decide → act → dispatch shall complete within 800 ms at P95 for operational loops; within 2,000 ms at P95 for clinical loops. | P95 < 800 ms (ops) / 2,000 ms (clin) | helixcare-business-case §5; product latency budget |
| NFR-CL-PRV-001 | Security: confidentiality | No reward-log entry, OPE artefact, or meta-reward tuple contains identifiable PHI; only SPID and policy/action identifiers. | 100% redaction at write | FR-CL-FBK-002; HIPAA; GDPR |
| NFR-CL-AUD-001 | Maintainability: analysability | Every policy decision is reconstructible from the reward log and feature-store snapshot for 7 years. | 7-year retention; bit-reproducibility | EU AI Act Art. 12; UK NHS records retention |
| NFR-CL-REP-001 | Reliability: maturity | Replay of a recorded snapshot produces a bit-identical state vector. | 100% bit-identical | Beam 2020; FR-CL-SNS-002 |
| NFR-CL-GOV-001 | Compliance | Every policy version has a current GHARRA capability card and CSAA classification. | 100% coverage | regulatory-agents.md |
| NFR-CL-GOV-002 | Compliance: BulletTrain Constitution | Closed-loop code contains zero direct sibling imports detected by semgrep + hook. | 0 violations on CI | ADR-004; BulletTrain Integration Constitution |
| NFR-CL-FRN-001 | Functional appropriateness: fairness | DIR across age, sex, ethnicity, plan type, ZIP income remains ≥ 0.80 on a rolling 90-day window. | DIR ≥ 0.80 | FR-CL-OPE-002 |
| NFR-CL-SCV-001 | Functional appropriateness: scientific validity | OPE estimator is doubly-robust; CI lower-bound gate is per-surface registered before any policy ships. | 100% gated promotions | Komorowski 2018; Gottesman 2019 |
| NFR-CL-OBS-001 | Reliability: availability | The reward log, feature store, and policy registry maintain ≥ 99.9% monthly availability. | ≥ 99.9% | Operational SLA |
| NFR-CL-REC-001 | Reliability: recoverability | Policy rollback from active version to previous registered version completes in ≤ 60 s end-to-end. | ≤ 60 s wall time | FR-CL-RBK-001 |
| NFR-CL-ISO-001 | Compatibility: interoperability | Every sense payload is FHIR R4 + Bridge-SDK-canonical; every act payload uses the sibling's published OpenAPI contract. | 100% conformance | symphonix-bridge-sdk; OpenAPI conformance tests |
| NFR-CL-USB-001 | Usability: operability | Clinician HITL approval flow has WCAG 2.2 AAA contrast and labels; provider-portal already enforces this. | WCAG 2.2 AAA | provider-portal/docs/compliance |
| NFR-CL-PORT-001 | Portability: adaptability | Closed-loop policies can be packaged for on-premises Enterprise tenants with no behavioural drift from the multi-tenant cloud build. | Drift detection: zero behavioural diff on shared OPE pack | helixcare-business-case §6.1 Enterprise |
| NFR-CL-COST-001 | Operational efficiency | LLM-inference cost per encounter for ambient-scribe + clinical-suggestion loops shall remain at or below the per-clinician margin envelope in [helixcare-business-case §8](helixcare-business-case.md). | ≤ $0.50 / encounter blended | helixcare-business-case §8 unit economics |
| NFR-CL-EVL-001 | Operational efficiency: evolvability | Meta-loop promotions (REA, CAID) shall not regress the clinical loop's OPE pack; cross-pack regression detection runs on every meta-policy promotion. | 0 clinical OPE regressions per meta promotion | FR-CL-META-003 |

---

## 7. System Constraints (SC)

Constraints are absolute. Constrained behaviour is the safety case.

| SC ID | Constraint | Rationale | Enforced by |
|---|---|---|---|
| SC-CL-001 | No closed-loop action bypasses `bullettrain.connectors.*` | BulletTrain Integration Constitution | semgrep + write-time hook + PR template |
| SC-CL-002 | No clinical policy ships without CSAA sign-off and DCB0129 hazard log update | regulatory-agents.md | CSAA gate in policy registry |
| SC-CL-003 | No autopilot at launch; HITL on every clinical action surface until autonomy is earned per CPCP | agent-first.md design principle #5 | hitl_router default-on |
| SC-CL-004 | No on-line exploration on real patient outcomes | Gottesman 2019 #7 | OPE-only promotion path |
| SC-CL-005 | No reward log entry contains external patient identifiers | symphonix-bridge-sdk patient-identity contract | SignalBox redactor + contract test |
| SC-CL-006 | No policy may be promoted with DIR < 0.80 on any protected group | FR-CL-OPE-002; four-fifths rule | bias_monitor freeze + CSAA review |
| SC-CL-007 | Every policy version is reproducible from the GHARRA capability card | NFR-CL-AUD-001 | content-addressed snapshot + signed log |
| SC-CL-008 | No emoji in any code, log, output, or documentation | workspace policy | review + linter |
| SC-CL-009 | No autonomous diagnostic claim at launch; diagnosis-support RL acts only as CDS under §520(o)(1)(E) | regulatory-agents.md | prompt-engine clause configuration; HITL |
| SC-CL-010 | Data residency by region (EU / UK / Africa / MENA / APAC / NA); cross-region federation only on explicit patient consent | GDPR; African DPA regimes | tenant routing; consent ledger |

---

## 8. Use Cases (IEEE 29148 §9.5)

### UC-HC-CL-001: Closed-loop encounter — scheduling RL produces a slot

**Actor:** Scheduling agent on behalf of a HelixCare clinician.

**Preconditions:**
- Patient is registered with a valid SPID.
- Scheduling RL policy v_n is promoted and active for the tenant.
- bullettrain.rl.feature_store has at least 30 days of historical signal for the patient cohort.

**Main Flow:**
1. Patient requests an appointment slot via citizen-portal.
2. scheduling-gateway invokes bullettrain.rl.feature_store.observe(event) to compute the canonical state vector keyed by SPID.
3. policy_registry.select_action(scheduling.v_n, state) returns a (slot, reminder_cadence, overbook_factor) action with confidence c.
4. If c ≥ HITL threshold, dispatch via bullettrain.connectors.scheduling_gateway; else enqueue HITL approval in provider-portal.
5. Patient is booked; reminder cadence is registered.
6. At appointment time, attendance event is emitted to BulletTrain FHIR EventBus.
7. bullettrain.rl.reward_log appends (state_sha, policy_id, action, reward) where reward = utilisation − no_show − α · wait_minutes.

**Postconditions:**
- Reward log contains a signed tuple for the cycle.
- DIR monitor includes the cycle in its rolling window.

### UC-HC-CL-002: Closed-loop encounter — pathway RL refines next node

**Actor:** Pathway agent on behalf of a treating clinician.

**Preconditions:**
- Pathway RL v_n is CSAA-cleared and active for the relevant clinical-pathway DAG.
- Patient is on an active pathway with state ≥ K observations.

**Main Flow:**
1. clinical-pathways emits a pathway-step event to BulletTrain FHIR EventBus.
2. feature_store.observe produces the canonical state vector.
3. policy_registry.select_action returns a node within the guideline DAG.
4. If c < HITL threshold OR action is a node-skip, route to provider-portal HITL queue.
5. Clinician approves / overrides / proceeds.
6. Action dispatched via bullettrain.connectors.clinical_pathways.
7. Outcome window (LOS, readmission-30d, PROMs at discharge) is measured.
8. Reward tuple is appended to the log.

**Postconditions:**
- Pathway step recorded; outcome attributed to (policy, action, state).
- DIR monitor updated.

### UC-HC-CL-003: Closed-loop encounter — prior-auth RL assembles documentation

**Actor:** Prior-auth agent on behalf of clinic AR.

**Preconditions:**
- Claim line with CPT / HCPCS / ICD-10 codes.
- Prior-auth RL v_n active for the payer.

**Main Flow:**
1. insurance-eclaims emits a prior-auth-required event.
2. feature_store.observe produces state vector including claim line and payer rule embedding.
3. policy_registry.select_action returns a documentation-bundle assembly + escalation path.
4. Documentation is assembled from chart with SignalBox-attested provenance.
5. Submission dispatched via bullettrain.connectors.insurance_eclaims (X12 278).
6. Payer response (approve / deny / pend) feeds the reward.
7. Tuple appended; turnaround-time metric updated.

**Postconditions:**
- Reward log updated; eclaims bias-audit four-fifths-rule monitor includes the cycle.

### UC-HC-CL-004: Closed-loop encounter — adherence bandit fires a refill nudge

**Actor:** Adherence agent on behalf of a chronic-disease patient.

**Preconditions:**
- Patient consented to adherence nudges.
- Adherence-RL bandit active for the regimen class.

**Main Flow:**
1. eps + pharmacy-system signal a refill-due event.
2. feature_store.observe produces patient context vector.
3. policy.select_action returns (channel, message_framing, timing).
4. Nudge dispatched via bullettrain.connectors.citizen_portal.
5. Patient response (dose taken / opt-out / no response) captured.
6. Biomarker outcome (where measured) feeds reward.
7. Tuple appended.

**Postconditions:**
- Patient remains opted-in or opted-out per their response.

### UC-HC-CL-005: HITL escalation — sub-confidence action routes to clinician

**Actor:** Clinician using provider-portal HITL queue.

**Preconditions:**
- An action with confidence below the per-surface HITL threshold has been selected by a policy.

**Main Flow:**
1. bullettrain.rl.hitl_router enqueues the action in the provider-portal queue with state context.
2. Clinician opens the queue, reviews state context, accepts / modifies / rejects the action.
3. Decision dispatched via the appropriate connector.
4. Clinician decision is recorded as part of the reward tuple.

**Postconditions:**
- Reward log contains the clinician decision and reasoning.
- Provider-portal audit dual-chain captures the override event.

### UC-HC-CL-006: OPE-gated policy promotion

**Actor:** RL platform engineer requesting promotion of policy v_n+1.

**Preconditions:**
- Candidate policy v_n+1 has been trained offline and registered with GHARRA capability card draft.

**Main Flow:**
1. Engineer submits promotion request through policy_registry.
2. ope_gate runs doubly-robust OPE against the production reward log.
3. ope_gate returns 95% CI lower bound on expected return delta.
4. If lower bound ≥ pre-registered threshold AND reward-hacking guard passes AND DIR projection passes, CSAA review ticket is opened.
5. CSAA reviews; on sign-off, policy is promoted and capability card is signed.

**Postconditions:**
- Policy registry reflects promoted version.
- Previous version remains available for rollback.

### UC-HC-CL-007: Bias-driven policy freeze

**Actor:** bias_monitor on rolling 90-day window.

**Preconditions:**
- A policy has been active for at least 7 days.

**Main Flow:**
1. bias_monitor computes DIR across age / sex / ethnicity / plan / ZIP-income.
2. If any DIR < 0.80, monitor sets policy state to `frozen` in the registry.
3. CSAA review ticket is opened with the offending cohort breakdown.
4. Fallback policy (previous version or baseline) becomes active.

**Postconditions:**
- Policy is frozen; no new decisions are made by the frozen version.
- Baseline policy serves until review concludes.

### UC-HC-CL-008: Reward-hacking detection

**Actor:** reward_hacking_guard nightly job.

**Preconditions:**
- An active policy has been live for ≥ 30 days.

**Main Flow:**
1. guard runs the per-surface adversarial pack.
2. Compares proxy reward to ground-truth outcome on the pack.
3. If divergence exceeds threshold, sets policy to `frozen` and opens CSAA ticket.

**Postconditions:**
- Frozen policy is taken out of rotation; baseline serves.

### UC-HC-CL-009: Operator policy rollback

**Actor:** RL platform on-call operator.

**Preconditions:**
- Active policy v_n is exhibiting anomalous behaviour reported by a tenant or surfaced by metrics.

**Main Flow:**
1. Operator issues `policy_registry rollback <policy_id> --to <previous_version>`.
2. Registry flips feature flag.
3. Next dispatch uses previous version.
4. Reward log captures rollback event with operator identity and reason.

**Postconditions:**
- End-to-end rollback completes within 60 seconds.

### UC-HC-CL-010: Per-tenant fine-tuned policy activation

**Actor:** Tenant administrator on Enterprise tier.

**Preconditions:**
- Tenant has accumulated ≥ N transitions since onboarding.

**Main Flow:**
1. Tenant requests per-tenant fine-tune of the shared base policy.
2. RL platform trains fine-tuned variant offline on tenant-scoped data.
3. Variant goes through OPE gate against the tenant-scoped reward log.
4. On clearance and CSAA sign-off, registry activates the variant for the tenant.

**Postconditions:**
- Tenant traffic served by fine-tuned variant; cross-tenant isolation preserved.

### UC-HC-CL-011: Cross-tenant federated patient — consented record handoff

**Actor:** Two HelixCare clinicians, both serving the same patient.

**Preconditions:**
- Patient has explicit consent ledger entries for both clinicians.

**Main Flow:**
1. Clinician A refers patient to Clinician B via Nexus A2A.
2. Patient citizen-portal consent ledger is checked.
3. On approval, GHARRA federates the relevant capability cards.
4. Clinician B sees the patient's full HelixCare record.
5. Subsequent encounters by Clinician B feed back to the patient's longitudinal record and the shared closed-loop reward signal where applicable.

**Postconditions:**
- Patient record is unified across both clinicians.
- Consent ledger updated.

### UC-HC-CL-012: Regulatory submission packet generation

**Actor:** Regulatory affairs lead preparing an MHRA AI Airlock submission.

**Preconditions:**
- A clinical policy has been live in shadow mode for ≥ 90 days.
- CSAA hazard log is current.

**Main Flow:**
1. Operator runs `bullettrain.rl.regulatory.export --policy <policy_id> --jurisdiction MHRA`.
2. The export bundles: capability card, OPE results with CI bounds, DIR rolling-window data, reward-hacking pack results, HITL override rate, hazard log, CPCP envelope, model card, traceability matrix.
3. Output is delivered as an MHRA-conformant submission packet.

**Postconditions:**
- Submission packet is available for regulatory review.

### UC-HC-CL-013: Insurance claim with closed-loop attribution

**Actor:** insurance-eclaims claim builder.

**Preconditions:**
- Encounter produced under HelixCare; some actions were policy-selected.

**Main Flow:**
1. Claim builder annotates the X12 837 with policy-attribution metadata (policy_id, action_sha) per HelixCare extension.
2. Claim submitted via existing X12 EDI surface.
3. Adjudication outcome feeds back to the reward log for the relevant policy.

**Postconditions:**
- Adjudication outcome is part of the policy's reward.

### UC-HC-CL-014: REA-Agent-MCP requirement evolves via meta loop

**Actor:** REA-Agent-MCP authoring a requirement update against a new pattern.

**Preconditions:**
- ≥ 200 REA-Agent-MCP-derived requirements have downstream verification signal.

**Main Flow:**
1. Meta reward log contains tuples (req_id, pattern, downstream_acceptance, defect_event).
2. REA-Agent-MCP runs offline meta-policy update on its pattern-selection policy.
3. Candidate meta-policy submitted to ope_gate with meta thresholds.
4. On clearance, REA-Agent-MCP capability card is updated.
5. New requirements derived after the update use the updated pattern-selection policy.

**Postconditions:**
- REA-Agent-MCP pattern selection improves on the empirical reward; CSAA records the change.

### UC-HC-CL-015: caid-agent generation policy evolves via meta loop

**Actor:** caid-agent (caid-plan / caid-develop / caid-engineer / caid-verify) running a build episode.

**Preconditions:**
- ≥ 100 caid-agent episodes have V-model verification outcomes recorded.

**Main Flow:**
1. Meta reward log contains tuples (task_id, pattern_invoked, generated-diff, verification_pass, post-merge_defects).
2. caid-agent runs offline meta-policy update on its role-routing and pattern-selection policies.
3. Candidate meta-policy submitted to ope_gate with meta thresholds.
4. On clearance, caid-agent capability card is updated.
5. Subsequent build episodes use the updated routing policy.

**Postconditions:**
- caid-agent generation outcomes improve on the empirical reward.

### UC-HC-CL-017: prompt-engine clause evolves via meta loop

**Actor:** prompt-engine authoring a clause refinement against accumulated clinician-acceptance signal.

**Preconditions:**
- ≥ 500 clause invocations per candidate clause have downstream accept/reject + outcome signal recorded.

**Main Flow:**
1. Meta reward log contains tuples (clause_id, clause_version, agent_invocation, downstream_action_accepted, downstream_outcome, clinician_override_event).
2. prompt-engine drafts a candidate clause refinement (wording, ordering, governance-policy change, or healthcare-renderer adjustment).
3. Clause OPE pack runs against the meta reward log with the doubly-robust estimator and the clause-Goodhart-vector catalogue.
4. Candidate clause version submitted to ope_gate with clause thresholds.
5. ope_gate also runs the clinical OPE cross-impact pack on any clinical policies whose recent generation invoked the candidate clause (per UC-HC-CL-016).
6. On clearance, prompt-engine capability card is updated and the new clause version becomes active.
7. Subsequent clinical and operational agent invocations use the updated clause.

**Postconditions:**
- prompt-engine clause refinement improves on the empirical reward without regressing clinical OPE.
- Old clause version remains in registry for rollback per FR-CL-RBK-001.

### UC-HC-CL-016: Meta-policy cross-impact check

**Actor:** ope_gate during a meta-policy promotion.

**Preconditions:**
- A REA or CAID meta-policy candidate has cleared its own OPE.

**Main Flow:**
1. ope_gate runs the clinical OPE pack against any clinical policies whose recent generation involved the candidate meta-policy.
2. If clinical OPE regresses beyond pre-registered tolerance, the meta-policy promotion is blocked.

**Postconditions:**
- Meta-policy promotion does not silently regress clinical outcomes.

---

## 9. Verification and Validation

### 9.1 Verification per surface

Every surface defined in [helixcare-business-case §5](helixcare-business-case.md) has a verification pack consisting of:

1. **Unit tests** — feature-store determinism, redaction, signature chain, registry behaviour, rollback timing.
2. **Integration tests** — sense → decide → act → feedback round-trip across BulletTrain connectors.
3. **OPE evaluation pack** — pre-registered estimators, pre-registered thresholds, pre-registered cohort breakdowns for DIR.
4. **Reward-hacking adversarial pack** — surface-specific Goodhart vectors with proxy/ground-truth divergence assertions.
5. **HITL acceptance scenarios** — provider-portal E2E covering approve, modify, reject paths.
6. **Bias-monitor simulation** — rolling-window simulation against synthetic and historical real-world cohort data.
7. **Regulatory artefact pack** — capability card, model card, hazard log entry, CPCP envelope.

### 9.2 V-model alignment

The caid-agent V-model verification operates on each generated component: requirement (REA-Agent-MCP) → architecture → component design → code → unit verify → integration verify → system verify → acceptance verify. The HelixCare closed-loop SRS is the requirements input to that V-model; the verification rungs map to the verification pack in §9.1.

### 9.3 Validation in shadow mode

Every clinical policy runs in shadow mode for a pre-registered window (typically 30–90 days, surface-dependent) before any HITL-approved live decisions. Shadow-mode reward tuples are tagged so OPE distinguishes between baseline and shadow data sources.

### 9.4 Continuous monitoring

Once live, every policy is monitored by:

- DIR rolling 90-day window per protected group (NFR-CL-FRN-001).
- Reward-hacking nightly adversarial pack (FR-CL-RHG-001).
- HITL override-rate trend per surface.
- Outcome drift (PSI / KL divergence vs. baseline).
- Latency SLA (NFR-CL-LAT-001).

Breaches trigger automatic freeze or operator alert per the matrix in §7.

---

## 10. Traceability Matrix

| Use Case | FRs | NFRs | Constraints | Repos |
|---|---|---|---|---|
| UC-HC-CL-001 (scheduling) | FR-CL-SNS-001, FR-CL-DEC-001, FR-CL-ACT-001, FR-CL-FBK-001, FR-CL-OPE-002 | NFR-CL-LAT-001, NFR-CL-FRN-001 | SC-CL-001, SC-CL-006 | scheduling-gateway, appointment-system, citizen-portal, BulletTrain |
| UC-HC-CL-002 (pathway) | FR-CL-SNS-001, FR-CL-DEC-001, FR-CL-DEC-002, FR-CL-ACT-002, FR-CL-FBK-001 | NFR-CL-LAT-001, NFR-CL-GOV-001 | SC-CL-002, SC-CL-003 | clinical-pathways, provider-portal, BulletTrain, csaa |
| UC-HC-CL-003 (prior-auth) | FR-CL-SNS-001, FR-CL-DEC-001, FR-CL-ACT-001, FR-CL-FBK-001 | NFR-CL-FRN-001 | SC-CL-006 | insurance-eclaims, BulletTrain |
| UC-HC-CL-004 (adherence) | FR-CL-SNS-001, FR-CL-DEC-001, FR-CL-ACT-001, FR-CL-FBK-001, FR-CL-FBK-002 | NFR-CL-PRV-001 | SC-CL-005 | citizen-portal, eps, pharmacy-system |
| UC-HC-CL-005 (HITL) | FR-CL-ACT-002 | NFR-CL-USB-001 | SC-CL-003 | provider-portal, BulletTrain |
| UC-HC-CL-006 (OPE) | FR-CL-OPE-001, FR-CL-RHG-001 | NFR-CL-SCV-001 | SC-CL-004 | csaa, BulletTrain |
| UC-HC-CL-007 (bias freeze) | FR-CL-OPE-002 | NFR-CL-FRN-001 | SC-CL-006 | csaa, insurance-eclaims, BulletTrain |
| UC-HC-CL-008 (reward hack) | FR-CL-RHG-001 | NFR-CL-SCV-001 | (—) | csaa, BulletTrain |
| UC-HC-CL-009 (rollback) | FR-CL-RBK-001 | NFR-CL-REC-001 | (—) | BulletTrain |
| UC-HC-CL-010 (per-tenant) | FR-CL-MT-001 | NFR-CL-PORT-001 | (—) | BulletTrain |
| UC-HC-CL-011 (federation) | FR-CL-DEC-001 (cross-tenant) | NFR-CL-ISO-001 | SC-CL-010 | global-agent-registry, nexus-a2a-protocol, citizen-portal |
| UC-HC-CL-012 (regulatory) | FR-CL-OPE-001, FR-CL-FBK-001 | NFR-CL-AUD-001, NFR-CL-GOV-001 | SC-CL-002 | csaa, BulletTrain |
| UC-HC-CL-013 (claims attribution) | FR-CL-FBK-001 | NFR-CL-AUD-001 | (—) | insurance-eclaims, BulletTrain |
| UC-HC-CL-014 (REA meta) | FR-CL-META-001, FR-CL-META-003 | NFR-CL-EVL-001 | (—) | REA-Agent-mcp, BulletTrain, csaa |
| UC-HC-CL-015 (CAID meta) | FR-CL-META-002, FR-CL-META-003 | NFR-CL-EVL-001 | (—) | caid-agent, BulletTrain, csaa |
| UC-HC-CL-016 (meta cross-impact) | FR-CL-META-003 | NFR-CL-EVL-001 | (—) | csaa, BulletTrain |
| UC-HC-CL-017 (prompt meta) | FR-CL-META-004, FR-CL-META-003 | NFR-CL-EVL-001, NFR-CL-SCV-001 | (—) | prompt-engine, BulletTrain, csaa |

---

## 11. Open Items and Next Steps

1. **REA-Agent-MCP integration.** Author a follow-up doc `helixcare-rea-meta-loop.md` defining the exact reward-tuple schema and the meta-policy update cadence for the requirements-engineering agent.
2. **caid-agent integration.** Author `helixcare-caid-meta-loop.md` similarly for the development orchestrator.
2a. **prompt-engine integration.** Author `helixcare-prompt-meta-loop.md` defining the clause-level reward tuple schema, the clause-Goodhart-vector catalogue, and the clause-OPE pack maintenance cadence.
3. **Per-surface CPCP envelopes.** Eight Closed-loop Predetermined Change Control Plans, one per surface. Owned by Regulatory Affairs lead.
4. **Reward-hacking adversarial packs.** Per-surface Goodhart-vector catalogues, owned by CSAA.
5. **Shadow-mode runbook.** Operational procedure for 30–90-day shadow before HITL-live.
6. **Per-jurisdiction data residency map.** Confirm region-by-region storage and federation rules.
7. **REA-Agent-MCP and caid-agent capability card schema extension.** Add fields for `meta_policy_version`, `meta_reward_log_pointer`, `last_promotion_csaa_ticket`.

Each follow-up doc lands in `symphonix-health-docs/strategy/` and cross-links to this SRS.

---

## Appendix A — Closed-loop quick reference

```
Sense    →  bullettrain.rl.feature_store  →  Bridge SDK canonical state
Decide   →  bullettrain.rl.policy_registry → policy v_n with capability card
Act      →  bullettrain.connectors.<sibling> (or api_gateway)  → HITL queue if c < threshold
Feedback →  SignalBox attest + bullettrain.rl.reward_log → OPE gate → CSAA review → promote / freeze / rollback
```

Meta-loops run over the same plane with three subject policies — `REA-Agent-MCP` (requirements pattern selection), `caid-agent` (development role routing), `prompt-engine` (clause refinement) — and the clinical OPE pack as the cross-impact gate.

---

*End of SRS v0.1. Open items in §11 are the priority backlog for v0.2.*
