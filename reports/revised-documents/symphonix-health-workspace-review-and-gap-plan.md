# Symphonix-Health workspace review and gap plan

Date: 2026-06-11

Scope: owned repositories under `C:\Users\hgeec\github`, excluding forked repositories and duplicate worktrees.

## Executive finding

The revised architecture is credible, but the workspace cannot yet support a complete implementation claim. The core platform services exist, the human/AI agent capability framework is implemented in important pieces, and the sibling-system estate is broad enough to support the diagram. The open failures are traceability drift, incomplete conformance testing, missing architecture documents in many sibling repos, and the absence of a single gated evidence loop proving that real outcomes update the platform safely.

The diagram and documents should therefore present Symphonix-Health as a governed target architecture with strong implemented foundations and an explicit closure plan.

## Review scope

Excluded forked repositories:

- `.github`
- `airllm`
- `claw-code-parity`
- `Liquid4Allcookbook`
- `LivePortrait`
- `MuseTalk`
- `openclaw`
- `piper`

Excluded duplicate or auxiliary worktrees:

- `_bt_hardening_wt`
- `_bt_shr_fix_1780935930`

Reviewed owned repositories:

`africa-marketplace`, `agent-skills`, `ambulance-ems`, `analytics-bi`, `appointment-system`, `blood-transfusion`, `BulletTrain`, `caid-agent`, `cancer-pathway-tracker`, `citizen-portal`, `clinical-pathways`, `community-nursing`, `csaa`, `design-system`, `elocute`, `epaccs`, `eps`, `erp`, `etps`, `genomics-interpretation`, `global-agent-registry`, `gp-system`, `health-agent-workspace`, `healthcare-pain-points-plan`, `HMIS`, `insurance-eclaims`, `kenya-uhc-implementation`, `lis`, `maternity-system`, `mha-administration`, `mortuary-and-me`, `nexus-a2a-protocol`, `pacs-ris`, `patient360-assistant`, `pharmacy-system`, `picis-system`, `prompt-engine`, `provider-portal`, `REA-Agent-mcp`, `scheduling-gateway`, `screening-recall`, `second-brain-kb`, `signalbox-mcp`, `supply-chain-erp`, `symphonix-bridge-sdk`, `symphonix-email-action-worker`, `symphonix-eps-ig`, `symphonix-health.github.io`, `symphonix-health-docs`, `symphonix-public`, `tool-library`, `triage-api`, `workspace-tooling`.

## Review method

The review used:

- repository inventory and remote-origin classification to exclude forks;
- architecture, README, requirements, matrix, and evidence file discovery;
- direct code evidence from core platform repos;
- representative component tests;
- a workspace-wide lightweight matrix/integrity gate using repo-local `test_bullettrain_v1_matrix.py` and `test_canonical_matrix_integrity.py` where present;
- standards mapping against ISO/IEC/IEEE 42010, IEEE/ISO/IEC 29148, and TOGAF Standard 10th Edition.

False-positive and false-negative rule:

- Treat every generated report, attached PDF, gap list, and diagram label as a hypothesis until the local codebase confirms it.
- Before adding work, check exact and normalized names, aliases, business keys, persona behavior, role and permission scope, tenant/facility scope, service ownership, API/UI route, use-case intent, test intent, migrations, fixtures, browser state, SignalBox scenario evidence, and CAID FP/FN audit output where available.
- Before accepting a pass claim, require direct evidence from the owning repo. Scenario-only evidence is not enough for backend contracts, and UI-only evidence is not enough for internal service readiness.

## Direct evidence that supports the architecture

| Area | Evidence |
| --- | --- |
| Platform fabric | `BulletTrain`, `global-agent-registry`, `nexus-a2a-protocol`, `symphonix-bridge-sdk`, `prompt-engine`, `signalbox-mcp`, `csaa`, and `caid-agent` exist as separate owned repos with implementation and test assets. Tool policy evidence should be taken from Bridge SDK, GHARRA, and SignalBox unless `tool-library` later passes a clinical-agent-tool conformance check. |
| Human personas | GHARRA defines a unified 101-persona registry with toolsets, SOPs, domains, FHIR role codes, function coverage, and main/v2 persona API tests. |
| AI superpersonas | Bridge SDK implements `SuperpersonaContract`, skill packs, tool bindings, framework selection, runtime budgets, safety posture, A2A card extension, MCP tool policy, SignalBox metadata, and audit evidence export. Focused contract and concurrency tests pass. |
| Agent routing | Nexus A2A documents trusted identity, route admission, GHARRA persona use, IAM groups, and real BulletTrain EventBus harness evidence. |
| Safety and governance | CSAA implements assurance/control-enforcement concepts, hazard gating, escalation, and safety-case controls. |
| Think/action loop | SignalBox implements persona-aware scenario execution and a perception-action loop; CAID implements strategy selection, reflection, structured memory, and learning-loop taxonomy; Prompt Engine supports planning/reflection and clinical/PHI policy inference. |
| Sibling-system estate | Domain repos exist for citizen, provider, scheduling, appointment, clinical pathways, laboratory, imaging, pharmacy, EMS, claims, ERP, supply chain, genomics, HMIS, screening, maternity, cancer, community nursing, ePACC's, PICIS, and analytics/BI surfaces. |
| Workspace inventory | `workspace-tooling` now generates a fork-aware Symphonix architecture inventory and maturity report from direct repo evidence. The latest generated report includes 53 owned repos and excludes 10 fork or duplicate worktree entries. |

## Attached PDF review and de-duplication findings

The attached document, `Mapping a CRAFTS-Based Agentic Intelligence Architecture into Symphonix-Health (1).pdf`, adds useful design material:

- a generic five-layer stack from context and trigger through substrate, fabric, persona/superpersona layer, and mechanism/outcome layer;
- a persona/superpersona inventory with role, skill, tool/API, input, and output columns;
- a proposed contract-first registry model using personas, skills, tools, guardrails, tests, and maturity artifacts;
- operationalized design principles: refuse human serial limits, keep the essence central, locality before convenience, never block emergency care, learn and compound, publish trust;
- CI/CD checks for schema validation, persona-to-tool compatibility, PHI locality, break-glass, safety evidence links, chain execution, and event replay;
- a compact ER model connecting `PERSONA` to `SKILL`, `TOOL`, `GUARDRAIL`, `TEST`, and `OUTCOME_METRIC`.

Local evidence corrects several PDF-era gaps:

| PDF-era claim or gap | Local decision | Evidence direction |
| --- | --- | --- |
| Persona registry absent or not code-verifiable | False positive for the local workspace. Do not build a second registry. | GHARRA owns `PersonaRegistry`, `PersonaDefinition`, and active superpersona coverage. Current focused tests validate 101 persona projections across the main and v2 API surfaces. |
| Skills/tools contract not normalized platform-wide | Partly fixed for GHARRA and Bridge SDK. GHARRA `persona_coverage.py` and Bridge SDK contracts are the current normalization surfaces. | Need ER export/schema conformance and sibling consumption tests, not a parallel `skills.yaml` source. |
| Tool library is the clinical agent tool registry | False positive until proven otherwise. | The repo named `tool-library` currently documents a physical/community tool-lending style app and matrix evidence. Clinical agent tool policy is in Bridge SDK/GHARRA/SignalBox. |
| Learning loop not generalized | Still open. | GHARRA has `outcome_learning.pathway_refine`, CAID memory, SignalBox attestation, and BulletTrain outcome tracking, but no workspace-wide closed-loop gate yet. |
| Maturity registry missing | Partly fixed. | `workspace-tooling` now generates an architecture inventory and maturity report from repo evidence. It is not yet a workspace gate, and maturity still needs to be wired into the architecture evidence index. |
| Power/compute policy under-specified | Partly implemented. | Bridge SDK has runtime budget policy; estate-wide compute/model routing policy still needs proof. |

The plan below therefore extends existing code-backed surfaces instead of duplicating them.

## Representative component tests

| Repo | Command | Result |
| --- | --- | --- |
| `global-agent-registry` | `python -m pytest tests/integration/test_personas_api.py -q` | PASS: 91 passed |
| `global-agent-registry` | `python -m pytest versions/v2/tests/integration/test_personas_api.py -q` | PASS: 79 passed |
| `symphonix-bridge-sdk` | `python -m pytest tests/test_superpersona_contract.py tests/test_concurrency.py -q` | PASS: 23 passed |
| `prompt-engine` | `python -m pytest tests/test_inference.py tests/test_engine.py -q` | PASS: 112 passed |
| `csaa` | `python -m pytest tests/test_hazards_risk.py tests/test_cli.py -q` | PASS: 26 passed |
| `caid-agent` | `python -m pytest tests/test_seeding_alignment_gate.py tests/test_seeded_alignment_traceability.py -q` | PASS: 48 passed |
| `caid-agent` | `python -m pytest tests/test_documentation_matrices.py tests/test_canonical_matrix_integrity.py -q` | PASS: 33 passed, 1 skipped |
| `workspace-tooling` | `python -m pytest tests/test_symphonix_architecture_inventory.py -q` | PASS: 2 passed |
| `caid-agent` | `python -m pytest tests -q` | INCOMPLETE: timed out after about 304 seconds; no full-suite pass claimed |

These results prove important components, but they do not prove platform-wide readiness.

## CAID FP/FN audit results

| Scope | Command | Result | Interpretation |
| --- | --- | --- | --- |
| `global-agent-registry` repo | `python -m caid.cli fpfn-audit --repo C:\Users\hgeec\github\global-agent-registry --format text --fail-on none` | PASS | Repo-level GHARRA package evidence is discoverable. |
| `global-agent-registry` persona component | `python -m caid.cli fpfn-audit --repo C:\Users\hgeec\github\global-agent-registry --component persona --format text --fail-on none` | BLOCKED | CAID did not discover a `persona` component in the repo ledger. This is unresolved audit coverage, not a persona implementation failure and not a pass. |
| `tool-library` repo | `python -m caid.cli fpfn-audit --repo C:\Users\hgeec\github\tool-library --format text --fail-on none` | PASS | The repo has its own evidence surface, but the audit does not prove it is the clinical agent tool registry. Clinical agent tool policy remains Bridge SDK, GHARRA, and SignalBox unless a later conformance check changes that. |

## Workspace-wide matrix and traceability gate

Command pattern:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'
python -m pytest tests/test_bullettrain_v1_matrix.py tests/test_canonical_matrix_integrity.py -q -x -p no:cacheprovider
```

Result summary:

- PASS: `BulletTrain`, `patient360-assistant`
- NO_MATRIX_TEST: `agent-skills`, `gp-system`, `health-agent-workspace`, `picis-system`, `second-brain-kb`, `symphonix-email-action-worker`, `symphonix-health.github.io`, `symphonix-health-docs`, `workspace-tooling`
- FAIL: the remaining tested sibling and support repos

Primary failure families:

| Failure family | Affected repos or examples | Meaning |
| --- | --- | --- |
| Source requirement IDs are not preserved in 14-column projection | `ambulance-ems`, `analytics-bi`, `citizen-portal`, `clinical-pathways`, `elocute`, `eps`, `erp`, `etps`, `global-agent-registry`, `HMIS`, `insurance-eclaims`, `lis`, `nexus-a2a-protocol`, `pacs-ris`, `pharmacy-system`, `prompt-engine`, `provider-portal`, `tool-library` | The reduced matrix is changing, dropping, adding, or normalizing requirement IDs instead of preserving the source row contract. |
| Requirements matrix metadata count differs from superset count | `africa-marketplace`, `appointment-system`, `blood-transfusion`, `cancer-pathway-tracker`, `community-nursing`, `csaa`, `design-system`, `epaccs`, `genomics-interpretation`, `healthcare-pain-points-plan`, `kenya-uhc-implementation`, `maternity-system`, `mha-administration`, `mortuary-and-me`, `REA-Agent-mcp`, `screening-recall`, `signalbox-mcp`, `supply-chain-erp`, `symphonix-bridge-sdk`, `symphonix-eps-ig`, `symphonix-public`, `triage-api` | The generated `requirements_matrix.json` metadata no longer matches the superset ledger. The earlier `caid-agent` occurrence was fixed in this pass by separating canonical and healthcare seeded superset handling and removing truncated L-202 IDs from seeded artifacts. |
| Scenario references unknown requirement | `scheduling-gateway` references `SG-001` from a scenario but the requirement is not known to the superset. | Scenario evidence is not traceable to a valid requirement ID. |
| Missing repo-local matrix gate | `agent-skills`, `gp-system`, `health-agent-workspace`, `picis-system`, `second-brain-kb`, `symphonix-email-action-worker`, `symphonix-health.github.io`, `symphonix-health-docs`, `workspace-tooling` | The repo has no local standard gate or no applicable waiver. |

The full workspace matrix loop still needs to be rerun after the CAID traceability repair. Focused CAID gates passed, but no workspace-wide pass is claimed.

## Documentation gaps

| Gap | Evidence | Required closure |
| --- | --- | --- |
| No controlling high-level architecture document | Existing revised documents are report-style and diagram-specific. | Adopt `symphonix-health-platform-high-level-architecture.md` as the controlling architecture description and make the diagram subordinate to it. |
| Missing architecture docs across domain repos | Only a minority of reviewed repos expose `docs/ARCHITECTURE.md` or `ARCHITECTURE.md`. | Add repo-local architecture docs or pointers to the platform HLA plus repo-specific views. |
| Persona/superpersona layer under-documented | Diagram originally hid persona, skills, tools, and frameworks inside platform services. The layer is now documented in the high-level architecture, and GHARRA/Bridge SDK focused tests pass. | Add ER export/schema validation and sibling conformance tests, using GHARRA and Bridge SDK as sources of truth. |
| Sibling/domain systems under-represented | Domain repos exist but the initial diagram did not show enough of the sibling estate. | Add the sibling-system ring and map each sibling to function, integration path, evidence, and test gate. |
| Learning loop not proven end to end | Components implement parts of the loop, but there is no single gated cross-platform evidence loop. | Define a learning-loop conformance test that passes through SignalBox, CAID, Prompt Engine, CSAA, Bridge SDK, and at least three sibling workflows. |

## Architecture gaps against the updated diagram

| Diagram element | Current standing | Gap |
| --- | --- | --- |
| CRAFTS context and triggers | Documented framing | Needs traceability to architecture drivers and requirement categories. |
| Enabling substrate | Partly implemented | Compute/resource governance and observability need workspace-level proof. |
| Symphonix platform fabric | Strong partial implementation | Cross-sibling integration gates are uneven. |
| Sibling systems and domain capabilities | Broad repo estate exists | Must be visible in diagram and documented with function/capability/evidence. |
| Persona, superpersona, skills, tools, frameworks | Code-backed and tested core in GHARRA and Bridge SDK | Must become a conformance requirement for sibling repos and must expose the ER view without creating a duplicate registry. |
| AI capability stack | Implemented in pieces | Needs per-capability evidence and route ownership. |
| Think/action/learning loop | Distributed implementation | Needs end-to-end scenario proof and outcome-fed updates. |
| Symphonix-Health mechanism core | Conceptually correct | Naming correction and evidence mapping required. |
| Essence-critical problem domains | Mostly present | Add bounded rationality. |
| Outcomes | Mostly present | Add innovation and invention with evidence obligations. |
| Design principles | Present as architecture principles | Add tests or review gates that check the principles indirectly through evidence. |

## Recommended target documentation set

The supporting documentation should be organized as an architecture package:

1. Architecture vision: TOGAF Architecture Vision for Symphonix-Health powering HelixCare.
2. High-level architecture description: ISO/IEC/IEEE 42010 aligned, with views and viewpoints.
3. System requirements specification: IEEE/ISO/IEC 29148 aligned functional and non-functional requirements.
4. Architecture requirements specification: TOGAF ADM requirements, constraints, assumptions, and gaps.
5. Application architecture: platform services, sibling systems, interfaces, ownership, routing.
6. Data architecture: FHIR/OpenHIE/claims/diagnostics/pharmacy/operational data flows.
7. Technology architecture: runtime, SDKs, gateway, identity, telemetry, deployment, CI gates.
8. Security and safety architecture: CSAA, IAM, HITL, audit, safety case, privacy, escalation.
9. Human and AI agent capability architecture: personas, superpersonas, skills, tools, frameworks, authority, learning, outcomes.
10. Verification and evidence strategy: canonical matrices, seeded data, SignalBox, FP/FN audit, real-service integration tests.
11. Roadmap and migration plan: work packages, transition states, acceptance gates.

## Gap closure plan summary

Detailed implementation steps are in `docs/superpowers/plans/2026-06-11-symphonix-health-platform-architecture-gap-closure.md`.

Workstream 1: architecture control

- Make the high-level architecture document the source of truth.
- Update the diagram labels and layer order to match the target taxonomy.
- Add documentation correspondence checks so diagram boxes are not orphaned from documentation sections.

Workstream 2: traceability repair

- Fix the reduced-matrix generator to preserve exact source requirement IDs.
- Regenerate affected matrices and metadata.
- Repair unknown requirement references such as `scheduling-gateway` `SG-001`.
- Add missing matrix gates or explicit waivers to non-runtime support repos.

Workstream 3: sibling and agent conformance

- Add a sibling-system capability inventory generated from repos.
- Add a superpersona capability conformance check for repos that expose agentic routes.
- Use GHARRA `PersonaRegistry`, GHARRA `persona_coverage.py`, and Bridge SDK `SuperpersonaContract` as the authority for personas, skills, tools, frameworks, authority scope, safety posture, and outcome evidence.
- Add a maturity ledger generated from real repo evidence; do not hand-maintain maturity claims.

Workstream 4: learning-loop evidence

- Define representative cross-platform workflows.
- Capture SignalBox scenario evidence and backend/network evidence.
- Feed results into CAID memory/advisory, Prompt Engine policy, CSAA risk cases, and Bridge SDK superpersona contracts.
- Require all claims to use real seeded internal services.

Workstream 5: final verification

- Run the workspace-wide matrix/integrity gate.
- Run representative direct tests for Bridge SDK, Prompt Engine, CSAA, CAID, SignalBox, GHARRA, Nexus, BulletTrain, and selected sibling systems.
- Run CAID FP/FN audit for disputed components.
- Re-run manual false-positive and false-negative checks before accepting each fixed gap.
- Publish updated architecture, gap register, and evidence index.

## Readiness rule

The architecture can be marked implemented when:

- the diagram and high-level architecture share the same layer taxonomy;
- every diagram element has a documented view and evidence mapping;
- all owned runtime repos have matrix gates or justified waivers;
- workspace-wide matrix/integrity gates pass;
- representative cross-sibling workflows pass with real seeded services;
- human and AI agent capability contracts are present for agentic routes;
- the persona ER view exports from existing GHARRA/Bridge SDK sources and validates without orphan personas, skills, tools, guardrails, tests, or outcome metrics;
- module maturity claims are generated from direct repo evidence;
- the learning loop is proven with at least one closed outcome-to-update path;
- the gap register has no blocking architecture, traceability, or safety gaps.
