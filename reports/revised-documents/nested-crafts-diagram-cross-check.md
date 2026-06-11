# Nested CRAFTS diagram cross-check

Source diagram: `C:\Users\hgeec\Downloads\Nested CRAFTS Agentic intelligence architeture.png`

Date: 2026-06-11

## Verdict

The diagram is directionally correct, but it over-compresses several implementation surfaces. The biggest omissions are the sibling-system ring and the human/AI agent capability framework. The persona and superpersona layer should not be shown as metadata alone: it is the framework through which human agents and AI agents receive skills, tools, clinical frameworks, authority, safety constraints, evidence requirements, and outcome targets. Pharmacy, clinical pathways, ambulance/EMS, insurance eclaims, ERP, supply-chain ERP, HMIS, provider portal, citizen portal, appointment system, genomics interpretation, and Patient360 are not visible even though they are where many clinical and operational capabilities execute. The diagram should show these as domain systems connected through BulletTrain, Bridge SDK, Nexus A2A, GHARRA, SignalBox, Prompt Engine, and CSAA.

The diagram should also add:

- A visible `Human and AI agent capability framework` band in the platform fabric, covering persona, superpersona, skills, tools, clinical frameworks, authority scope, safety, evidence, and outcome binding.
- `Bounded rationality` as an essence-critical problem domain.
- `Innovation and invention` as strategic outcomes.
- A labeled `learning and improvement loop` spanning the think loop, action loop, SignalBox/CAID evidence, Prompt Engine optimization, CSAA risk updates, and superpersona contract evolution.
- Correct naming: `Symphonix-Health mechanism core`, not `Symphonix mechanism core`.
- A clear distinction between the `Symphonix platform fabric` product family and `Symphonix-Health` as the healthcare mechanism.

## Layer audit

| Diagram layer | Documented | Implemented | Tested | Audit note |
|---|---:|---:|---:|---|
| 1. CRAFTS context and trigger conditions | PASS | N/A | N/A | CRAFTS is an analytic framing layer, not a runtime subsystem. It should be documented as context/trigger/mechanism analysis, not implemented code. |
| 2. Enabling substrate | PASS | PARTIAL | PARTIAL | Power/compute is better named `resource governance`; Bridge SDK implements per-persona/per-patient execution budgets and Prompt Engine/Bevan route model work through governed gateways. Estate-level compute ownership is not evidenced. |
| 3. Symphonix platform fabric | PASS | PASS | PARTIAL | BulletTrain, GHARRA, Nexus A2A, Bridge SDK, Prompt Engine/Bevan, and governance services are documented and implemented. Cross-sibling test gates are mixed. |
| 3a. Sibling/domain systems | PARTIAL | PASS | FAIL/PARTIAL | The sibling systems exist and many have tests, but the prior revised report did not make them visible enough. Several canonical matrix checks currently fail with requirement-ID drift. |
| 3b. Human and AI agent capability framework | PARTIAL | PASS | PARTIAL | GHARRA implements human/clinical persona definitions and registry; Nexus implements agent/IAM routing; Bridge SDK implements `SuperpersonaContract`, `skill_pack`, `tool_pack`, framework selection, route salience, runtime budgets, and exports. Diagram visibility and cross-sibling consumption remain partial. |
| 4. AI capability stack | PASS | PARTIAL | PARTIAL | Retrieval, clinical prompt assembly, coordination, context assembly, and governed tool use are implemented in pieces. "Networked superhuman clinical intelligence" remains a bounded thesis/outcome claim, not a single executable service. |
| 5. Think loop and action loop | PARTIAL | PARTIAL | PARTIAL | SignalBox implements a perception-action loop; CAID implements strategy selection, reflection, structured memory, and learning-loop taxonomy; Prompt Engine supports planning/reflection scaffolding. There is no single end-to-end clinical learning service yet. |
| 6. Symphonix-Health mechanism core | PASS | PASS | PARTIAL | Context integration, trust discovery, delegation/coordination, reasoning/planning, guardrails/safety, and workflow execution are implemented across repos. Learning/reflection is implemented in adjacent evidence systems but not fully closed across all clinical outcomes. |
| 7. Essence-critical problem domains | PARTIAL | PARTIAL | PARTIAL | Navigation/triage, care planning, summarization, claims friction, and longitudinal context are represented. Add bounded rationality as a distinct critical problem. |
| 8. Outcomes | PASS | PARTIAL | PARTIAL | Immediate/service outcomes are implemented as outputs and workflow evidence. Strategic outcomes should add innovation and invention, but those are outcome claims that need metrics/evidence, not just diagram text. |
| 9. Design principles | PASS | N/A | PARTIAL | The four principles are architecture/design governance. They are not runtime code, but they can be tested indirectly through CSAA, SignalBox, CAID, accessibility, real-service, and evidence gates. |

## Sibling-system ring

The diagram should add a visible sibling/domain-system band below or beside the Bridge SDK/integration services box:

| Sibling system | Function in the complete diagram | Evidence |
|---|---|---|
| `pharmacy-system` | MedicationRequest intake, dispensing, labeling, nomination, pharmacy claims handoff. | README lines 31-87 describe provider portal -> BulletTrain HIE -> pharmacy-system and API routes; test/matrix files are present, but current matrix gate fails. |
| `clinical-pathways` | NICE/NHS/WHO pathway execution, FHIR ServiceRequest emission, BridgeClient dispatch to appointment and A2A agents. | README lines 10-24 and 58-71 describe Bridge SDK and FHIR dispatch; selected tests passed (`8 passed`). |
| `ambulance-ems` | Triage/dispatch, emergency-read flow, EMS console, provider portal handoff. | README lines 31-70 describe BulletTrain HIE and dispatch architecture; current matrix gate fails. |
| `insurance-eclaims` | X12 837/835 claims, payer adjudication, claim lifecycle, bias audit and PHI guard. | README lines 31-93 describe eclaims architecture and APIs; current matrix gate fails. |
| `erp` | Finance, inventory, HR/payroll, procurement, pharmacy/eclaims/provider-portal feed consolidation. | README lines 8-103 describe integrated ERP and BulletTrain matrix posture; current matrix gate fails. |
| `supply-chain-erp` | Purchasing, stock allocation, cold-chain, UDI traceability, 3PL/vendor webhooks. | README lines 25-125 describe architecture and tests; current matrix gate fails. |
| `HMIS` | Facility registry, indicator reporting, FHIR MeasureReport publishing, organizational reporting. | README lines 29-84 describe features, BulletTrain registration, and tests; current matrix gate fails. |
| `provider-portal` | Clinician-facing portal, auth/MFA, audit chain, BulletTrain client, clinical UI. | README lines 31-110 describe docs, stack, tests, BulletTrain mode, and audit model; current matrix gate fails. |
| `citizen-portal` | Patient/carer access portal, screening opt-out, cross-system audit aggregation. | README lines 16-35 describe BulletTrain/cascade and matrix posture; current matrix gate fails. |
| `appointment-system` | Scheduling, slots, waitlist, FHIR Appointment, GHARRA/Nexus/BulletTrain integration. | README lines 31-68 describe GHARRA, Nexus JSON-RPC, HAPI FHIR, and seed data; current canonical matrix count gate fails. |
| `genomics-interpretation` | Genomic interpretation, ACMG/AMP, CPIC, report drafting, cascade testing, Caldicott/DPO gates. | README lines 1-62 describe capabilities, personas, integration, standards, and testing; selected tests passed (`23 passed`). |
| `patient360-assistant` | Longitudinal patient context, assistant workflow, governance and persona-aware patient journey surface. | Tests and matrices exist; covered in the revised reports as the longitudinal/context surface. |

## Human and AI agent capability framework

The diagram should not leave persona, skills, tools, and frameworks implicit inside "memory, prompt, and tool services." This should be a visible control band between the platform fabric and the AI capability stack. It should show human agents and AI agents as governed actors whose capabilities are defined by persona/superpersona contracts, skill packs, tool packs, clinical frameworks, authority, safety, and outcome obligations.

| Framework element | Repo-backed implementation | Test/evidence status |
|---|---|---|
| Human agent personas | GHARRA `PersonaRegistry` and `PersonaDefinition` define role keys, labels, categories, summaries, toolsets, SOPs, domains, FHIR role codes, and avatar variants. | Documented and implemented; specialty completeness still needs a generated inventory. |
| AI agent and superpersona contracts | Nexus represents route-admitted agents and IAM groups; Bridge SDK `SuperpersonaContract` binds persona identity to skill packs, tool bindings, IAM scopes, safety posture, eval evidence, route salience, intuition decision, and runtime budget policy. | Direct Bridge SDK tests passed in `tests/test_superpersona_contract.py`; cross-sibling adoption remains partial. |
| Skills framework | Skill packs are represented through persona toolsets/SOPs in GHARRA and `skill_pack` fields in Bridge SDK superpersona contracts. These should map to clinical and operational roles, not generic AI capabilities. | Partly tested through Bridge SDK contract tests; needs generated skill-pack catalog across siblings. |
| Tools framework | Tool policy is represented through Bridge SDK capabilities, MCP tool policy exports, A2A card extension, and sibling route/tool authorization. | Bridge SDK tests verify GHARRA, A2A, MCP, audit, SignalBox, high-risk, and validation behavior; sibling route tests are not all clean. |
| Clinical and operational frameworks | Framework selection is represented through SOPs, safety classes, `IntuitionDecision`/route salience, prompt policy, and domain systems such as clinical pathways, pharmacy, claims, EMS, and genomics. | Implemented in pieces; needs explicit framework-pack fields and cross-sibling tests before it can be claimed as complete. |
| Outcome binding | The framework should connect each human/AI agent capability to immediate outputs, service outcomes, strategic outcomes, and innovation/invention evidence. | Not fully implemented as a single gate; should become part of the superpersona contract and SignalBox/CAID evidence pack. |

## Direct tests run in this audit

These tests were executed locally after the diagram cross-check. They are representative direct evidence, not a full CI replacement.

| Repo | Command | Result |
|---|---|---|
| `symphonix-bridge-sdk` | `python -m pytest tests/test_superpersona_contract.py tests/test_concurrency.py -q` | PASS: 23 passed |
| `prompt-engine` | `python -m pytest tests/test_inference.py tests/test_engine.py -q` | PASS: 112 passed |
| `csaa` | `python -m pytest tests/test_hazards_risk.py tests/test_cli.py -q` | PASS: 26 passed |
| `caid-agent` | `python -m pytest tests/test_advisory_taxonomy.py tests/test_strategies.py tests/test_structured_memory.py -q` | PASS: 100 passed |
| `clinical-pathways` | `python -m pytest tests/test_executor.py tests/test_dedup.py -q` | PASS: 8 passed |
| `genomics-interpretation` | `python -m pytest tests/test_health.py tests/test_vrs.py -q` | PASS: 23 passed |
| `pharmacy-system` | `python -m pytest tests/test_bullettrain_v1_matrix.py tests/test_canonical_matrix_integrity.py -q -x` | FAIL: reduced matrix requirement IDs omit `FR-BA-112-AC01` |
| `ambulance-ems` | `python -m pytest tests/test_bullettrain_v1_matrix.py tests/test_canonical_matrix_integrity.py -q -x` | FAIL: source has `FR-BA-100-AC01`, projection has `FR-BA-100` |
| `insurance-eclaims` | `python -m pytest tests/test_bullettrain_v1_matrix.py -q -x` | FAIL: source has `NFR-EC-BIAS-001-AC01..AC03`, projection has `NFR-EC-BIAS-001` |
| `provider-portal` | `python -m pytest tests/test_bullettrain_v1_matrix.py tests/test_canonical_matrix_integrity.py -q -x` | FAIL: projection adds `L-342` not present in source row |
| `appointment-system` | `python -m pytest tests/test_bullettrain_v1_matrix.py tests/test_canonical_matrix_integrity.py -q -x` | FAIL: `requirements_matrix.metadata.requirement_count` differs from superset count |

The other CAID-generated sibling repos in the lightweight loop also failed the same family of matrix/count gates: `erp`, `supply-chain-erp`, `HMIS`, and `citizen-portal`. Their application code and test files are present, but the current traceability gate is not clean.

## Required diagram/document updates

1. Rename layer 6 to `Symphonix-Health mechanism core`.
2. Keep layer 3 as `Symphonix platform fabric` if it is meant to name the product/platform fabric, but add text that the healthcare mechanism is `Symphonix-Health`.
3. Add a visible `Human and AI agent capability framework` band inside the platform fabric or immediately below it, showing persona, superpersona, skills, tools, clinical frameworks, authority, safety, evidence, and outcome binding.
4. Add the sibling/domain-system ring and route it through BulletTrain, Bridge SDK, Nexus A2A, and GHARRA, not direct peer-to-peer mutation.
5. Add `Bounded rationality` under essence-critical problem domains.
6. Add `Innovation and invention` under strategic outcomes.
7. Add a labelled `Learning and improvement loop` that includes think loop, action loop, SignalBox evidence capture, CAID reflection/structured memory, Prompt Engine optimization, CSAA risk-case updates, and superpersona contract updates.
8. Mark the sibling matrix drift as an active test gap until the reduced matrices are regenerated or corrected against their source rows.

## Evidence notes

- Bridge SDK now implements a superpersona contract shape in `src/bridge_sdk/superpersona_contract.py`, including skill packs, tool bindings, IAM scopes, safety posture, eval evidence, intuition decision, runtime budget policy, GHARRA/A2A/MCP exports, and audit export. Its tests verify GHARRA, A2A, MCP, audit, SignalBox, high-risk, and validation behavior. The diagram still needs to present this as a human/AI agent capability framework that enables outcomes, not as a hidden implementation detail.
- The think/action loop is implemented across components rather than as one service: SignalBox handles browser perception-action; CAID handles strategy/reflection/memory; Prompt Engine handles prompt-level planning/reflection and clinical/PHI inference; CSAA handles safety-case gating.
- Do not claim all sibling systems are fully tested until the failing matrix gates are repaired and rerun.
