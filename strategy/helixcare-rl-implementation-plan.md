# HelixCare RL Implementation Plan - v1.0

**Status:** Implementation kickoff baseline
**Authored:** 2026-05-14
**Companion to:** [helixcare-business-case.md §5](./helixcare-business-case.md) (the eight RL surfaces)
**Anchor pattern:** [agent-first.md](./agent-first.md) - *"Reference agent before scale"*
**Implementation start:** Phase 0 and Wave 1 may commence from this plan. Clinical activation remains gated by the evidence, safety, and regulatory controls below.

---

## 1. Execution Thesis

HelixCare does **not** ship eight RL surfaces in parallel. We build one administrative reference surface end-to-end, extract the reusable RL operating system, then expand by risk tier:

1. **Phase 0:** build and validate `bullettrain.rl`, the shared policy, evidence, reward, and governance layer.
2. **Wave 1:** ship Prior-Auth RL as the reference surface in shadow mode, then HITL-live only after evidence gates pass.
3. **Wave 2:** expand to operational surfaces with constrained contextual bandits.
4. **Wave 3:** prepare clinical surfaces as regulated AI/ML device or high-risk AI candidates; build may proceed, but clinical activation waits for classification, safety case, regulator engagement where required, and prospective validation.

The implementation rule is simple: **autonomy is earned per action class, not per surface.** Every policy starts in shadow. Every live recommendation is versioned, logged, replayable, reversible, and attributable to a named policy card.

### Non-negotiables

| Rule | Implementation consequence |
|---|---|
| No online exploration in clinical workflows | Clinical policies train offline or in simulation only; live systems recommend under HITL |
| No regulator-shortcut assumptions | Each clinical surface carries intended-use classification before clinical activation |
| Lower-risk does not mean zero-risk | Prior-auth, scheduling, inbox, and adherence still receive equity, delay-harm, and appealability controls |
| No opaque reward-only promotion | Promotion requires OPE, overlap, subgroup, calibration, harm, and human-override evidence |
| No policy update outside change control | Even prompt, threshold, feature, or reward-shape changes receive policy-version review |
| No patient-facing manipulation | Adherence and scheduling use explicit consent, opt-out, quiet hours, burden budgets, and no dark patterns |

---

## 2. Regulatory And Safety Baseline

This plan uses a conservative classification posture. The engineering teams may build the software now, but activation is constrained by intended use, market, and evidence state.

### 2.1 Jurisdiction posture

| Jurisdiction | Baseline posture | Implementation implication |
|---|---|---|
| US | Non-device CDS is available only when all FDA CDS criteria are met. Many CDS-like functions remain medical devices. PCCP applies inside a marketing submission for AI-enabled devices. | Every clinical or medical-necessity surface needs an intended-use statement, CDS criteria assessment, and fallback SaMD pathway. Do not label a surface "CDS excluded" until the four criteria are explicitly evidenced. |
| UK | DCB0129 covers manufacture; DCB0160 covers deployment and use. MHRA AI Airlock is a sandbox/engagement path for AIaMD regulatory questions, not a generic clearance mechanism. | Every UK clinical-decision deployment needs a clinical safety case, hazard log, named clinical safety officer, deployment safety case, and MHRA route decision. |
| EU | EU AI Act high-risk obligations may apply to clinical and healthcare-access AI. MDR/IVDR classification depends on medical purpose and software function. Annex IV technical documentation is necessary for high-risk AI systems. | Each EU launch needs AI Act classification, MDR/IVDR Rule 11 analysis where medical purpose exists, post-market monitoring, logging, human oversight, and CE/conformity route where applicable. |
| HIPAA / GDPR | SPID-only streams are pseudonymised unless de-identification is independently established. | Reward logs remain regulated data unless privacy review confirms de-identification. Treat SPID as a linkable identifier with access controls, retention, audit, and DPIA/BAA coverage. |

### 2.2 Surface classification table

| # | Surface | Launch posture | Regulatory posture before activation |
|---|---|---|---|
| 4 | Prior-auth RL | Wave 1 reference; shadow first, then HITL-live in design partners | Administrative / access-to-care system. Not "zero patient-safety risk." Requires delay-harm monitoring, appealability, equity review, and medical-necessity CDS/SaMD screen per payer workflow. |
| 1 | Scheduling RL | Wave 2 operational | Operational access system. Requires wait-time equity, urgent-slot protection, no-show fairness, and EU high-risk/profiling screen before EU rollout. |
| 5 | Inbox-triage RL | Wave 2 operational with clinical-message partitioning | Administrative messages can remain operational. Clinical advice, refill protocoling, or symptom triage require CDS/SaMD classification and DCB review. |
| 6 | Adherence RL | Wave 2 operational/patient engagement | Consent-based engagement surface. Disease-specific adherence optimization may carry medical-purpose classification. Requires opt-out, burden budget, and no behavioural dark patterns. |
| 2 | Clinical pathway RL | Wave 3 regulated clinical surface | Treat as SaMD/AIaMD candidate unless legal/regulatory review says otherwise. Requires guideline shield, clinical safety case, PCCP/update envelope, human factors, and prospective validation. |
| 3 | ED / triage RL | Wave 3 regulated clinical surface | Treat as high-risk clinical triage support. No down-triage autonomy. Requires MTS shield, triage-nurse confirmation, safety case, and prospective silent trial. |
| 7 | Diagnosis support RL | Wave 3 regulated clinical surface | Must either satisfy all non-device CDS criteria or proceed as SaMD. Clinician must independently review basis. No autonomous diagnosis, ordering, or differential suppression. |
| 8 | Resource allocation RL | Wave 3 regulated operational-clinical surface | Treat as safety-critical allocation support. Use constrained optimisation first; RL only in simulation until evidence supports escalation. Requires fairness, incident, and human-override monitoring. |

---

## 3. Shared RL Operating System (`bullettrain.rl`)

`bullettrain.rl` lives inside BulletTrain because BulletTrain already owns integration, canonical data flow, auth, audit, SignalBox, and GHARRA wiring. Phase 0 is not just scaffolding: it must produce replayable evidence suitable for CSAA and external review.

### 3.1 Work packages

| WP | Component | Owner | Build scope | Acceptance criteria |
|---|---|---|---|---|
| WP0.1 | `bullettrain.rl.contracts` | BulletTrain + CSAA | Versioned state/action/reward/policy schemas; JSON Schema + Python models; surface-specific action vocabularies | Schemas compile; each of eight surfaces has a registered action set, forbidden-action set, and primary/secondary outcome map |
| WP0.2 | `bullettrain.rl.feature_store` | BulletTrain | FHIR-canonical deterministic snapshots via Bridge SDK; feature lineage; late-arriving data handling | Same encounter replay returns identical feature vector; every feature has source system, timestamp, transform, and PHI class |
| WP0.3 | `bullettrain.rl.reward_log` | SignalBox | Append-only reward events; GHARRA-anchored Ed25519 signatures; policy/action/user context | Every tuple records state hash, action, propensity, policy version, actor, reward source, and delayed-outcome linkage |
| WP0.4 | `bullettrain.rl.ope_gate` | CSAA | IPS, SNIPS, doubly robust OPE, bootstrap CIs, effective sample size, overlap checks, subgroup metrics | Gate blocks promotion when overlap is poor, sample support is thin, subgroup harm worsens, or lower CI misses threshold |
| WP0.5 | `bullettrain.rl.policy_registry` | GHARRA | Capability-card extension for policies: version, intended use, activation scope, evidence pack, rollback pointer | Policy cannot activate without signed card, owner, approved gate report, activation window, and previous-version pointer |
| WP0.6 | `bullettrain.rl.hitl_router` | Provider-Portal | HITL queue routing, confidence thresholds, action-class approvals, override capture | Human accept/reject/edit/override is logged and replayable; emergency bypass is available for clinical workflows |
| WP0.7 | `bullettrain.rl.reward_hacking_guard` | CSAA | Surface-specific adversarial packs and Goodhart tests | Each surface has at least ten named reward-hacking vectors with automated or manual test evidence |
| WP0.8 | `bullettrain.rl.privacy_controls` | Security + Data Protection | PHI classification, pseudonymization, re-identification controls, retention, DPIA hooks | Reward log is treated as regulated data until privacy review says otherwise; access is least-privilege and auditable |
| WP0.9 | `bullettrain.rl.monitoring` | Observability | Drift, reward, harm, override, fairness, and rollback dashboards | On-call can see active policy versions, gate status, subgroup metrics, incident triggers, and rollback controls |

### 3.2 Activation gate

No policy promotes beyond shadow unless all checks pass:

| Gate | Required evidence |
|---|---|
| Data readiness | Feature completeness, missingness by subgroup, source-system latency, delayed outcome availability, logged propensities |
| Offline replay | Deterministic state reconstruction; baseline-policy replay; no forbidden action emitted |
| Support / overlap | Candidate policy actions are supported by historical data or bounded by simulator evidence; poor-overlap segments route to HITL |
| OPE | Primary reward lower 95% CI >= baseline; no material worsening on secondary safety outcomes; ESS above surface threshold |
| Equity | Four-fifths DIR >= 0.80 where applicable, plus subgroup performance, false-positive/false-negative, wait-time, delay, and override-rate checks |
| Human factors | Intended user can understand recommendation, basis, uncertainty, and override path without workflow degradation |
| Clinical safety | CSAA sign-off for clinical or access-to-care risk; DCB0129/0160 artefacts where UK deployment is in scope |
| Privacy/security | DPIA/BAA/data-sharing assessment complete; reward stream classification and retention approved |
| Rollback | Feature flag verified; rollback under 60 seconds; prior version and event audit remain intact |

### 3.3 Evidence states

| State | Meaning | Live behaviour |
|---|---|---|
| `LAB_ONLY` | Training, simulation, or offline replay only | No production user sees outputs |
| `SHADOW` | Runs on production events, no workflow influence | Outputs are logged but invisible or clearly marked non-actionable |
| `HITL_SUGGEST` | Human sees suggestion with basis and can reject/edit | No autonomous execution |
| `ASSISTED_ACTION` | Low-risk action can execute after explicit configured human approval or protocol approval | Only action classes with passed gates |
| `AUTONOMOUS_LIMITED` | Narrow operational action class can execute within approved envelope | Not available for Wave 3 clinical actions in v1.0 |
| `FROZEN` | Policy cannot emit workflow-affecting output | Triggered by harm, fairness, drift, incident, or expired evidence |

### 3.4 Test-scope gap review

The current implementation-plan repository has no discoverable CAID canonical harness for HelixCare RL. A scoped CAID test-agent run against `symphonix-health-docs` reports `Targets: 0`, which means implementation could otherwise begin without an executable matrix gate, V-model coverage, or requirement-to-scenario traceability. That is not acceptable for this programme.

The test scope is therefore part of Phase 0, not a later QA activity. No RL feature ticket is complete until it has linked canonical matrix rows, executable tests at the relevant V-model levels, and a passing matrix-integrity check.

### 3.5 Canonical test harness baseline

The active CAID contract for new HelixCare work is `BT_CANONICAL_MATRIX_V2_18COL`. Legacy 14-column JSON matrices may be emitted only as compatibility sidecars for existing BulletTrain harnesses; they are not the source of truth. The V2 matrix remains authoritative, and the sidecars must be regenerated from V2 rows so requirement IDs, scenario IDs, use-case IDs, and verification levels cannot diverge.

Each HelixCare canonical matrix must contain exactly 100 realistic, unique scenarios with an 85 / 10 / 5 split: 85 positive, 10 negative, and 5 edge. Every row must include or reference:

- Requirement ID(s), use-case ID, scenario ID, and verification level.
- The target component or surface, preconditions, trigger, payload, expected connector calls, expected events, expected outputs, fault profile, security profile, priority, automation status, duration, and tags.
- One V-model rung from `unit`, `integration`, `system`, or `acceptance`; traceability must prove every requirement has at least one row at every required rung and that no scenario is orphaned.

Required repository artifacts:

| Artifact | Required path | Purpose |
|---|---|---|
| Matrix integrity test | `tests/test_canonical_matrix_integrity.py` | Fails closed on missing V2 metadata, wrong columns, duplicate scenario IDs, row count drift, ratio drift, orphan requirements, or unsupported verification levels |
| Test-agent manifest | `tests/harness/matrix_config.toml` | Declares HelixCare RL matrices, owning repo, implementation package, and compatibility sidecars |
| Functional surface matrices | `tests/harness/canonical_matrices/helixcare_rl_<surface>.json` | Eight 100-scenario matrices, one each for prior-auth, scheduling, inbox-triage, adherence, clinical-pathway, ED-triage, diagnosis-support, and resource-allocation |
| Shared component matrices | `tests/harness/canonical_matrices/helixcare_rl_<component>.json` | 100-scenario matrices for contracts, feature-store, reward-log, OPE gate, policy registry, HITL router, reward-hacking guard, privacy controls, monitoring, and rollback |
| NFR matrices | `tests/harness/nfr_canonical_matrices/helixcare_rl_<nfr>.json` | 100-scenario matrices for privacy/security, auditability, latency, reliability/rollback, fairness, explainability, human oversight/usability, clinical safety, and regulatory traceability |
| Legacy compatibility sidecars | `tests/harness/json_matrices/*.json` | Generated 14-column projections only where existing BulletTrain tests require them |
| Requirements traceability | `tests/harness/requirements_matrix.json` | Maps SRS FR/NFR IDs, implementation tickets, canonical scenario IDs, V-model rung, owner, and evidence artifact |
| V-model executable suites | `tests/harness/v_model/` | Unit, integration, system, and acceptance suites parametrized from the canonical scenario IDs |

Minimum scenario families that must be present before Wave 1 shadow:

| Area | Positive coverage | Negative coverage | Edge coverage |
|---|---|---|---|
| Contracts and schemas | Valid state/action/reward/policy/decision envelopes across all eight surfaces | Missing required fields, unknown action classes, stale schema versions, invalid propensities | Version-boundary migration, late-arriving outcomes, null optional context, high-cardinality tags |
| Feature snapshots | Deterministic FHIR-canonical replay, source lineage, PHI class propagation | Inconsistent source timestamps, missing SPID mapping, invalid transform provenance | Duplicate events, backfilled encounters, daylight-saving and timezone boundary cases |
| Reward log | Signed append-only events, delayed reward linkage, actor/policy attribution | Broken Ed25519 signature, hash mismatch, missing propensity, unapproved reward source | Reward reversal, late reward arrival, duplicate reward event, retention-window boundary |
| OPE gate | IPS, SNIPS, doubly robust estimates, bootstrap CI, overlap, ESS, subgroup metrics | Poor overlap, low ESS, subgroup harm, lower CI below threshold, unsupported action segment | Small subgroup cell, wide CI, conflicting primary/secondary outcomes, simulator-only support |
| Policy registry | Signed policy card, activation window, evidence pack, rollback pointer | Unsigned card, missing owner, expired evidence, change outside review | Patch update within PCCP envelope, rollback pointer to frozen version, concurrent promotion request |
| HITL router | Accept/reject/edit/override capture, emergency bypass, replayable decisions | Missing override reason, bypass without authorization, action emitted outside approval class | Clinician edits suggested action, queue timeout, multi-approver conflict |
| Reward-hacking guard | Goodhart vectors detected and routed to review | Reward increases while safety worsens, gaming cycle-time metric, subgroup burden shift | Sparse-harm signal, delayed appeal spike, proxy metric drift |
| Privacy and security | SPID-only handling, access control, audit log, retention and DPIA hooks | PHI leakage, re-identification path, unauthorised reward-log read, missing audit event | DSAR/delete hold conflict, retention boundary, cross-border transfer classification |
| Monitoring and rollback | Drift, harm, fairness, override, and rollback dashboards update from live evidence | Dashboard missing active policy, rollback exceeds 60 seconds, incident trigger ignored | Partial rollback, stale cache after freeze, policy card visible before activation |

V-model execution scope:

| Rung | Required tests |
|---|---|
| Unit | Schema model validation, policy-card validation, reward-log signing, OPE metric calculations, action vocabulary guards |
| Integration | Real service-path tests across BulletTrain, SignalBox, GHARRA, Provider Portal, insurance-eclaims, Bridge SDK, and CSAA using deterministic fixtures; mocks are not sufficient for promotion evidence |
| System | End-to-end replay from historical event to feature vector to action to reward log to OPE report to policy card and freeze/rollback path |
| Acceptance | Design-partner shadow evidence, HITL usability checks, evidence-pack export, policy change-board approval, clinical safety/regulatory sign-off where applicable |

---

## 4. Algorithm Decisions

The initial plan intentionally uses boring, auditable algorithms where they are sufficient. More complex RL is deferred until the evidence justifies it.

| Surface | v1.0 algorithm | Explicitly deferred |
|---|---|---|
| Prior-auth | Contextual bandit using LinUCB / logistic Thompson sampling; `vowpalwabbit` acceptable for baseline; no autonomous denial | PPO escalation strategy, NeuralUCB, and online exploration until 100k+ high-quality transitions and OPE support |
| Scheduling | Constrained contextual bandit with hard capacity and urgent-slot shields | Full RL over appointment book unless simulator and prospective evidence exist |
| Inbox-triage | Classifier/ranking bandit for route and draft suggestion; LLM output remains HITL and policy-versioned | Auto-send for clinical content; PPO routing until delayed harms are measurable |
| Adherence | Consent-aware contextual bandit per regimen class; burden budget and opt-out as hard constraints | Biomarker-driven reward as primary reward; full RL across multi-med regimens until lagged outcome model is validated |
| Clinical pathway | Offline CQL only inside guideline DAG shield; `d3rlpy` candidate | Online exploration; recommendation outside guideline DAG without explicit clinician override |
| ED / triage | Start with constrained ordinal/ranking model plus Manchester Triage shield; CPO research track only after simulator validation | Direct CPO in live triage; any down-triage autonomy |
| Diagnosis support | Offline ranking/reward model from adjudicated cases; transparent basis and retrieval trace | PPO-based differential ordering in production; differential suppression |
| Resource allocation | Constrained optimisation / MILP first; OR-Tools-style solver with safety and fairness constraints; RL only in simulation | Constrained DDPG in live bed/staff allocation |

Implementation note: `stable-baselines3` is suitable for PPO/DDPG/SAC/TD3 experiments, but it is **not** the production answer for CPO. If CPO remains necessary, select a dedicated safe-RL implementation or build a constraint/shield layer with CSAA review.

---

## 5. Wave 1 Reference Surface: Prior-Auth RL

Prior-auth remains the reference surface because `insurance-eclaims` is the canonical agent and X12 workflows give the cleanest closed-loop transition. The risk framing changes: this is **lower clinical immediacy**, not zero patient-safety risk.

### 5.1 Scope

| Item | Decision |
|---|---|
| Sibling | `insurance-eclaims` |
| Shared infra | `bullettrain.rl` |
| Initial state | CPT/HCPCS, ICD-10, payer rule, requested service, documentation completeness, prior denials, deadline, patient continuity risk, protected-group attributes for audit only |
| Initial actions | assemble documentation bundle, request missing chart evidence, route to human reviewer, suggest peer-to-peer escalation, suggest appeal path |
| Forbidden actions | auto-deny, fabricate evidence, suppress missing evidence, hide appeal route, route urgent continuity-risk case to slow lane |
| Initial reward | approval outcome - cycle-time penalty - appeal-cost penalty - continuity-delay penalty |
| Primary guardrail | no direct denial; urgent continuity cases always human-reviewed; unsupported action regions route to HITL |
| Shadow window | Minimum 4 weeks and at least the pre-registered minimum supported transitions per payer/use-case |

### 5.2 Prior-auth build tasks

| Task | Owner | Done when |
|---|---|---|
| PA-1 Action vocabulary | insurance-eclaims + CSAA | Every action has allowed/forbidden status, required provenance, and HITL class |
| PA-2 State extractor | insurance-eclaims + Bridge SDK | Historical X12/FHIR cases replay into deterministic feature snapshots |
| PA-3 Logging adapter | insurance-eclaims + SignalBox | Existing queue emits state/action/reward/provenance events into `bullettrain.rl.reward_log` |
| PA-4 Baseline policy | insurance-eclaims | Current human/rules workflow is captured as comparator with propensities or deterministic-action labels |
| PA-5 Candidate policy | BulletTrain RL | LinUCB/logistic Thompson model trains offline and emits calibrated action scores |
| PA-6 OPE report | CSAA | DR/SNIPS report covers primary reward, cycle time, continuity delay, appeals, and subgroup metrics |
| PA-7 Shadow dashboard | Observability | Design partners show baseline vs candidate outcomes, overrides, delays, fairness, and rollback readiness |
| PA-8 Reference artefact | Docs owner | `helixcare-rl-reference-prior-auth.md` documents patterns, gates, failures, and reusable components |

### 5.3 Prior-auth live criteria

Prior-auth may move from `SHADOW` to `HITL_SUGGEST` only when:

- No forbidden action appears in replay or shadow logs.
- OPE lower 95% CI is at least baseline on primary utility.
- No subgroup has material worsening in denial, delay, appeal, or reviewer override metrics.
- Urgent continuity-risk cases show no increased turnaround time.
- Human reviewers can see evidence provenance and reject/edit every suggestion.
- Rollback to previous policy version is tested in production-like environment.

---

## 6. Wave 2 Operational Surfaces

Wave 2 starts only after the Prior-Auth reference pattern has produced working contracts, logs, OPE reports, dashboards, and rollback evidence. Wave 2 can build in parallel, but each surface gates independently.

### 6.1 Scheduling RL

| Field | Implementation decision |
|---|---|
| Sibling | `scheduling-gateway` + `appointment-system` |
| State | patient cohort, appointment type, slot, clinician availability, historical attendance, travel/channel constraints, urgency, prior waits |
| Action | single-book, capped double-book, reminder cadence, alternative slot offer |
| Reward | attendance + utilisation - wait-time penalty - overrun penalty - urgent-slot breach penalty |
| Hard constraints | never overbook urgent slots; cap double-booking by clinician/session; preserve accessibility accommodations |
| Fairness | wait-time and cancellation metrics by age, language, disability marker where lawful, deprivation proxy, and geography |
| Gate to live | 4-week shadow, no urgent-slot breach, no subgroup wait-time regression, clinician override below threshold |

### 6.2 Inbox-Triage RL

| Field | Implementation decision |
|---|---|
| Sibling | `provider-portal` |
| State | message type, content embedding, patient acuity, medication/protocol context, clinician inbox load, historical routing |
| Action | route to staff, draft reply, request clinician review, defer with SLA, escalate |
| Reward | clinician time saved + SLA met - patient delay - unsafe-routing event - dissatisfaction |
| Hard constraints | never auto-send clinical advice; clinical/refill protocol actions require explicit approved protocol; red-flag symptoms always escalate |
| Fairness | response time, escalation, and misroute rates by language, age, deprivation proxy, disability marker where lawful |
| Gate to live | clinical-message partitioning validated; red-flag recall meets threshold; all drafts remain HITL |

### 6.3 Adherence RL

| Field | Implementation decision |
|---|---|
| Sibling | `citizen-portal` + `pharmacy-system` + `eps` |
| State | regimen, fill history, stated preference, channel consent, quiet hours, nudge fatigue, patient-reported burden, relevant outcome trend |
| Action | channel, cadence, timing, framing, caregiver copy only when consented |
| Reward | refill-on-time / PDC improvement - opt-out - burden - complaint; biomarker improvement is delayed secondary evidence |
| Hard constraints | opt-out is one tap; no quiet-hours messaging; no escalation of pressure after negative feedback; caregiver involvement requires explicit consent |
| Fairness | opt-out, burden, adherence, and language accessibility by age, language, socioeconomic proxy, and condition |
| Gate to live | consent capture verified; opt-out terminates policy; burden budget enforced |

---

## 7. Wave 3 Clinical Surfaces

Wave 3 build can start after Phase 0 contracts exist, but clinical activation is evidence-clocked and regulator-clocked. Do not promise live dates until classification and regulator route are agreed.

### 7.1 Clinical Pathway RL

| Field | Implementation decision |
|---|---|
| Sibling | `clinical-pathways` |
| Algorithm | Offline CQL inside guideline DAG shield |
| Action | next pathway node, monitoring cadence, escalation recommendation |
| Forbidden action | recommendation outside NICE/AHRQ/local guideline DAG unless surfaced as clinician override pathway |
| Evidence package | guideline trace, dataset representativeness, OPE, subgroup outcomes, clinician comprehension, DCB0129 hazard log, post-market plan |
| Activation | `HITL_SUGGEST` only after clinical safety case and jurisdiction route clearance |

### 7.2 ED / Triage RL

| Field | Implementation decision |
|---|---|
| Sibling | `triage-api` |
| Algorithm | Constrained ordinal model plus MTS shield; CPO remains research track |
| Action | queue priority within safe category, clinician routing, escalation recommendation |
| Forbidden action | down-triage MTS Category 1 or 2; autonomous category assignment |
| Evidence package | prospective silent trial, mistriage analysis, red-flag recall, triage-nurse override review, DCB hazard log |
| Activation | HITL nurse confirmation always required in v1.0 |

### 7.3 Diagnosis Support RL

| Field | Implementation decision |
|---|---|
| Sibling | `provider-portal` + `prompt-engine` |
| Algorithm | Offline ranking/reward model from adjudicated cases; retrieval-grounded basis |
| Action | differential ordering suggestion, next-test suggestion, escalation prompt |
| Forbidden action | autonomous diagnosis, autonomous test order, suppressing differential below configured confidence, hiding uncertainty |
| Evidence package | FDA CDS criteria assessment, independent-review basis, clinical performance, human factors, bias review, post-market monitoring |
| Activation | US non-device CDS only if all criteria are met; otherwise SaMD route |

### 7.4 Resource Allocation RL

| Field | Implementation decision |
|---|---|
| Sibling | `picis-system` + `scheduling-gateway` |
| Algorithm | Constrained optimisation first; simulation-only RL research track |
| Action | bed assignment recommendation, staff mix recommendation, theatre scheduling suggestion, telemedicine offload suggestion |
| Forbidden action | autonomous ICU/HDU allocation, hidden rationing, optimisation that excludes high-need/high-cost cohorts |
| Evidence package | fairness, incident, clinical escalation, staff fatigue, adverse-event, and override analysis |
| Activation | HITL charge nurse / bed manager approval always required in v1.0 |

---

## 8. Implementation Timeline

The timeline has two clocks:

- **Build clock:** code and internal evidence generation.
- **Activation clock:** clinical safety, legal, regulator, and prospective validation.

### 8.1 Build clock

| Window | Implementation output |
|---|---|
| Days 0-2 | Kickoff, owners, issue board, canonical test-harness scaffold, action vocabulary templates, policy-card template, initial risk register |
| Sprint weeks 1-2 | `bullettrain.rl.contracts`, feature-store skeleton, reward-log adapter, policy registry skeleton, Prior-Auth state/action extractor, first passing canonical matrix integrity gate |
| Sprint weeks 3-4 | OPE gate v1, replay harness, baseline policy capture, prior-auth candidate policy, rollback and monitoring hooks, V-model unit and integration suites parametrized from canonical scenarios |
| Sprint weeks 5-8 | Prior-auth design-partner shadow; weekly CSAA OPE/fairness/harm review; reference artefact |
| Sprint weeks 9-14 | Wave 2 build and shadow: scheduling, inbox-triage, adherence; each gates independently |
| Sprint weeks 6-14 in parallel | Wave 3 data-readiness, intended-use classification, hazard-log draft, and simulator/offline replay work |
| Sprint weeks 15+ | Wave 3 evidence packages, prospective silent trials, regulator engagement where required |

### 8.2 Activation clock

| Surface tier | Earliest activation posture |
|---|---|
| Prior-auth | `HITL_SUGGEST` after 4-week shadow and passed gates; no auto-denial |
| Wave 2 operational | `HITL_SUGGEST` or narrow `ASSISTED_ACTION` after 4-week shadow per action class |
| Wave 3 clinical | `HITL_SUGGEST` only after classification, clinical safety case, prospective evidence, and jurisdiction route clearance |

---

## 9. First Implementation Tickets

Create these tickets immediately. They are ordered so implementation can start without waiting for Wave 3 regulatory detail. Test-scope tickets are first-class implementation work; no feature ticket can close without linked canonical scenario rows and V-model evidence.

| Ticket | Title | Owner | Acceptance criteria |
|---|---|---|---|
| RL-TST-000 | Create HelixCare canonical test harness scaffold | CAID + BulletTrain QA | `tests/test_canonical_matrix_integrity.py`, `tests/harness/matrix_config.toml`, `tests/harness/requirements_matrix.json`, `tests/harness/canonical_matrices/`, `tests/harness/nfr_canonical_matrices/`, and `tests/harness/v_model/` exist and are discoverable by the CAID test agent |
| RL-TST-001 | Generate functional surface matrices | Surface owners + CAID | Eight V2 canonical matrices exist, each with exactly 100 unique realistic scenarios at 85/10/5 and trace links to SRS requirements, tickets, and V-model levels |
| RL-TST-002 | Generate shared component and NFR matrices | BulletTrain + CSAA + Security | Shared component and NFR matrices cover contracts, feature snapshots, reward log, OPE, policy registry, HITL, reward-hacking, privacy, monitoring, rollback, fairness, audit, latency, reliability, explainability, human oversight, safety, and regulatory traceability |
| RL-TST-003 | Add legacy 14-column compatibility sidecars where needed | BulletTrain QA | Existing 14-column harness consumers receive generated sidecars from V2 rows; CI proves sidecars match V2 scenario IDs, requirement IDs, ratio, and automation status |
| RL-TST-004 | Wire V-model execution suites to canonical scenarios | CAID + Implementation owners | Unit, integration, system, and acceptance suites select scenarios by canonical ID; CAID test-agent reports nonzero targets and hidden-failure validation is clean before Wave 1 shadow |
| RL-000 | Create `bullettrain.rl` module skeleton | BulletTrain | Package imports, CI target, README, owner map, and empty contracts compile |
| RL-001 | Define common RL event schemas | BulletTrain + CSAA | State/action/reward/policy/decision schemas versioned with JSON Schema and Python model tests |
| RL-002 | Add policy-card extension to GHARRA | GHARRA | Capability card stores policy version, evidence pack, intended use, activation scope, rollback pointer |
| RL-003 | Implement reward-log event writer | SignalBox | Signed append-only event includes state hash, action, reward source, propensity, policy version, actor |
| RL-004 | Implement deterministic feature snapshot API | BulletTrain + Bridge SDK | Replay for the same source event produces identical feature vector and lineage metadata |
| RL-005 | Implement OPE gate v1 | CSAA | IPS/SNIPS/DR metrics, bootstrap CI, overlap, ESS, subgroup report, machine-readable pass/fail |
| RL-006 | Wire HITL router to provider approval queue | Provider-Portal | Policy suggestions capture accept/reject/edit/override and emergency bypass |
| RL-007 | Build Prior-Auth state/action extractor | insurance-eclaims | Historical X12/FHIR cases convert into RL tuples with forbidden-action validation |
| RL-008 | Capture prior-auth baseline policy | insurance-eclaims | Current rules/human workflow is replayable as baseline comparator |
| RL-009 | Train prior-auth candidate bandit | BulletTrain RL | Offline model emits calibrated action scores and propensities; no forbidden actions |
| RL-010 | Build prior-auth shadow dashboard | Observability | Dashboard shows lift, delay, appeals, continuity risk, subgroup metrics, overrides, policy version |
| RL-011 | Draft prior-auth safety case addendum | CSAA | Delay-harm, equity, appealability, and rollback hazards logged with controls |
| RL-012 | Open Wave 2 data-readiness assessments | Surface owners | Scheduling, inbox, and adherence each have data availability, outcome delay, and consent/fairness gaps listed |
| RL-013 | Open Wave 3 classification assessments | Regulatory + CSAA | Pathway, triage, diagnosis, and resource allocation each have intended-use and jurisdiction route drafts |

---

## 10. Definition Of Done

### Phase 0 done

- `bullettrain.rl` schemas, feature snapshots, reward logs, policy registry, OPE gate, HITL routing, monitoring, and rollback path are implemented.
- A simulated policy can run from historical event to feature vector to action to reward log to OPE report to policy card.
- CSAA can freeze a policy from gate output or monitoring trigger.
- Reward logs are classified and protected as regulated data unless de-identification is formally approved.
- CAID discovers nonzero HelixCare RL canonical targets, all V2 matrices pass integrity and traceability checks, and any 14-column compatibility sidecars are regenerated from the V2 source.
- V-model unit and integration suites execute from canonical scenario IDs for every Phase 0 shared component.

### Wave 1 done

- Prior-auth runs in shadow for at least 4 weeks in 2-3 design-partner clinics.
- Evidence pack shows no forbidden actions, no delay-harm increase, no subgroup regression, and OPE lower CI >= baseline.
- HITL-live activation is limited to approved action classes.
- `helixcare-rl-reference-prior-auth.md` is published and becomes the pattern for Wave 2.
- The Prior-Auth canonical matrix, V-model system replay, HITL acceptance checks, shadow dashboard checks, and rollback tests all pass from the same scenario and requirement IDs.

### Wave 2 done

- Scheduling, inbox-triage, and adherence each complete data readiness, shadow, OPE, fairness, burden/delay, and rollback gates.
- Any clinical-message or medical-purpose subset is partitioned and held at clinical safety review until classified.
- Each Wave 2 surface has its own 100-scenario V2 matrix, NFR coverage, V-model system tests, and acceptance evidence before action-class promotion.

### Wave 3 done

- Each clinical surface has intended use, classification, hazard log, evidence plan, human factors plan, post-market monitoring plan, and regulator route decision.
- Clinical activation does not proceed from this plan alone.

---

## 11. Operating Cadence

| Cadence | Meeting | Purpose |
|---|---|---|
| Daily during Phase 0 | RL implementation standup | Blockers across BulletTrain, SignalBox, GHARRA, provider-portal, insurance-eclaims |
| Twice weekly | CSAA gate review | Review schemas, hazards, OPE assumptions, forbidden actions, and reward-hacking tests |
| Weekly during shadow | Evidence review | Baseline vs candidate, subgroup metrics, override analysis, incidents, rollback readiness |
| Per promotion | Policy change board | Approve policy card, evidence pack, activation scope, rollback plan, and monitoring thresholds |
| Monthly | Regulatory posture review | Refresh classification, guidance changes, PCCP/update-envelope assumptions, jurisdiction risks |

---

## 12. Risk Register

| Risk | Severity | Control |
|---|---|---|
| Prior-auth delay harm hidden by approval-rate lift | High | Continuity-delay penalty, urgent-case stratification, appeals review, subgroup turnaround monitoring |
| Poor historical support makes OPE unreliable | High | Overlap and ESS gates; unsupported segments route to HITL; collect shadow data before promotion |
| Reward hacking improves proxy but worsens real outcomes | High | Surface adversarial packs, secondary safety outcomes, delayed-outcome review, automatic freeze |
| Clinical surfaces misclassified as CDS | High | Intended-use review and CDS criteria evidence before any clinical activation |
| SPID reward logs treated as de-identified when linkable | High | Treat as regulated data; DPIA/BAA; access control; retention and re-identification controls |
| Implementation outpaces canonical test scope | High | RL-TST tickets run first; no feature ticket closes without V2 matrix rows, V-model evidence, and passing CAID discovery |
| Algorithm complexity outruns auditability | Medium | Start with constrained bandits / optimisation; require explainability and replay before advanced RL |
| Human reviewers rubber-stamp suggestions | Medium | Human-factors testing, override analytics, sampled case review, UI makes uncertainty and basis visible |
| Bias metric is too narrow | Medium | DIR plus subgroup performance, delays, false positives/negatives, overrides, opt-outs, and burden |
| Regulator queue delays Wave 3 | Medium | Start classification/evidence work during Wave 1; do not tie Wave 2 revenue proof to Wave 3 activation |

---

## 13. Required References

Engineering and governance should keep these references in the evidence folder for every policy pack:

- [FDA Clinical Decision Support Software FAQ](https://www.fda.gov/medical-devices/software-medical-device-samd/clinical-decision-support-software-frequently-asked-questions-faqs).
- [FDA Marketing Submission Recommendations for a Predetermined Change Control Plan for AI-Enabled Device Software Functions](https://www.fda.gov/regulatory-information/search-fda-guidance-documents/marketing-submission-recommendations-predetermined-change-control-plan-artificial-intelligence), final guidance, August 2025.
- [FDA Good Machine Learning Practice for Medical Device Development](https://www.fda.gov/medical-devices/software-medical-device-samd/good-machine-learning-practice-medical-device-development-guiding-principles) and [Transparency for Machine Learning-Enabled Medical Devices](https://www.fda.gov/medical-devices/software-medical-device-samd/transparency-machine-learning-enabled-medical-devices-guiding-principles).
- [MHRA AI Airlock collection](https://www.gov.uk/government/collections/ai-airlock-the-regulatory-sandbox-for-aiamd) and pilot learnings; use as regulatory engagement/sandbox context, not clearance shorthand.
- [NHS England DCB0129](https://digital.nhs.uk/data-and-information/information-standards/governance/latest-activity/standards-and-collections/dcb0129-clinical-risk-management-its-application-in-the-manufacture-of-health-it-systems/) and [DCB0160](https://digital.nhs.uk/data-and-information/information-standards/governance/latest-activity/standards-and-collections/dcb0160-clinical-risk-management-its-application-in-the-deployment-and-use-of-health-it-systems/) clinical risk management standards.
- [Regulation (EU) 2024/1689 (EU AI Act)](https://eur-lex.europa.eu/eli/reg/2024/1689/oj/eng), especially high-risk AI requirements, logging, transparency, human oversight, post-market monitoring, and Annex IV technical documentation.
- [European Commission MDCG guidance library](https://health.ec.europa.eu/medical-devices-sector/new-regulations/guidance-mdcg-endorsed-documents-and-other-guidance_en) for MDR / IVDR software classification guidance, including Rule 11 analysis where medical-purpose software is in scope.
- [HHS HIPAA de-identification guidance](https://www.hhs.gov/hipaa/for-professionals/privacy/special-topics/de-identification/index.html) for coded and pseudonymised health information.
- [NIST AI RMF 1.0](https://www.nist.gov/publications/artificial-intelligence-risk-management-framework-ai-rmf-10) for risk management vocabulary and trustworthy-AI controls.

---

## 14. Kickoff Decision

Proceed with implementation in this order:

1. Open RL-TST-000 through RL-TST-004 and RL-000 through RL-013.
2. Start the canonical test harness before closing any feature implementation ticket.
3. Start `bullettrain.rl` Phase 0 immediately.
4. Start Prior-Auth RL extraction in parallel with Phase 0 contracts.
5. Hold Wave 2 implementation until the common schemas, reward log, and matrix integrity gate are usable.
6. Start Wave 3 classification and data-readiness work now, but do not commit clinical activation dates until evidence and regulatory routes are accepted.

This is the final implementation baseline for commencing work. Any future change to algorithm class, reward shape, activation state, intended use, jurisdiction posture, or autonomy level is a policy change and must create a new signed policy-card version.
