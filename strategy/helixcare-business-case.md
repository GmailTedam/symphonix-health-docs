# HelixCare — Business Case and Demonstrable Value

**Status:** Strategy draft v0.1 — 2026-05-13
**Audience:** Founders, prospective investors, partner payers, Horizon 1000 programme leads, technical leadership at scaling private-care groups
**Sibling docs:** [agent-first.md](agent-first.md), [regulatory-agents.md](regulatory-agents.md), [governance-agents.md](governance-agents.md), [agent-eclaims-reference.md](agent-eclaims-reference.md), [helixcare-rl-implementation-plan.md](helixcare-rl-implementation-plan.md), [GHARRA Healthcare AI Agent Market Intelligence](../../health-agent-workspace/GHARRA_Healthcare_AI_Agent_Market_Intelligence.md), [symphonix-health-marketing.md](../marketing/symphonix-health-marketing.md)

---

## 1. Executive Summary

HelixCare is the **commercial product layer** on top of the Symphonix Health agent-first platform. It packages BulletTrain (integration hub), GHARRA (agent registry), Nexus A2A (agent coordination), CAID (orchestration), Prompt Engine (reasoning), SignalBox (attestation), CSAA (clinical safety), Bridge SDK (protocol translation) and the 26 sibling clinical apps into a single, multi-tenant cloud service that **any licensed clinician anywhere in the world** can subscribe to and run their practice from — as if they were operating inside a national health system.

The wedge is not feature count. The wedge is **architecture, auditability, and a reinforcement-learning policy stack** that earns measurable lifts on the metrics clinicians and payers actually pay for: waiting time, no-show rate, length of stay, readmission, prior-auth turnaround, claim denial rate, inbox burden, time-to-diagnosis, medication adherence.

Three commercial primitives:

1. **Monthly clinician subscriptions** — Starter $79, Professional $149, Enterprise $299 per clinician per month. Undercuts Epic Connect / athenaOne / Tebra / Practice Fusion / DrChrono by 30–60% on equivalent surface area, because the agent layer absorbs the work that would otherwise need staff seats and bolt-ons.
2. **Patient pay-as-you-go** at $15–$75 per encounter (global) and $1.50–$15 per encounter on the Africa wallet tier — competitive with Teladoc/Amwell at the top and with mTIBA-style micropay rails at the bottom.
3. **HelixCare Insurance Rails** — third-party insurance ingestion via the X12 270/271/837/835 surface already shipping in [insurance-eclaims](../../insurance-eclaims), plus a HelixCare-administered cover product for emerging markets priced at $3–$25 per member per month with risk re-pooled to licensed reinsurers.

Symphonix Health takes its fee on three axes — subscription, transaction (claim submission, micropayment), and outcome-share where payers will fund it. The unit economics target a 78–85% gross margin at steady-state because the agent layer compounds: each new tenant amortises the model and policy investment that earlier tenants paid for.

The competitive risk is not Epic. Epic will keep its hospital footprint. The risk is fast-following AI scribes (Abridge, Nuance DAX, Ambience) bundling into Epic / athenahealth and squeezing standalone agents out of US enterprise. HelixCare's answer is to **lead in three places EHR incumbents structurally cannot reach**: (a) the global long tail of solo and small-group clinicians outside US enterprise EHR coverage; (b) emerging markets where the EHR market never consolidated; (c) multi-agent interoperability between independent providers, which Epic cannot offer because Epic does not federate.

The next 12 months of go-to-market ship HelixCare Starter (solo clinicians, 6 jurisdictions), HelixCare Professional (small clinics), the RL scheduling and inbox-triage policies behind HITL, and the HelixCare Wallet on Paystack / Flutterwave / M-Pesa rails. The **build** velocity is sprint-week (Claude-Code-driven on top of the 26-sibling platform); the **calendar** is paced by external work — clinician credentialing per jurisdiction, PSP partnerships, regulator queues for Wave 3 clinical RL surfaces, and sales pipeline. Sequencing detail in [helixcare-rl-implementation-plan.md §8](helixcare-rl-implementation-plan.md). Target end of Year 1: 4,000 paying clinicians, 80,000 patient lives, $4–6M ARR, 88% gross margin on platform revenue, 32% blended including third-party PSP fees.

---

## 2. Product Definition

### 2.1 What HelixCare is

HelixCare is a **cloud-hosted, multi-tenant, multi-jurisdiction virtual hospital** delivered as SaaS. A licensed clinician signs up, completes credentialing, picks a jurisdiction tier, and from that point onward has:

- A clinician workstation — the existing [provider-portal](../../provider-portal) front-end (FastAPI + React 18, port 8700/5175), themed and rebranded as HelixCare Workstation, with full encounter management, e-prescribing, lab order, referral, and dual-chain audit ([provider-portal/README.md](../../provider-portal/README.md)).
- A patient-facing companion — [citizen-portal](../../citizen-portal) rebranded as HelixCare Patient, with timeline, consent, proxy access, GDPR/HIPAA SAR cascade, and pluggable subject term (`patient` vs `client` vs `service user`) via `CITIZEN_PORTAL_SUBJECT_TERM` ([project_citizen_portal_subject_term.md](../../.claude/projects/c--Users-hgeec-github/memory/project_citizen_portal_subject_term.md) in the operator's runtime memory).
- An acute / inpatient surface — [picis-system](../../picis-system) when the clinician operates a virtual ward, including ADT, ED, ICU, theatre flows and BCMA. For solo practitioners this surface is disabled.
- A pharmacy surface — [pharmacy-system](../../pharmacy-system) and [eps](../../eps) for e-prescribing.
- A laboratory surface — [lis](../../lis) for orders and results.
- An imaging surface — [pacs-ris](../../pacs-ris) for diagnostic imaging.
- An ambulance and transport surface — [ambulance-ems](../../ambulance-ems) where the clinician participates in mobile care.
- A claims and revenue surface — [insurance-eclaims](../../insurance-eclaims) with X12 270/271/837/835/278/277CA, bias audit, four-fifths-rule monitoring.
- A supply chain surface — [supply-chain-erp](../../supply-chain-erp) for inventory, cold chain, UDI traceability, where the clinician owns physical stock.
- A scheduling fabric — [scheduling-gateway](../../scheduling-gateway) plus [appointment-system](../../appointment-system) federated through GHARRA.
- A cross-border credential surface — BulletTrain's GDHCN service issues, verifies, and revokes COSE-signed vaccination, test, and recovery certificates interoperable with the WHO Global Digital Health Certification Network, the EU DCC, and ICAO VDS, so a HelixCare patient's credentials are verifiable across borders.
- A genomics, oncology, mental-health, maternity, screening, transfusion, mortuary and community-nursing set of sibling apps activated on demand.

All of this is **already running in the workspace**. HelixCare is not new software; it is the **commercial repackaging and the agent overlay** that turns the existing 26-sibling stack into a single product a clinician can buy.

### 2.2 What HelixCare is not

- Not an Epic replacement. Epic owns the US large-hospital tier. We do not chase it.
- Not a billing-only SaaS. The claims surface is included but is not the wedge.
- Not a telemedicine-only product. Telemedicine is one workflow inside a full virtual hospital.
- Not autonomous AI. Every clinical agent runs behind CSAA + GHARRA + Nexus A2A with HITL by default; autonomy is earned per metric per agent ([regulatory-agents.md](regulatory-agents.md)).
- Not an EHR feature-count race. Differentiation is architecture, auditability, and measurable RL-driven lift, not surface area.

### 2.3 The unit of value

A **HelixCare seat** is one credentialed clinician licensed to practise in at least one jurisdiction, with one or more patients on the platform, an integrated payment surface (insurance, wallet, or pay-as-you-go), and the full agent suite activated. The platform is priced per seat per month with usage overage on transactions (claims, micropayments, agent runs above tier cap).

---

## 3. The Clinician Value Proposition — Pain → Relief Mapping

Clinicians do not buy "AI." They buy specific pain relief. HelixCare maps to seven pain points named in [symphonix-health-marketing.md](../marketing/symphonix-health-marketing.md) and the literature, with the specific platform surface and target metric for each:

| Pain | HelixCare relief | Platform surface | Target metric |
|---|---|---|---|
| Documentation burden ("pyjama time") | Ambient scribe agent writing structured SOAP + ICD-10 + SNOMED to the encounter | [prompt-engine](../../prompt-engine) clauses on top of provider-portal | 60–75% documentation-time reduction; published Abridge / Nuance DAX studies and Ambience customer reports cluster in this range |
| Inbox volume | Inbox-triage RL agent (see §5.5) drafts, auto-resolves, routes | provider-portal inbox + Nexus A2A | 30–50% inbox-time reduction |
| Prior-auth friction | Prior-auth RL agent assembles documentation, predicts approval, queues peer-to-peer | insurance-eclaims + eps + payer connector | 40–60% turnaround compression; 30–50% denial reduction |
| Scheduling chaos / no-shows | Scheduling RL (see §5.1) optimises slot grid, overbooking, reminder cadence | scheduling-gateway + appointment-system | 12–22% no-show reduction; 15–30% wait-time reduction |
| Diagnostic uncertainty | Differential + next-test RL (see §5.7) with full guideline grounding | prompt-engine + signalbox attestation | 12–25% diagnostic-delay reduction |
| Pathway deviation / variability | Pathway-routing RL (see §5.2) inside evidence-based guidelines | [clinical-pathways](../../clinical-pathways) + BulletTrain | 8–15% length-of-stay reduction; 10–20% readmission reduction |
| Billing leakage | Coding agent + denial-manager agent + bias-audit guardrail | insurance-eclaims | 5–12% net collection lift; reduced disparate-impact ratio (DIR) variance |

Notice the target metrics are all bounded and grounded in published industry ranges. HelixCare does not claim breakthrough numbers; it claims that the **portfolio compounds** because the same patient signals power eight RL surfaces simultaneously, where standalone vendors run only one.

### 3.1 The "national system feel" globally

Clinicians outside the US/UK frequently say: "I want what the NHS or VA has — one patient identity, one inbox, one referral graph, one claim rail — but my country doesn't have it." HelixCare delivers this **per clinician** rather than per country. A clinician in Lagos using HelixCare gets:

- One **Symphonix Patient ID (SPID)** across every sibling app the clinician activates, with external aliases (NHS Number, Medicare Number, Ghana Card, national ID) treated as cross-references ([symphonix-bridge-sdk patient identity contract](../../symphonix-bridge-sdk/tests/harness/patient_identity/test_patient_identity_contract.py)).
- One **referral graph** — referrals to other HelixCare clinicians are first-class; referrals to non-HelixCare clinicians degrade gracefully to fax / printed letter.
- One **claim rail** — eclaims handles whichever payer the patient holds, including multi-payer split.
- One **medication record** — eps + pharmacy-system with cross-jurisdiction interaction checking.
- One **audit chain** — the dual-chain audit per citizen and per clinician means the patient owns their record and the clinician has defensible practice evidence.

This is the "national system globally" framing: the clinician gets the structural benefits of NHS-class integration without needing a country to build it for them.

---

## 4. The Patient Value Proposition

Patients on HelixCare get a portable, longitudinal, sovereign record across every clinician they see on the platform, payment optionality (insurance, wallet, pay-as-you-go), and the agentic virtual-hospital benefits — proactive medication reminders, symptom-check triage, pathway adherence nudges, second-opinion routing, and the right to subject-access, deletion, and proxy.

### 4.1 Insurance — like national insurance, globally

National insurance schemes have three properties patients value: predictable cost, broad coverage, low friction at point of care. HelixCare reproduces these three properties without a sovereign payer by:

- **Ingesting third-party cover.** Any insurer that speaks X12 270/271 (US), or that integrates via the insurance-eclaims payer connector (UK PMI, Africa private insurers, GCC mandatory schemes), is accepted. Patients add their card; eligibility is checked in real time via the existing 270/271 path.
- **Administering a HelixCare-branded scheme** in emerging markets where private insurance penetration is low. This is co-underwritten with a licensed local reinsurer; HelixCare is the administrator, not the risk-taker. Pricing is $3–25 PMPM (per member per month) by tier, comparable to Reliance Health and Helium Insure ranges. Risk pricing comes from the cohort claim history that eclaims already tracks.
- **Claim submission on the patient's behalf.** When the patient is seen, the clinician's encounter generates the claim; eclaims submits it; the patient sees one statement.

### 4.2 Pay-as-you-go

The pay-as-you-go path supports patients who don't have insurance or who want to see a clinician outside their network. The patient is charged per encounter, payment is taken via Stripe (developed markets) or Paystack / Flutterwave / M-Pesa (Africa) — patterns already proven in [africa-marketplace](../../africa-marketplace/VISION.md) — and Symphonix Health takes a transaction fee from the pass-through, never holding seller funds (PSP licensing requirements per Bank of Ghana and equivalents).

Per-encounter pricing bands:
- General practice video consult: $15–35
- Specialist video consult: $35–75
- Africa wallet tier (HelixCare Wallet): $1.50–$15 per encounter, MoMo-payable, with donor subsidy on top where Gates/Horizon 1000 funds flow.

### 4.3 The patient's right to leave

Patients can export their full record (FHIR Bundle) and revoke access at any time. This is not a marketing line; it is a GDPR Article 20 + HIPAA §164.524 requirement that the existing citizen-portal SAR cascade already implements. Critical for trust in jurisdictions where patients have been burned by data-locked EHR systems.

---

## 5. The Agentic Virtual Hospital — The RL Thesis

The core technical claim is that **reinforcement learning on the platform's accumulating signal corpus produces measurable, compounding lift across eight workflow surfaces** that clinicians and payers reward. This section names each surface, the formulation, the reward signal, the constraints (so it doesn't go rogue), and the target lift.

> **Companion document:** the sequencing, phase plan, build-vs-adopt table, and OPE-gate ownership for delivering these eight surfaces lives in [helixcare-rl-implementation-plan.md](helixcare-rl-implementation-plan.md). This section is *what and why*; that doc is *when and how*.

A note on caution. All RL in clinical workflows runs as **safe, off-policy, constrained, HITL-default** policies. We do not deploy RL that learns on-line from patient outcomes without an explicit clinical safety case approved through CSAA. The reward signals below are designed so that the worst-case policy is the existing rule-based baseline; RL only diverges when the off-policy evaluation (OPE) confidence interval clears a threshold.

### 5.1 Scheduling RL — wait time and no-show reduction

**State.** Slot grid for the next N days × clinician load × patient history (cancellation, no-show, lead time, demographic, distance, SDoH) × time of day × service type.

**Action.** Slot assignment, overbooking factor in [0, 0.3], reminder cadence and channel (SMS/voice/app/email), waitlist promotion.

**Reward.** `-wait_time_minutes − α·no_show_event + β·utilisation − γ·cancellation`. α tunable per clinic willingness-to-overbook; γ tunable per cancellation cost.

**Constraint.** Cannot violate clinician declared availability or stat off-time. Cannot exceed acuity-adjusted patient limit per session. HITL on novel overbooking ratios above clinic ceiling.

**Algorithm.** Contextual bandit (Thompson sampling) for reminder cadence; constrained DDPG or SAC for slot assignment; PPO with safety layer for full-policy.

**Surface.** [scheduling-gateway](../../scheduling-gateway) and [appointment-system](../../appointment-system).

**Target lift.** 12–22% no-show reduction, 15–30% wait-time reduction within 9 months of deployment per tenant. Published ranges from Olive AI, Notable, Phreesia, and academic studies (e.g. Daggy et al. on ML scheduling) cluster in this band; we anchor on the lower end to avoid over-promising.

### 5.2 Clinical pathway RL — length of stay and readmission

**State.** Patient FHIR record (conditions, observations, vitals, labs, imaging, meds, social, encounter history), current pathway node, comorbidities, SDoH, acuity score.

**Action.** Next pathway node within an evidence-based guideline DAG; referral; escalation to higher acuity; discharge readiness; follow-up cadence.

**Reward.** `outcome_at_discharge − λ·LOS_cost − μ·readmission_risk_30d + ν·adherence_score`. Outcome scored via standard pathway-specific endpoints (e.g. PROMs for orthopaedic pathways, time-to-undetectable for HIV, HbA1c trajectory for diabetes).

**Constraint.** Policy is constrained to **never propose a node outside the published guideline DAG**. The guideline is the safety layer. RL is allowed to reorder, time-shift, and personalise within the guideline, never to escape it. Clinician HITL on any node-skip.

**Algorithm.** Constrained Q-learning over discrete action space, with conservative-Q-learning (CQL) for offline training on historical pathway data. Doubly-robust OPE for deployment gating.

**Surface.** [clinical-pathways](../../clinical-pathways) and BulletTrain pathway services.

**Target lift.** 8–15% LOS reduction in inpatient cohorts; 10–20% 30-day readmission reduction. The clinical-pathway-routing literature in JAMA, NEJM AI, and the digital-health systematic reviews cluster in this band when the policy is constrained.

### 5.3 ED / virtual triage RL — door-to-doctor compression

**State.** Chief complaint NLP embedding, vitals, presenting time, demographic, prior visits, current ED load, available clinician roster.

**Action.** Triage category (Manchester Triage 1–5), queue priority within category, clinician routing (generalist vs specialty).

**Reward.** `-door_to_doc_minutes − ρ·mis_triage_event + σ·correct_severity_match`. Mis-triage is rare, expensive, and asymmetric — down-triage of a critical patient costs orders of magnitude more than up-triage of a non-acute. The reward is asymmetric on the loss side.

**Constraint.** Manchester Triage decision tree remains the floor — RL can promote within Manchester bands, never demote across them. HITL on any band-cross.

**Algorithm.** Asymmetric-loss DQN; PPO with safety layer for routing.

**Surface.** [triage-api](../../triage-api) and [ambulance-ems](../../ambulance-ems).

**Target lift.** 12–30% door-to-doc compression. Multiple ED RL papers report 15–30% (e.g. Lee et al., Wang et al.); we anchor at the low end.

### 5.4 Prior-auth RL — turnaround and approval rate

**State.** Claim line items, CPT/HCPCS codes, ICD-10, payer rules, denial history for similar lines, time-to-deadline.

**Action.** Documentation bundle assembly, peer-to-peer call request, appeal path selection, supplementary diagnostic request.

**Reward.** `approval_event − τ·cycle_time_days − υ·appeal_cost + φ·patient_outcome_continuity`.

**Constraint.** Cannot fabricate documentation. Every documentation element is sourced from existing chart with provenance signed via SignalBox. HITL on novel appeal paths.

**Algorithm.** Contextual bandit on documentation bundles; PPO on escalation strategy. Reward shaping via clinician feedback (RLHF-style) on novel cases.

**Surface.** [insurance-eclaims](../../insurance-eclaims) with the bias-audit and four-fifths-rule monitoring already shipping ([insurance-eclaims/docs/USE_CASES.md](../../insurance-eclaims/docs/USE_CASES.md) UC-EC-BIAS-001).

**Target lift.** 40–60% turnaround compression, 30–50% denial reduction on the lines the agent touches. Industry references (Cohere Health, Olive prior-auth, Availity studies) cluster in this band.

### 5.5 Inbox-triage RL — clinician burnout relief

**State.** Inbox item type (refill, lab follow-up, patient message, referral, payer query), sender, content embedding, clinician current workload, patient acuity.

**Action.** Auto-resolve (standard refill within protocol), draft reply for clinician one-click sign-off, route to staff, escalate to clinician, defer.

**Reward.** `clinician_time_saved_minutes − ψ·error_event − ω·patient_delay_minutes`.

**Constraint.** Auto-resolve only operates within explicitly clinician-approved protocols (e.g. "refill chronic hypertension med within parameters"). Everything else drafts for one-click sign-off. HITL is the default.

**Algorithm.** Contextual bandit for protocol classification; PPO for routing.

**Surface.** provider-portal inbox + Nexus A2A agent.

**Target lift.** 30–50% inbox-time reduction. Epic ambient + AthenaInbox studies cluster here.

### 5.6 Medication adherence RL — outcome and engagement

**State.** Adherence history per medication, comorbidities, SDoH, channel preference (SMS / voice / app / family proxy), prior nudge response, patient-stated preference.

**Action.** Nudge content (warm vs clinical vs caregiver-CC'd), channel, timing, intensity.

**Reward.** `dose_taken_event + δ·biomarker_improvement − ε·patient_opt_out − ζ·family_complaint`. Patient annoyance carries a hard negative; opt-out terminates the bandit.

**Constraint.** Patient consent required at enrolment; channel preferences honoured; no nudge during patient-declared quiet hours; opt-out is one tap.

**Algorithm.** Contextual bandit (LinUCB or NeuralUCB) suffices for most settings; reserve full RL for complex multi-medication regimens.

**Surface.** citizen-portal + pharmacy-system + eps.

**Target lift.** 15–30% adherence improvement on chronic-disease cohorts (hypertension, diabetes, HIV, TB, mental-health depot meds); 10–25% biomarker improvement on the responder subset. Wysa, Babylon (pre-collapse), Omada, Livongo published ranges support this band.

### 5.7 Diagnosis support RL — differential and next-test

**State.** Full patient context, current differential (with confidences), available tests with cost and turnaround, clinician's stated working hypothesis.

**Action.** Next-test recommendation, differential weight update, escalation suggestion.

**Reward.** `time_to_correct_diagnosis_inverse − η·unnecessary_test_cost + θ·outcome_at_resolution`. Correct diagnosis is established at adjudication time and feeds back into the reward.

**Constraint.** Always HITL — the agent never orders, only suggests. Diagnostic uncertainty is surfaced explicitly. The agent does not gate clinician judgement; it competes with it and the clinician can ignore. Every suggestion is attested via SignalBox so post-hoc review is honest.

**Algorithm.** Offline RL with conservative-Q on historical case data; reward model trained from adjudicated case outcomes.

**Surface.** prompt-engine clauses inside provider-portal; insurance-eclaims medical-necessity-advisor as the reference agent ([agent-eclaims-reference.md](agent-eclaims-reference.md)).

**Target lift.** 12–25% diagnostic-delay reduction on the cohort where the agent's confidence clears a threshold; non-inferior on the rest. Important framing: the agent does not change the outcome for the routine 70% of cases — it changes it for the 20–30% where uncertainty is high.

### 5.8 Resource allocation RL — virtual ward and cross-clinician load balancing

**State.** Ward load, acuity mix, staff fatigue (hours worked, alert frequency), predicted admissions next 4–12 hours, equipment availability.

**Action.** Bed assignment, staff shift mix, escalation triggers, cross-ward transfer recommendation, telemedicine offload for sub-acute.

**Reward.** `-overflow_event − ι·mortality_risk_increase + κ·staff_wellbeing_score`. Staff wellbeing is measured (with consent) through workload and self-report; not optional.

**Constraint.** Cannot exceed staff-to-patient ratios required by local regulation (e.g. RCN guidelines UK, ANA staffing ratios US). HITL on any cross-ward transfer.

**Algorithm.** PPO with safety layer; constraints encoded as CPO (Constrained Policy Optimisation).

**Surface.** picis-system and BulletTrain virtual-ward services.

**Target lift.** 8–18% bed-day savings; reduced overflow events.

### 5.9 The RL meta-architecture

All eight RL surfaces share infrastructure to make the platform investment compound rather than fragment:

- **Feature store.** FHIR-canonical via Bridge SDK. One feature set powers all eight policies.
- **Reward logging.** SignalBox attests every (state, action, reward) tuple with GHARRA-signed provenance, so every policy decision is auditable, replayable, and admissible as evidence in clinical-risk-management review.
- **Off-policy evaluation gate.** No policy is deployed without doubly-robust OPE meeting a pre-registered threshold per use case. The gate is owned by CSAA.
- **Reward-hacking guard.** Every reward function has a published shape and a published list of failure modes (e.g. "scheduling reward of -wait_time will not be reduced by lying about wait_time because reward signal comes from the patient timestamp, not the clinic clock"). The guard is reviewed quarterly.
- **HITL by default.** Autonomy is earned per metric per agent ([regulatory-agents.md](regulatory-agents.md) §PCCP).
- **Reward model from clinician feedback.** For surfaces where the reward is fuzzy (inbox-triage, diagnosis support), a RLHF-style reward model is trained on clinician feedback and audited for bias against the same demographics that the eclaims bias-audit already monitors.

This meta-architecture is HelixCare's deepest moat. Standalone vendors run one policy on one surface. HelixCare runs eight policies on one shared feature store, attestation chain, governance gate, and reward-model audit. The marginal cost of adding the ninth surface is small. The marginal cost for a competitor to reach this position is large.

---

## 6. Architecture — How HelixCare Composes the Existing Platform

HelixCare is the **commercial skin** on a stack that already runs. The composition map:

```
                      ┌──────────────────────────────────────────────┐
                      │            HelixCare Tenant Plane            │
                      │  (subscription, billing, jurisdiction, SLA)  │
                      └──────────────────────────────────────────────┘
                                          │
            ┌─────────────────────────────┼──────────────────────────────┐
            │                             │                              │
   ┌────────────────┐          ┌────────────────────┐         ┌────────────────────┐
   │  HelixCare     │          │   HelixCare        │         │   HelixCare        │
   │  Workstation   │          │   Patient          │         │   Wallet / Claims  │
   │  (clinician)   │          │   (patient)        │         │                    │
   │  provider-     │          │   citizen-portal   │         │   insurance-       │
   │  portal        │          │                    │         │   eclaims +        │
   └────────────────┘          └────────────────────┘         │   PSP rails        │
                                                              └────────────────────┘
                                          │
                      ┌──────────────────────────────────────────────┐
                      │         RL Policy Layer (§5)                 │
                      │  scheduling | pathway | triage | prior-auth  │
                      │  inbox | adherence | diagnosis | resourcing  │
                      └──────────────────────────────────────────────┘
                                          │
                      ┌──────────────────────────────────────────────┐
                      │         Agent Platform (existing)            │
                      │  GHARRA | Nexus A2A | CAID | Prompt Engine   │
                      │  SignalBox | CSAA | Bridge SDK               │
                      └──────────────────────────────────────────────┘
                                          │
                      ┌──────────────────────────────────────────────┐
                      │         BulletTrain Integration Hub          │
                      │     (API gateway, FHIR EventBus, audit)      │
                      └──────────────────────────────────────────────┘
                                          │
                      ┌──────────────────────────────────────────────┐
                      │     26 Sibling Clinical Apps (existing)      │
                      │  lis · pacs-ris · pharmacy-system · eps      │
                      │  gp-system · picis · ambulance-ems · etc.    │
                      └──────────────────────────────────────────────┘
```

The HelixCare Tenant Plane is **new**. Everything below is **existing**. The new code surface for a v1.0 HelixCare launch is therefore bounded: tenancy, jurisdictional licensing, billing, RL policy deployment infrastructure, the rebrand of provider-portal and citizen-portal, and the wallet rails. The 26 sibling apps and the agent platform do not need to be rebuilt.

This is the lever. The competitive cost-of-entry for a startup to reach this stack from scratch is well over $30M and 24+ months. The cost for HelixCare to commercialise it is in the low single-digit millions and the next 12 months.

### 6.1 Multi-tenant isolation

Each clinician (or clinic group) is a tenant. Tenants share the platform infrastructure but data is isolated at the row level (patient records, encounters, claims) and at the policy level (each tenant's RL policy can be either a global shared policy with tenant features as inputs, or a fine-tuned per-tenant policy on the shared base). For Tier 2/3 enterprise, dedicated infrastructure isolation is available as a price-up option.

### 6.2 Cross-tenant federation

Two HelixCare clinicians who share a patient (e.g. a GP refers to a cardiologist) federate through Nexus A2A using the standard A2A task lifecycle, with consent gated by the patient via citizen-portal. The patient sees one record across both clinicians. This is the property no current EHR delivers globally and it is the strongest "national system feel" lever.

---

## 7. Pricing Strategy

### 7.1 Competitive anchor (current market pricing, late-2025/early-2026)

| Vendor | Tier | Pricing band per clinician per month | Notes |
|---|---|---|---|
| Epic Connect (cloud-hosted small group) | small-group | $300–700 effective | Implementation $30K–$300K up front; minimum group size |
| athenahealth (athenaOne) | small to mid | $140–300 plus 4–7% of collections | Collection-share model |
| Tebra (Kareo + PatientPop) | small to mid | $150–300 + per e-claim fees | |
| DrChrono / EverHealth | small | $149–300 | Per-encounter billing module extra |
| Practice Fusion (Allscripts/Veradigm) | small | $149+ | Light EHR |
| Doctolib (EU) | small | €129–169 | Strong scheduling, weaker clinical |
| NextGen Mirth | mid | $300–400 | Multi-specialty |
| Helium Health (Africa) | small | $30–100 | EMR + light eclaims, light agents |
| Reliance Health (Nigeria) | member | $5–30 PMPM | Managed-care subscription, not clinician |
| Babylon (collapsed 2023) | member | £39 PMPM at peak | Reference, not competitor |
| Teladoc / Amwell | per encounter | $0–75 visit; $1–3 PEPM enterprise | Telemedicine only |

The pattern: standalone EHR for solo / small group sits at $140–300/clinician/month and requires bolt-ons (scribe, prior-auth, scheduling AI, patient app) that each cost another $50–250/clinician/month. **A realistic stack of EHR + scribe + prior-auth + patient app + scheduling AI costs $300–700/clinician/month in 2026.**

### 7.2 HelixCare price ladder

| Tier | Target | Price per clinician per month | Bundle |
|---|---|---|---|
| **Starter** | Solo clinicians, locums, low-volume independent practice | **$79** | Workstation; patient app; e-prescribing; scheduling RL; inbox-triage RL; ambient scribe; pay-as-you-go patient payments (Stripe / Paystack pass-through). Cap: 300 active patients, 200 encounters/month. |
| **Professional** | Clinics, small groups (2–25 clinicians) | **$149** | Everything in Starter plus: insurance-eclaims (X12 270/271/837/835), prior-auth RL, pathway RL, lab + pharmacy + imaging integration, multi-staff seats (3 admin staff included), supply-chain-erp light. Cap: 2,000 active patients, 1,500 encounters/month per clinician. |
| **Enterprise** | Hospitals, virtual wards, multi-site groups (25+ clinicians) | **$299** | Everything in Professional plus: picis acute surface, virtual-ward resourcing RL, diagnosis-support RL, multi-jurisdiction licensing, dedicated tenant isolation, SLA, dedicated CSO support, HelixCare Insurance Rails admin, cross-border health credentials (GDHCN-aligned, EU DCC + ICAO VDS interoperable). Uncapped. |
| **Africa Bronze (subsidised)** | Solo clinicians in Horizon 1000-aligned jurisdictions, Gates-funded programmes, faith-based clinics | **$9–19** | Workstation; patient wallet; scheduling RL; ambient scribe (multilingual); inbox-triage RL; pay-as-you-go via Paystack / Flutterwave / M-Pesa. Subsidy applied per donor agreement. |
| **Pay-as-you-go (clinician)** | Occasional locum, volunteer, post-disaster surge | **$2.50/encounter, no subscription** | Workstation + scribe + scheduling for the encounter only. |

Add-on, per tenant, all tiers:
- Additional admin staff seat: $19/month.
- Additional patient app vanity domain: $29/month.
- Premium reporting / outcomes dashboard: $49/month.
- Dedicated multi-region failover: $1,000/month flat.

Transaction fees (passes through PSP costs, takes Symphonix margin):
- Insurance claim submission (X12 837): **$0.50 per claim** (industry $1.50–$5).
- Patient micropayment: **2.9% + $0.30 PSP pass-through + 1% Symphonix platform fee** in developed markets; **3.5% + $0.10 PSP pass-through + 0.5% Symphonix platform fee** on Africa wallet.
- Eligibility check (X12 270/271): **$0.10 per check** (industry $0.30–$1).

### 7.3 Why this undercuts but is still high-margin

HelixCare can sit 40–60% under the equivalent stack price because:

1. **The agent layer absorbs work that would otherwise need staff seats.** A clinic that today pays for an EHR plus 2 admin FTEs ($60K–80K combined) replaces ~0.5–1 of those FTEs with HelixCare agent suite, freeing six figures of clinic budget. We capture a small fraction of that and we still feel cheap.
2. **The 26-sibling stack is already built.** We are not paying to build EHR / lab / pharmacy / imaging / scheduling / billing. We are paying to package and govern.
3. **Multi-tenant amortisation.** The cost to run one tenant is small. The cost to run 1,000 tenants on shared infrastructure is not 1,000×; it is closer to ~200×. Gross margin compounds.
4. **PSP pass-through with thin platform margin** keeps patient micropayments competitive with mTIBA / Reliance Health / standard Stripe checkout, so the patient never sees HelixCare as the expensive option.

### 7.4 Outcome-based pricing (Year 2+)

For payers and self-insured employers, HelixCare offers an **outcome-share** option: a fixed PMPM ($1–4) plus a share of measurable savings (avoidable admissions, prior-auth turnaround compression, denial reduction). This converts the sceptical-payer objection ("prove the savings before you bill me") into a contracted reward that aligns HelixCare's incentives with payer outcomes. The eclaims bias-audit infrastructure already gives the auditable evidence base.

---

## 8. Unit Economics

For one Professional-tier clinician at $149/month:

| Line | Value | Notes |
|---|---|---|
| Gross revenue per clinician per month | $149 | Subscription |
| + Transaction revenue | $25–60 | Average 50–120 claims/month at $0.50 plus eligibility checks |
| Total gross revenue per clinician per month | **$174–209** | |
| - Cloud hosting / compute | $11–14 | Multi-tenant amortised; spike on RL inference |
| - LLM inference (scribe, agent calls) | $9–15 | Cached embeddings, distilled models, hybrid local+cloud |
| - Support cost (allocated) | $5–8 | Tier 2 self-serve, ~5% of clinicians escalate per month |
| - PSP / banking pass-through | $0 | Patient micropayments — pass-through neutral |
| - Customer success allocated (Professional tier) | $4 | |
| Total marginal cost | **~$29–41** | |
| **Gross margin per clinician** | **$133–180** | |
| **Gross margin %** | **76–86%** | Steady-state |

Starter ($79) lands around 70–80% gross margin due to lower transaction revenue share. Enterprise ($299) lands at 80–88% because the fixed infrastructure is amortised over higher volume per tenant. Africa Bronze ($9–19) lands at 25–55% before donor subsidy and at 75%+ after donor subsidy (the subsidy is structured as platform-fee buy-down).

### 8.1 CAC and payback

Target blended CAC: $400–650 per Starter, $1,500–3,500 per Professional, $25,000–60,000 per Enterprise (concierge sale). Payback: ~6 months Starter, ~9 months Professional, ~12–14 months Enterprise. LTV / CAC target: >4× by month 24.

### 8.2 The compounding economics

The RL policies improve with data. The OPE-gated policy upgrade cycle delivers measurable lift quarterly. As lift compounds, churn drops (clinicians do not leave a platform that demonstrably reduces their inbox 50%, their no-shows 20%, and their claim-denial rate 35%). Net revenue retention is the metric that matters. Target: 115–125% by month 24.

---

## 9. Market Sizing

### 9.1 TAM

Global outpatient and ambulatory clinician population: ~12M doctors (WHO 2024 baseline), ~30M nurses, ~25M other licensed allied (pharmacists, midwives, paramedics, PAs, NPs). **Addressable seat-holder population: ~25–35M licensed clinicians globally**, of whom ~12–18M practise in settings where they can independently buy a SaaS tool (not employed by a single-vendor-locked hospital). At a blended $150 ARPU/month = $1.80K ARR per seat, the gross TAM is $22–32B ARR.

### 9.2 SAM

Filter to: clinicians (a) in jurisdictions where HelixCare can credential within 18 months (UK, Ireland, Ghana, Kenya, Nigeria, Rwanda, South Africa, US ambulatory, Canada, Australia, UAE, Saudi Arabia, Singapore, Malaysia, Philippines), (b) with payment rails available, (c) practising outside the deep-Epic-lock US health-system tier. **SAM ≈ 4–6M clinicians**, ≈ $7–11B ARR.

### 9.3 SOM (3-year)

Realistic Year-3 capture, with strong execution and Horizon 1000 leverage:
- Africa Bronze: 30K–60K clinicians at $12 blended ARPU = $4–9M ARR.
- Professional in Africa/SE Asia private markets: 8K–15K clinicians at $149 = $14–27M ARR.
- Professional + Enterprise in UK / EU / Canada / Australia / GCC: 12K–25K clinicians at $180 blended ARPU = $26–54M ARR.
- US ambulatory (selective; avoid Epic-lock tier): 5K–10K clinicians at $200 blended = $12–24M ARR.

**Year-3 ARR target band: $56–114M.** Aggressive but defensible given Horizon 1000 funding for emerging-markets capacity and the EHR-bundling squeeze pushing standalone agents out of US enterprise (creating a tailwind elsewhere).

---

## 10. Competitive Positioning

The competitive matrix is sliced by **segment-defensibility** rather than feature count.

| Segment | Incumbent | Why HelixCare wins | What we cede |
|---|---|---|---|
| US large hospital (Epic-locked) | Epic | We don't compete here. Cede. | The entire segment. |
| US ambulatory / solo / small-group | athenahealth, DrChrono, Tebra | 40–60% price; agent suite included; portable patient record; cross-clinician federation | Insurer relationships will take time to build for full US payer mix |
| UK NHS partner / NHS-adjacent | TPP SystmOne, EMIS Web (locked) | Cannot replace SystmOne/EMIS for GMS contract. Where HelixCare wins: NHS-adjacent (private GP, locums, occupational health, dental, pharmacy) and DSPT-compliant supplementary tooling | NHS GMS-contracted core EHR |
| EU private clinics | Doctolib, Compugroup | Multi-jurisdiction, multi-language, full clinical surface (not just scheduling); RL agent suite | Doctolib's France network effect is hard to dent |
| Africa private clinics | Helium Health, mTIBA-aligned partners | Stronger clinical surface, agent suite, multi-jurisdiction; Horizon 1000-aligned subsidy | Helium's local feet-on-the-ground sales |
| Africa public health (donor-funded) | Bespoke programmes (mostly Excel + Kobo) | First-class platform replacing brittle pipelines; donor-aligned pricing; multilingual triage | Long sales cycle to ministries |
| Telemedicine standalone | Teladoc, Amwell, Doctor on Demand | Full virtual hospital, not just video; integrated claim rail and lab/imaging | Their employer-channel sales |
| Mental-health standalone | Wysa, Woebot, Talkspace | Bundle mental-health within full virtual hospital, not standalone app; clinician-augmented | Brand familiarity in consumer DTC |
| Ambient scribe standalone | Abridge, Nuance DAX, Ambience | Bundle scribe within full platform; price subsidised by subscription; portable record | Their US enterprise contracts |
| Prior-auth standalone | Cohere, Olive (post-pivot) | Bundle within full clinical workflow, not standalone; multi-jurisdiction | Their established payer integrations |
| Agent interoperability | None (open gap) | GHARRA + Nexus A2A + Bridge SDK is the only production federated agent rail | — |

### 10.1 The agent interoperability moat

The deepest moat is **agent federation**. No competitor in the table above can federate their AI agents across organisational boundaries with auditable trust. Epic's AI is in-Epic. athenahealth's AI is in-athenahealth. Abridge's scribe runs inside whichever EHR ships it. **GHARRA + Nexus A2A is the only production-grade federated agent rail in the market**, and it is what makes "a patient's record follows them across HelixCare clinicians globally" work. This is also the most defensible architectural pillar against incumbents — they would have to fundamentally change their architecture to compete, and they have strong commercial reasons not to.

---

## 11. Regulatory Posture

Refer to [regulatory-agents.md](regulatory-agents.md) for the full operating model. HelixCare-specific summary:

- **US.** Each AI agent in the suite is positioned as **Clinical Decision Support (CDS)** under 21st Century Cures Act §520(o)(1)(E) where applicable. The reference agent ([agent-eclaims-reference.md](agent-eclaims-reference.md)) satisfies the four CDS exclusion conditions and serves as the template for the other seven RL surfaces. HIPAA / HITECH compliance is delivered through eclaims, provider-portal, and citizen-portal existing controls. SOC2 Type II target Year 1; HITRUST CSF target Year 2.
- **UK.** MHRA AI Airlock submission for each clinical-decision agent. DCB0129 + DCB0160 clinical safety case via [csaa](../../csaa); DTAC compliance for any NHS deployment.
- **EU.** EU AI Act 2024/1689 high-risk system classification for clinical agents with Annex IV technical documentation, conformity assessment via notified body. EU MDR 2017/745 SaMD pre-market submission where the agent makes autonomous diagnostic claims (initially none; HITL on all).
- **Africa.** Country-by-country health-data-regulation compliance (Ghana DPA 2012, Kenya DPA 2019, Nigeria NDPR 2019, South Africa POPIA, Rwanda DPP Law 2021). Telemedicine licensing per Medical and Dental Council of each jurisdiction.
- **GDPR / data sovereignty.** Regional data residency by default (EU clinicians' data in EU; Africa clinicians' data in Africa). Patient SAR + Article 15/20 cascade via citizen-portal.
- **WHO cross-border alignment.** The GDHCN credential surface is aligned with the WHO Global Digital Health Certification Network and interoperable with the EU DCC and ICAO VDS. Live participation in the WHO trust network is a per-jurisdiction onboarding step (submitting trust keys to WHO), not additional build — which makes cross-border credentials a credible sovereign/ministry sell rather than a roadmap promise.
- **EU AI Act algorithmic fairness.** Bias-audit and four-fifths-rule monitoring across age, sex, ethnicity, plan type, ZIP income — already shipping in [insurance-eclaims/docs/USE_CASES.md](../../insurance-eclaims/docs/USE_CASES.md) UC-EC-BIAS-001 — extended to scheduling, triage, and inbox-triage RL surfaces.

The strategic posture: **clinician-in-the-loop CDS exclusion as the launch position; SaMD pre-market only when a specific agent's autonomy is earned per the PCCP (Predetermined Change Control Plan)**. This is the right posture for time-to-market and is consistent with the agent-first strategy.

---

## 12. Go-to-Market Phases

> **Velocity note.** GTM phase windows below are **calendar-paced** because the binding work is external (credentialing, PSP partnerships, regulator queue, sales pipeline). The **build** inside each phase compresses to sprint-week granularity on the existing 26-sibling platform — see [helixcare-rl-implementation-plan.md §8](helixcare-rl-implementation-plan.md) for build-clock vs regulator-clock split.

### Phase 1 — Months 0–6 (Foundation)

- Ship HelixCare Starter to 6 jurisdictions: UK private practice, Ireland, Ghana, Kenya, Nigeria, Rwanda.
- Activate provider-portal + citizen-portal rebrand.
- Deploy scheduling RL and inbox-triage RL in shadow-mode (logging + OPE) on every tenant; activate decisioning where OPE clears threshold.
- Ship HelixCare Wallet on Paystack + Flutterwave + M-Pesa.
- Soft-launch Africa Bronze tier with two Horizon 1000-aligned programmes (faith-based clinic networks).
- Target: 800–1,200 paying clinicians, $0.8–1.5M ARR, 25K patient lives.

### Phase 2 — Months 6–12 (Scale to Professional)

- Ship HelixCare Professional with eclaims integration in same 6 jurisdictions.
- Activate prior-auth RL and pathway RL.
- Ship multi-clinician federation (cross-clinician patient record) — the "national system feel" demo.
- Begin SOC2 Type II evidence collection.
- Launch HelixCare Insurance Rails admin product co-underwritten in Kenya and Nigeria.
- Target: end-of-Year-1 at 4,000 paying clinicians, $4–6M ARR, 80K patient lives.

### Phase 3 — Months 12–18 (Enterprise + EU/AUS)

- Ship HelixCare Enterprise with picis integration and virtual-ward resourcing RL.
- Add jurisdictions: Australia, UAE, Saudi Arabia, Singapore, Malaysia.
- Begin MHRA AI Airlock submission for two clinical agents (medical-necessity-advisor and pathway-router).
- Begin EU AI Act conformity assessment with notified body.
- First outcome-share contract with a payer or self-insured employer.
- Target: 10K paying clinicians, $15–22M ARR.

### Phase 4 — Months 18–30 (US ambulatory + outcome share)

- Selective US ambulatory entry (states with friendlier telemedicine law: California, Texas, Florida, New York via clinician-side, not patient-side).
- Scale outcome-share contracts.
- HITRUST CSF certification.
- Target: end-of-Year-2 at 22–28K clinicians, $35–55M ARR; Year-3 at $56–114M.

---

## 13. Risks and Mitigations

| Risk | Likelihood | Severity | Mitigation |
|---|---|---|---|
| EHR incumbents bundle agent suite and cut prices | High | Medium | We don't fight incumbent EHR core; we serve adjacency and emerging markets. Differentiation is federation + auditability, not feature count. |
| Regulator declares an agent SaMD requiring pre-market | Medium | High | PCCP filed in advance; HITL by default so CDS exclusion applies. Pre-market filings already in plan for Phase 3. |
| Off-policy evaluation gates fail to clear; RL agents stay in shadow mode | Medium | Medium | The platform delivers value even without RL activation (ambient scribe, federated record, claims). RL is the upside, not the floor. |
| Africa payment-rail failure (PSP outage, regulatory change) | Medium | Medium | Multi-PSP architecture (Paystack + Flutterwave + M-Pesa from day one). Bank of Ghana / CBN / CBK licensing tracked. |
| Clinician credentialing fraud | Medium | High | Out-of-band verification with regulator API where available; doctor-ID by GMC / IMC / MDC; multi-factor; SignalBox-attested credential chain. |
| Patient data breach | Low | Catastrophic | AES-256-GCM at rest (existing); zero-trust between siblings; per-tenant key isolation for Enterprise tier; quarterly red-team. |
| Bias / disparate impact | Medium | High | Four-fifths-rule monitoring already shipping (eclaims), extended to every RL surface. CSAA gates every policy deployment. |
| RL reward hacking | Medium | Medium | Reward shapes published; quarterly review; SignalBox attests state→action→reward tuples so post-hoc audit is honest. |
| Capital intensity outpaces ARR | Medium | High | Africa Bronze subsidised by donor flow; outcome-share converts payer scepticism into contracted revenue; Enterprise concierge sales fund infra. |
| Churn from clinicians who don't see RL lift | Medium | Medium | Quarterly clinician-facing outcome scorecard; lift attribution honest; failure-to-deliver-lift triggers tier downgrade not churn. |
| Cross-jurisdiction data residency conflict | Low | High | Regional data planes (EU, Africa, MENA, APAC, NA) with brokered cross-region federation only via consented data flows. |

---

## 14. Demonstrable Value — KPI Scorecard

A clinician on HelixCare for 12 months is expected to demonstrate the following deltas against their pre-HelixCare baseline. Each is measurable from existing audit data:

| KPI | Pre-HelixCare baseline (industry average) | HelixCare target by month 12 | Delta |
|---|---|---|---|
| Documentation time per encounter | 14–20 min | 5–8 min | -60 to -75% |
| Inbox time per day | 90–150 min | 45–75 min | -30 to -50% |
| No-show rate | 12–18% | 9–14% | -12 to -22% |
| Patient wait time (in clinic + telemed) | 28–45 min | 20–32 min | -15 to -30% |
| Length of stay (inpatient cohort, where applicable) | baseline | -8 to -15% | |
| 30-day readmission (chronic cohorts) | baseline | -10 to -20% | |
| Door-to-doctor (ED / urgent care) | baseline | -12 to -30% | |
| Prior-auth turnaround | 4–9 days | 1.5–4 days | -40 to -60% |
| Claim denial rate | 11–18% | 7–13% | -30 to -50% |
| Net collection ratio | baseline | +5 to +12% | |
| Time to diagnosis (uncertain-cohort subset) | baseline | -12 to -25% | |
| Medication adherence (chronic cohorts) | 50–60% PDC | 60–75% PDC | +15 to +30% |
| Clinician self-reported burden (Maslach abbreviated) | baseline | meaningful reduction at month 6 and 12 | |
| Patient NPS | baseline | +20 points by month 12 | |

The scorecard is delivered to every tenant quarterly and is the basis for tier-progression conversations and outcome-share contracts.

---

## 15. The One-Paragraph Summary

HelixCare is a cloud-hosted, multi-tenant virtual hospital that gives any licensed clinician globally the structural benefits of practising inside a national health system — one patient identity, one referral graph, one claim rail, one medication record, one audit chain — augmented by an eight-surface reinforcement-learning policy stack that delivers measurable lift on the metrics clinicians and payers actually reward. Priced 40–60% under the equivalent EHR-plus-bolt-on stack at $79 / $149 / $299 per clinician per month with $9–19 Africa subsidised tier and $2.50 pay-as-you-go, patient pay-as-you-go from $1.50 to $75 per encounter, and a HelixCare Insurance Rails admin product co-underwritten in emerging markets. The 26-sibling clinical platform is already built; HelixCare is the commercial skin, the tenancy plane, the RL policy layer, and the wallet rails. Year-1 target: 4,000 clinicians, $4–6M ARR. Year-3 target: $56–114M ARR. The moat is agent federation, which incumbents structurally cannot match without rewriting their stacks.

---

## Appendix A — Mapping HelixCare features to existing repos

| HelixCare feature | Existing repo | Status |
|---|---|---|
| Clinician workstation | [provider-portal](../../provider-portal) | Production-shape |
| Patient app | [citizen-portal](../../citizen-portal) | Production-shape |
| Inpatient / virtual ward | [picis-system](../../picis-system) | Working |
| E-prescribing | [eps](../../eps) | Working |
| Pharmacy | [pharmacy-system](../../pharmacy-system) | Working |
| Laboratory | [lis](../../lis) | Working |
| Imaging | [pacs-ris](../../pacs-ris) | Working |
| Ambulance / EMS | [ambulance-ems](../../ambulance-ems) | Working |
| Claims and EDI | [insurance-eclaims](../../insurance-eclaims) | Production-shape with bias audit |
| Supply chain | [supply-chain-erp](../../supply-chain-erp) | Working |
| Scheduling fabric | [scheduling-gateway](../../scheduling-gateway), [appointment-system](../../appointment-system) | Working |
| GP encounter | [gp-system](../../gp-system) | Working |
| Maternity, screening, oncology, etc. | [maternity-system](../../maternity-system), [screening-recall](../../screening-recall), [cancer-pathway-tracker](../../cancer-pathway-tracker), etc. | On-demand activation |
| Agent registry | [global-agent-registry](../../global-agent-registry) | Production |
| Agent coordination | [nexus-a2a-protocol](../../nexus-a2a-protocol) | Production |
| Orchestration | [caid-agent](../../caid-agent) | Production |
| Reasoning DSL | [prompt-engine](../../prompt-engine) | Production |
| Attestation | [signalbox-mcp](../../signalbox-mcp) | Production |
| Protocol translation | [symphonix-bridge-sdk](../../symphonix-bridge-sdk) | Production |
| Clinical safety | [csaa](../../csaa) | Production |
| Integration hub | [BulletTrain](../../BulletTrain) | Production |
| Cross-border health certificates | [BulletTrain](../../BulletTrain) GDHCN service | Production-shape |
| Emulator | [symphonix-emulator-kit](../../symphonix-emulator-kit) | Production |

New work for HelixCare v1.0 launch (Phase 1):
1. HelixCare Tenant Plane — tenancy, jurisdiction, licensing, billing, subscription lifecycle.
2. HelixCare brand layer on provider-portal and citizen-portal.
3. Wallet integration on PSP rails.
4. RL policy deployment pipeline + OPE gate operationalisation.
5. Clinician credentialing service.
6. Outcome scorecard generator.

Everything else exists.

---

## Appendix B — What this document deliberately does not contain

- Financial projections beyond ARR bands. A separate financial model lives outside this strategy doc.
- Detailed implementation plans per repo. Those live in each repo's own roadmap.
- A pitch deck. A 12–14 slide deck derived from this document is the right next artefact for fundraising conversations.
- Investor cap-table implications. Out of scope.
- Detailed RL algorithm choice per surface. The choices in §5 are starting points; final selection is per-tenant data-driven.

---

*End of business case v0.1. Next revision triggers: (a) first paying tenant invoice issued, (b) first RL policy clearing OPE deployment gate, (c) first outcome-share contract signed, (d) first MHRA AI Airlock submission accepted. Each of those events warrants a v0.2 update against the assumptions in §7–9.*
