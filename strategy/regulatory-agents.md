# Regulatory Posture for Multi-Agent Clinical Systems

Phase 3 deliverable for the Symphonix Health agent-first strategy. Companion to [agent-first.md](agent-first.md) §7 (four gates) and [governance-agents.md](governance-agents.md) (HITL / break-glass / freeze).

## Purpose

This document records the regulatory posture every Symphonix Health agent is held to, the jurisdictions in scope, and the mapping from a deployed agent's capability card to the regulatory framework its operator must answer to. It is **not** a legal opinion and it is **not** a substitute for a Notified Body, FDA 510(k) submission, or the equivalent in any jurisdiction — it is the internal contract that lets us evaluate a new agent consistently and brief regulators with a consistent story.

Operational rule of thumb: **if an agent advises a clinician who still decides, it is software; if an agent decides autonomously on a clinical question, it is a medical device.** The strategy deliberately anchors launch posture on the first side of that line.

## Scope

Applies to every Symphonix Health agent whose capability card declares `scope=internal` or `scope=cross_org` AND whose `healthcare.safety.decision_type` is one of the five levels in [governance-agents.md §1](governance-agents.md). Does not apply to:

- Deterministic rule engines, terminology servers, CDR / EHR storage components.
- UI kits, design-system components.
- Research code, offline analysis, ad-hoc notebooks.

## 1. The Five Jurisdictions in Scope

Ordered by regulatory tempo for the ecosystem's current geography. Each row is the scan; §2 onward is the detail.

| Jurisdiction | Regulator | Primary framework for agents | Tempo |
|---|---|---|---|
| United States | FDA | SaMD + Clinical Decision Support guidance | Frequent updates; PCCP-enabled |
| United Kingdom | MHRA | UKCA (post-Brexit) + AI airlock + DTAC (digital health) | Airlock active 2025– |
| European Union | EMA (med) / national competent authorities | MDR + AI Act (2024–2026 staged) | AI Act phased in |
| China | NMPA (med devices) + CAC (generative AI) | NMPA AI medical device guideline + interim GenAI measures | Active and distinct |
| Australia | TGA | TGA Software-Based Medical Devices guidance | Aligned to IMDRF |

Kenya, Nigeria, Rwanda, Ghana, and the wider African Medicines Agency (AMA) roll-up are explicitly **deferred to a country-annex** doc rather than absorbed here; the UHC implementations deliver the operational context for those jurisdictions and deserve their own treatment.

## 2. United States (FDA)

### 2.1 Posture

Agents at HITL-always with advisory output only, no patient-facing autonomous action, and no direct device control remain inside the FDA Clinical Decision Support (CDS) exclusion criteria set out in Section 520(o)(1)(E) of the FD&C Act and the 2022 CDS guidance. Specifically, four conditions must all hold:

1. The software does not acquire, process, or analyse medical images / signals / patterns (the reference agent does not — it operates over FHIR structural claim data).
2. The software's output is intended to support, not replace, clinical judgement.
3. The clinical basis of the recommendation can be independently reviewed by the clinician.
4. The clinician is able to, and is expected to, review the recommendation before action.

Mapping to the reference agent ([agent-eclaims-reference.md](agent-eclaims-reference.md)): condition 1 is satisfied by scope (administrative claims data, no imaging / signals). Condition 2 is satisfied by the "recommendation" action vocabulary — the agent never emits a verdict. Condition 3 is satisfied by the `cited_policies` and `rationale` fields being human-readable. Condition 4 is satisfied by the HITL-always launch posture.

### 2.2 What pushes an agent out of CDS exclusion

Any of the following transitions an agent into SaMD and requires pre-market pathway selection (510(k) / De Novo / PMA depending on classification):

- Autonomous clinical decisions (demotion from HITL-always to level 3+ in [governance-agents.md §1](governance-agents.md)).
- Processing of medical images, ECG signals, or time-series physiological data.
- Output that drives a device action (infusion rate, radiation dose).
- Claims of diagnostic performance, stratification, or risk prediction targeted at a disease state rather than a claims-administrative decision.

### 2.3 Predetermined Change Control Plans (PCCP)

For agents that do enter SaMD territory, the FDA's PCCP framework lets us pre-specify the model update envelope at submission time, avoiding a new 510(k) for every model refresh inside the envelope. A Symphonix Health PCCP must declare: the model-update cadence, the metrics that trigger a retrain, the performance bounds outside which a new submission is required, and the human-in-the-loop regressions that would force a pause. Every agent promoted past level 2 that touches FDA-scope decisions ships with a PCCP or a rationale for why one is not required.

### 2.4 Artefacts required per agent (US)

- Capability card with `regulatory_status.frameworks=["FDA CDS Exclusion"]` or `["SaMD"]` as appropriate.
- A CSAA classification record in the audit chain.
- Evidence of HITL-always launch posture (the reference agent's `decision_type=advisory` in the card).
- For SaMD: 510(k) decision summary or De Novo letter referenced from the card.

## 3. United Kingdom (MHRA)

### 3.1 Posture

Post-Brexit, medical-device software follows UKCA + the MHRA's AI-specific guidance. The MHRA **AI Airlock** (active since 2025) is the mechanism the strategy anticipates using for any agent that graduates past HITL-always with a clinical decision class — the airlock gives us a controlled real-world pilot with the regulator co-observing, in exchange for earlier feedback and a clearer post-market evidence plan.

### 3.2 DTAC (Digital Technology Assessment Criteria)

Any agent that lands inside an NHS England deployment also clears DTAC — clinical safety (DCB0129/DCB0160, which is the CSAA gate in [agent-first.md §7.1](agent-first.md)), data protection, technical security, interoperability, and usability. The [csaa](../../csaa) repo is precisely the gate that produces DTAC-compatible clinical-safety evidence; every agent is gated at build time by it per [governance-agents.md §1.1](governance-agents.md).

### 3.3 Artefacts required per agent (UK)

- DCB0129 hazard log (produced by [csaa](../../csaa)).
- DCB0160 deployment safety case for the first real NHS deployment.
- DTAC response pack.
- Airlock participation records (if applicable to the agent).

## 4. European Union (MDR + AI Act)

### 4.1 Posture

Two frameworks stack and both apply. MDR classifies software as a medical device against Rule 11; any software providing information used to take clinical decisions is at least Class IIa, and software for critical conditions or therapy / diagnostic monitoring is Class IIb or III. The AI Act is risk-based and orthogonal — **an AI-as-a-medical-device automatically sits in the AI Act "high-risk" bucket** (Article 6), which triggers conformity assessment, risk-management system, data-governance controls, technical documentation, human-oversight provisions, and post-market monitoring.

### 4.2 The AI Act's staged timeline

Key Symphonix Health-relevant milestones:

| Date | Obligation | Our action |
|---|---|---|
| 2025-02-02 | Prohibited-use categories in force | No Symphonix Health agent sits in a prohibited category; audit anyway |
| 2025-08-02 | GPAI (general-purpose AI) obligations on foundation-model providers | We consume foundation models; we are downstream, but we track provider conformity |
| 2026-08-02 | Full high-risk obligations apply to new high-risk systems | Every high-risk Symphonix Health agent must clear conformity assessment by this date |
| 2027-08-02 | Legacy high-risk systems must conform | N/A — no legacy systems in scope |

### 4.3 Artefacts required per agent (EU)

- MDR classification rationale (Rule 11 application).
- CE mark + Notified Body review if Class IIa or above.
- AI Act conformity assessment (high-risk).
- Risk-management system documentation (EN ISO 14971).
- Data-governance records per AI Act Article 10.
- Human-oversight arrangements (cross-references [governance-agents.md §1–2](governance-agents.md)).
- Post-market monitoring plan.

## 5. China (NMPA + CAC)

### 5.1 Posture

Medical-device software is classified and registered with NMPA. AI-specific guidance (NMPA 2022 "Guidelines for Registration and Review of Artificial Intelligence Medical Devices") governs software that incorporates AI/ML — requiring separate evidence on training-data governance, validation methodology, and continuous-improvement plans. In parallel, the CAC's Interim Measures for Generative AI (effective 2023-08-15) apply to any generative component, with obligations around content moderation, pre-release security review, and user protection.

### 5.2 Data residency

Data localisation is non-trivial in China. Training data, inference traces, and patient data must stay in-country, and cross-border data transfer requires a security assessment. Any Symphonix Health deployment that serves Chinese users lands on an in-country stack with isolated model weights and a local GHARRA federation peer — the [symphonix-bridge-sdk](../../symphonix-bridge-sdk) data-residency checks ([agent-first.md §1](agent-first.md)) are the mechanism that enforces this at request time.

### 5.3 Artefacts required per agent (CN)

- NMPA classification record.
- Training / validation / testing dataset documentation per NMPA 2022 guideline.
- CAC registration if generative component.
- Data-residency attestation from [symphonix-bridge-sdk](../../symphonix-bridge-sdk).

## 6. Australia (TGA)

### 6.1 Posture

The TGA's Software-Based Medical Devices (SBMD) framework, aligned to IMDRF SaMD guidance, classifies medical-device software across Class I (self-declaration) to Class III (pre-market approval). The TGA explicitly rolls in IMDRF's SaMD Risk Categorisation, so a Class IIa under MDR maps naturally to TGA Class IIa. An agent launched with the same posture as the reference agent sits at the lower end of that spectrum (administrative, advisory, HITL-always).

### 6.2 Artefacts required per agent (AU)

- TGA SBMD classification record.
- Essential Principles checklist.
- If relying on equivalence to a non-AU conformity (e.g., FDA 510(k) or CE mark), the equivalence rationale.

## 7. The Single Card-Driven Mapping

Every agent's regulatory posture is derivable from its capability card. This section is the map.

| Card field | What regulators read it as |
|---|---|
| `healthcare.safety.decision_type=advisory` + HITL-always | US CDS exclusion candidate; EU low-risk (probably Rule 11 Class I); UK DTAC non-device |
| `healthcare.safety.decision_type=threshold_autonomous` or above | US SaMD; EU AI Act high-risk; MHRA device; NMPA AI medical device; TGA SBMD |
| `healthcare.safety.break_glass_supported=true` | Requires documented override review in the safety case under every framework |
| `healthcare.safety.phi_egress=true` | Requires DPIA (UK/EU) and BAA (US); likely triggers CAC review (CN) |
| `healthcare.regulatory_status.classification="CDS"` or above | Mandates CSAA hazard log regardless of jurisdiction |
| `capabilities.autonomy=recommendation_only` | CDS-exclusion-compatible; requirements §1–6 per jurisdiction reduce |
| `capabilities.autonomy` level 3+ | Full device-track conformity assessment required per jurisdiction |

When a capability card is edited, the regulatory posture for that agent is recomputed. A change to `decision_type` is a regulatory change, not a config change — it opens a sub-bullet in the incident playbook.

## 8. The Symphonix Health Regulatory Ledger

For any agent in production, a single append-only ledger row records:

- `agent_uri` (GHARRA URI).
- `posture_snapshot_sha256` (hash of the capability card at posture evaluation time).
- Per jurisdiction: `framework`, `classification`, `evidence_artefact_uri`, `valid_from`, `valid_until`.
- Reviewer identity (CSO delegate) and signature.

The ledger is what a regulator sees when they ask "what is this agent classified as and who said so." It is populated automatically from the capability card plus the CSAA output; the human step is the CSO review signature.

## 9. What Triggers a Regulatory Re-Review

Called out so nothing slips through:

- Any change to `healthcare.safety.decision_type`, `healthcare.safety.break_glass_supported`, `healthcare.safety.phi_egress`, or `capabilities.autonomy`.
- Any [governance-agents.md §1.1](governance-agents.md) promotion past level 2 for a clinical decision class.
- Any [governance-agents.md §4](governance-agents.md) freeze that lasted > 30 days.
- Any model-version change that leaves the agent's PCCP envelope (US) or equivalent.
- Any data-residency scope change (jurisdiction added or removed).
- Any PHI-leak guardrail trip rate breach.

Re-review is a cross-functional action; it is not something the engineer who edited the card initiates alone. The CSO delegate owns the gate.

## 10. What This Document Is Not

Kept explicit to prevent scope creep:

- **Not a submission template.** Each jurisdiction has its own submission format; this document is what feeds every template, not any one of them.
- **Not a substitute for a regulatory consultant.** The strategy engages qualified counsel per jurisdiction before any submission; this document is the internal input to that engagement.
- **Not the clinical safety case.** That is [csaa](../../csaa) output. This document consumes CSAA classification; it does not replace CSAA.
- **Not the data-protection story.** DPIA / GDPR / HIPAA / PIPL mechanics live in a sibling document; this document references them but does not author them.

## 11. Enforcement at PR time

A new agent landing PR is not complete until every row below is either ticked or explicitly justified:

- [ ] Capability card has `healthcare.regulatory_status.frameworks` populated with at least one jurisdiction-appropriate framework string.
- [ ] Capability card has `healthcare.regulatory_status.classification` set (`administrative` / `CDS` / `SaMD` / `medical_device`).
- [ ] If classification is `CDS` or above, a CSAA hazard log exists.
- [ ] For first-time deployment in a jurisdiction, the regulatory-ledger row is populated.
- [ ] Re-review triggers (§9) are covered by the demotion monitor in [governance-agents.md §1.2](governance-agents.md).
- [ ] Card field changes that match §9 are called out in the PR description.

---

## Status

Draft — Phase 3 deliverable #2. Companion `governance-agents.md` is the runtime half of the posture; this document is the regulatory half. Country-annex docs (Kenya / Nigeria / Ghana / Rwanda) are deferred.
