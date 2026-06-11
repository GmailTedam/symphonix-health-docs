# Symphonix-Health Platform Architecture Gap Closure Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the Symphonix-Health architecture diagram, documentation, codebase evidence, canonical matrices, and tests agree across the owned workspace, excluding forked repositories.

**Architecture:** The controlling architecture is the ISO/IEC/IEEE 42010 aligned high-level architecture in `C:\Users\hgeec\github\symphonix-health-docs\reports\revised-documents\symphonix-health-platform-high-level-architecture.md`. It uses TOGAF architecture building blocks and IEEE/ISO/IEC 29148 requirements traceability. The architecture layers are CRAFTS context, enabling substrate, Symphonix platform fabric, sibling systems, persona/superpersona skills and tools framework, AI capability stack, think/action/learning loops, Symphonix-Health mechanism core, essence-critical problem domains, outcomes, and design principles.

**Tech Stack:** PowerShell, Python, pytest, CAID matrix utilities, repo-local harnesses, Markdown, Mermaid, SignalBox scenarios, Bridge SDK, GHARRA, Nexus A2A, BulletTrain, Prompt Engine, CSAA.

---

## Task 0: Run the de-duplication and FP/FN gate before implementation

- [x] Read `C:\Users\hgeec\github\second-brain-kb\knowledge\agent-workflows\wiki\symphonix-persona-skills-tools-gap-review.md`.
- [x] Confirm the current source-of-truth map before adding any new registry or schema:
  - GHARRA persona source: `C:\Users\hgeec\github\global-agent-registry\src\gharra\core\personas.py`
  - GHARRA skills/tools/function coverage: `C:\Users\hgeec\github\global-agent-registry\src\gharra\core\persona_coverage.py`
  - Bridge SDK contract source: `C:\Users\hgeec\github\symphonix-bridge-sdk\src\bridge_sdk\superpersona_contract.py`
  - SignalBox evidence source: `C:\Users\hgeec\github\signalbox-mcp\src\signalbox_mcp\attestation`
- [x] Treat the attached PDF as a hypothesis where it says a persona registry or skills/tools framework is absent. Local evidence shows those are partly implemented.
- [x] Do not add standalone `personas.yaml`, `skills.yaml`, `tools.yaml`, `guardrails.yaml`, `tests.yaml`, or `maturity.yaml` as hand-maintained sources unless an ADR first moves ownership away from the existing Python contract surfaces.
- [x] Run a false-positive check before each code change:
  - exact and normalized names;
  - aliases and role bindings;
  - persona behavior and permission scope;
  - tenant, facility, country, account, and patient scope;
  - service ownership;
  - use-case, test, API route, UI route, fixture, migration, and SignalBox scenario intent.
- [x] Run a false-negative check before accepting a pass:
  - direct owning-repo evidence;
  - backend/network evidence for backend contracts;
  - real seeded internal service evidence;
  - CAID FP/FN audit for disputed components;
  - no internal mock, stub, fake, or placeholder telemetry counted as readiness.
- [ ] For disputed repos, run:

```powershell
cd C:\Users\hgeec\github\caid-agent
python -m caid.cli fpfn-audit --repo C:\Users\hgeec\github\<repo> --format text --fail-on none
```

Acceptance criteria:

- No remediation task starts from a stale PDF/report claim without local evidence.
- The plan extends existing GHARRA, Bridge SDK, SignalBox, CAID, and BulletTrain surfaces instead of duplicating them.
- Each fix has a short FP/FN decision recorded in the repo-local gap register or the architecture evidence index.

## Task 1: Freeze the architecture taxonomy in docs

- [ ] In `C:\Users\hgeec\github\symphonix-health-docs\reports\revised-documents\nested-crafts-diagram-cross-check.md`, update the layer list to match `symphonix-health-platform-high-level-architecture.md`.
- [ ] Correct all references to layer 6 so the healthcare mechanism is `Symphonix-Health mechanism core`, while the reusable fabric remains `Symphonix platform fabric`.
- [ ] Add explicit entries for `Persona, superpersona, skills, and tools framework`, `Sibling systems and domain capabilities`, `Bounded rationality`, and `Innovation and invention`.
- [ ] Add the logical ER view from the attached PDF as a documentation view over existing GHARRA and Bridge SDK code, not as a new registry.
- [ ] Add a documentation correspondence table with these columns: `Diagram element`, `Architecture section`, `Repo evidence`, `Test evidence`, `Status`.
- [ ] Run:

```powershell
cd C:\Users\hgeec\github\symphonix-health-docs
rg -n "Symphonix-Health mechanism core|Persona, superpersona|Sibling systems|Bounded rationality|Innovation and invention" reports\revised-documents
```

Acceptance criteria:

- The diagram cross-check, high-level architecture document, and revised report language use the same layer names.
- No document claims all sibling systems are fully tested while matrix gates are failing.

## Task 2: Add a workspace architecture inventory generator

- [x] Create `C:\Users\hgeec\github\workspace-tooling\tools\symphonix_architecture_inventory.py`.
- [x] The script must scan owned repositories under `C:\Users\hgeec\github`.
- [x] Exclude repos whose upstream remote points to a third-party fork and exclude `_bt_hardening_wt` and `_bt_shr_fix_1780935930`.
- [x] For each repo, collect: repo name, remote, fork status, README present, `AGENTS.md` present, `CLAUDE.md` present, `REQUIREMENTS.md` present, architecture doc present, matrix files present, matrix test present, scenario files present, evidence count, direct test count, likely architecture role, maturity state, and source-of-truth role.
- [x] Emit:
  - `C:\Users\hgeec\github\workspace-tooling\reports\symphonix_architecture_inventory.json`
  - `C:\Users\hgeec\github\workspace-tooling\reports\symphonix_architecture_inventory.md`
- [x] Add tests in `C:\Users\hgeec\github\workspace-tooling\tests\test_symphonix_architecture_inventory.py` using a temporary fake workspace.
- [x] Run:

```powershell
cd C:\Users\hgeec\github\workspace-tooling
python -m pytest tests\test_symphonix_architecture_inventory.py -q
python tools\symphonix_architecture_inventory.py --workspace C:\Users\hgeec\github
```

Acceptance criteria:

- Forked repositories are excluded.
- Owned repos are classified consistently.
- The generated Markdown can be referenced from the architecture package.
- Maturity claims are generated from direct evidence and are not hand-written status labels.

## Task 3: Fix 14-column matrix requirement-ID preservation

- [x] In `C:\Users\hgeec\github\caid-agent`, inspect the matrix projection path used by the generated repo-local `tests/test_bullettrain_v1_matrix.py` tests.
- [ ] Do not normalize acceptance-criteria IDs such as `FR-BA-100-AC01` to base IDs such as `FR-BA-100`.
- [ ] Do not add legacy IDs such as `L-342` unless they are present in the source row.
- [ ] Preserve all source `requirement_ids` exactly and in stable order.
- [ ] Add regression fixtures for at least these cases:
  - `FR-BA-100-AC01` must remain `FR-BA-100-AC01`.
  - `NFR-EC-BIAS-001-AC01`, `NFR-EC-BIAS-001-AC02`, and `NFR-EC-BIAS-001-AC03` must not collapse to `NFR-EC-BIAS-001`.
  - `FR-BA-112-AC01` must not be dropped.
  - `L-342` must not be introduced when absent from the source row.
- [ ] Run:

```powershell
cd C:\Users\hgeec\github\caid-agent
python -m pytest tests -q -x
```

Acceptance criteria:

- CAID projection tests cover the exact drift seen in `ambulance-ems`, `insurance-eclaims`, `pharmacy-system`, and `provider-portal`.
- The projection preserves source requirement IDs exactly.

Implementation-pass status:

- Fixed the CAID seeded-alignment false positives caused by truncated L-202 IDs (`FR-00`, `FR-BA`, `FR-CO`, `NFR-S`, `NFR-R`) and added integrity coverage to prevent those IDs from reappearing in CAID seeded artifacts.
- Split CAID matrix configuration so the 99-row canonical CAID superset is not conflated with the 451-row healthcare seeded requirement matrix.
- Focused CAID traceability and matrix integrity tests pass. Full CAID suite timed out, and sibling-wide 14-column projection drift remains open.

## Task 4: Regenerate affected matrices and metadata

- [ ] For each repo that failed `requirements_matrix.metadata.requirement_count`, run the repo-local generation scripts that exist under `tests\harness`.
- [ ] Prefer existing scripts named `build_requirements_superset.py`, `build_requirements_matrix.py`, `build_nfr_canonical_matrices.py`, `build_derived_nfrs.py`, or repo-local equivalents.
- [ ] If a repo has no generator, repair the metadata from the actual `requirements_superset.json` count and add a generator issue to that repo's gap register.
- [ ] Run this validation loop after regeneration:

```powershell
$repos = @(
  "africa-marketplace","appointment-system","blood-transfusion","caid-agent",
  "cancer-pathway-tracker","community-nursing","csaa","design-system",
  "epaccs","genomics-interpretation","healthcare-pain-points-plan",
  "kenya-uhc-implementation","maternity-system","mha-administration",
  "mortuary-and-me","REA-Agent-mcp","screening-recall","signalbox-mcp",
  "supply-chain-erp","symphonix-bridge-sdk","symphonix-eps-ig",
  "symphonix-public","triage-api"
)
foreach ($repo in $repos) {
  Push-Location "C:\Users\hgeec\github\$repo"
  $env:PYTHONDONTWRITEBYTECODE='1'
  python -m pytest tests\test_canonical_matrix_integrity.py -q -x -p no:cacheprovider
  Pop-Location
}
```

Acceptance criteria:

- `requirements_matrix.metadata.requirement_count` equals the superset count in every regenerated repo.
- No internal fake service is introduced as readiness evidence.

## Task 5: Repair source/projection matrix drift in sibling repos

- [ ] After Task 3, regenerate or directly repair reduced 14-column matrices in:
  `ambulance-ems`, `analytics-bi`, `citizen-portal`, `clinical-pathways`, `elocute`, `eps`, `erp`, `etps`, `global-agent-registry`, `HMIS`, `insurance-eclaims`, `lis`, `nexus-a2a-protocol`, `pacs-ris`, `pharmacy-system`, `prompt-engine`, `provider-portal`, and `tool-library`.
- [ ] For each repo, run:

```powershell
cd C:\Users\hgeec\github\<repo>
$env:PYTHONDONTWRITEBYTECODE='1'
python -m pytest tests\test_bullettrain_v1_matrix.py tests\test_canonical_matrix_integrity.py -q -x -p no:cacheprovider
```

- [ ] Replace `<repo>` with the actual repo name for each run.
- [ ] Record failures in the repo-local gap register if a generator or source matrix is missing.

Acceptance criteria:

- All listed repos pass the 14-column projection preservation test.
- Any remaining failure has a direct code or data defect recorded with file path and requirement ID.

## Task 6: Fix unknown requirement references

- [ ] In `C:\Users\hgeec\github\scheduling-gateway`, inspect `tests\harness\json_matrices\seeded_alignment_trace_scenarios.json`.
- [ ] Find scenario `SA-SCHED-SRC-00219`.
- [ ] Decide whether `SG-001` is a valid requirement missing from the superset or a stale scenario reference.
- [ ] If valid, add `SG-001` to the correct superset and requirements matrix with acceptance criteria.
- [ ] If stale, replace it with the canonical requirement ID from the superset.
- [ ] Run:

```powershell
cd C:\Users\hgeec\github\scheduling-gateway
$env:PYTHONDONTWRITEBYTECODE='1'
python -m pytest tests\test_canonical_matrix_integrity.py -q -x -p no:cacheprovider
```

Acceptance criteria:

- No scenario references an unknown requirement ID.
- The fix is backed by either a valid requirement row or a corrected scenario reference.

## Task 7: Add matrix gates or waivers to repos without local gates

- [ ] Inspect these repos: `agent-skills`, `gp-system`, `health-agent-workspace`, `picis-system`, `second-brain-kb`, `symphonix-email-action-worker`, `symphonix-health.github.io`, `symphonix-health-docs`, `workspace-tooling`.
- [ ] If a repo is a runtime or domain system, add repo-local matrix tests following the canonical pattern from `C:\Users\hgeec\github\CANONICAL_ARTEFACT_SAMPLES_HANDOFF.md`.
- [ ] If a repo is a support-only repo, add an explicit `.caid-gate-exempt` or equivalent repo-local waiver that states why canonical matrices are not applicable.
- [ ] For runtime repos, run:

```powershell
cd C:\Users\hgeec\github\<repo>
$env:PYTHONDONTWRITEBYTECODE='1'
python -m pytest tests\test_bullettrain_v1_matrix.py tests\test_canonical_matrix_integrity.py -q -x -p no:cacheprovider
```

Acceptance criteria:

- Every owned repo has either a passing matrix gate or a documented non-runtime waiver.
- Waivers are not used for internal runtime services that execute clinical, operational, or agentic workflows.

## Task 8: Add repo-local architecture docs or pointers

- [ ] For each owned runtime repo without `ARCHITECTURE.md` or `docs\ARCHITECTURE.md`, add `docs\ARCHITECTURE.md`.
- [ ] Each doc must include:
  - repo purpose and boundary;
  - owned capabilities;
  - platform fabric dependencies;
  - sibling-system interfaces;
  - persona/superpersona participation;
  - data contracts and standards;
  - safety, identity, audit, and observability controls;
  - matrix and real-service test evidence.
- [ ] Link each repo-local doc back to:
  - `C:\Users\hgeec\github\symphonix-health-docs\reports\revised-documents\symphonix-health-platform-high-level-architecture.md`
  - `C:\Users\hgeec\github\CANONICAL_ARTEFACT_SAMPLES_HANDOFF.md`

Acceptance criteria:

- Runtime repos are no longer architecture-silent.
- The high-level diagram can cite repo-local architecture docs instead of only README text.

## Task 9: Harden the existing superpersona ER and capability conformance

- [ ] In `C:\Users\hgeec\github\global-agent-registry`, add `schemas\persona-capability-er.schema.json` only as a validation schema over existing GHARRA and Bridge SDK payloads.
- [ ] Add or extend an export surface that projects the existing code into the ER entities:
  `PERSONA`, `SKILL`, `TOOL`, `GUARDRAIL`, `TEST`, `OUTCOME_METRIC`, `PERSONA_SKILL`, `PERSONA_TOOL`, `PERSONA_GUARDRAIL`, and `PERSONA_TEST`.
- [ ] The export must read from `PersonaRegistry`, `persona_coverage.py`, Bridge SDK `SuperpersonaContract`, and SignalBox/CAID evidence. It must not introduce a second hand-maintained persona registry.
- [x] Run GHARRA tests proving the current registry and coverage projections have no missing persona references, no function purpose-of-use gaps, no sibling role binding gaps, and no logical tool binding gaps:
  - every `PERSONA_SKILL` references an existing persona and skill;
  - every `PERSONA_TOOL` references an existing persona and tool binding;
  - every regulated guardrail has a policy or attestation evidence link;
  - every test row links to a real repo-local test, SignalBox scenario, or documented non-runtime waiver;
  - every outcome metric has a threshold and owning workflow;
  - the contracts summary still reports stale claims such as "no persona registry" as false positives.
- [x] In `C:\Users\hgeec\github\symphonix-bridge-sdk`, run existing tests that validate the exported superpersona contract fields required by the high-level architecture:
  `persona_key`, `role_title`, `role_category`, `allowed_purposes`, `skill_packs`, `tool_bindings`, `intuition`, `runtime_budget`, `safety_class`, `eval_packs`, `required_token_scopes`, `audit_evidence_ref`, `a2a_card_extension`, and `mcp_tool_policy`.
- [ ] In sibling repos that expose agentic routes, add a contract smoke test that validates the repo's declared persona/function/tool use against GHARRA rather than a local duplicate list.
- [x] Run:

```powershell
cd C:\Users\hgeec\github\global-agent-registry
python -m pytest tests\integration\test_personas_api.py versions\v2\tests\integration\test_personas_api.py -q

cd C:\Users\hgeec\github\symphonix-bridge-sdk
python -m pytest tests\test_superpersona_contract.py tests\test_concurrency.py -q
```

Acceptance criteria:

- Agentic routes cannot claim platform conformance without persona, superpersona, skills, tools, framework, authority, safety, guardrail, test, outcome, and evidence bindings.
- The ER view validates against existing GHARRA and Bridge SDK payloads.
- Existing GHARRA and Bridge SDK tests still pass.

Implementation-pass status:

- Added missing GHARRA persona definitions so the active registry and v2 registry expose 101 personas and current coverage validates cleanly.
- `global-agent-registry` main persona API tests passed: 91 tests.
- `global-agent-registry` v2 persona API tests passed: 79 tests.
- `symphonix-bridge-sdk` superpersona contract and concurrency tests passed: 23 tests.
- ER schema/export and sibling agentic-route smoke tests remain open.

## Task 10: Prove one closed learning loop

- [ ] Select one representative workflow each from:
  - clinical care: `clinical-pathways` or `patient360-assistant`;
  - medicines or diagnostics: `pharmacy-system`, `lis`, or `pacs-ris`;
  - operations or finance: `insurance-eclaims`, `erp`, or `supply-chain-erp`.
- [ ] For each workflow, capture:
  - SignalBox scenario evidence;
  - backend API or event evidence;
  - Bridge SDK contract and audit evidence;
  - Prompt Engine prompt/policy/reflection evidence if used;
  - CSAA safety or hazard decision where relevant;
  - CAID memory/advisory or traceability update.
- [ ] Use `global-agent-registry` function `outcome_learning.pathway_refine` as the GHARRA-side function anchor when the workflow updates a pathway, policy, persona pack, or model governance artifact.
- [ ] Include an explicit observation-action-outcome-review record with outcome metric ID, threshold, reviewer, override status, and follow-up change target.
- [ ] Add the evidence references to the architecture evidence index.
- [ ] Run repo-specific scenario and backend tests. Do not count UI-only evidence as backend contract evidence.

Acceptance criteria:

- At least one workflow demonstrates outcome evidence feeding back into a policy, scenario, risk, prompt, contract, requirement, maturity state, or architecture update.
- The evidence uses real seeded internal service paths.

## Task 11: Run the final workspace verification gate

- [ ] Run the workspace-wide matrix loop across all owned repos.
- [x] Run representative component tests for:
  `symphonix-bridge-sdk`, `prompt-engine`, `csaa`, `caid-agent`, `signalbox-mcp`, `global-agent-registry`, `nexus-a2a-protocol`, `BulletTrain`, and selected sibling repos.
- [x] Run CAID FP/FN audit for disputed components:

```powershell
cd C:\Users\hgeec\github\caid-agent
python -m caid.cli fpfn-audit --repo C:\Users\hgeec\github\<repo> --format text --fail-on none
```

- [ ] Replace `<repo>` with each repo under dispute.
- [ ] Treat `BLOCKED` as unresolved evidence, not a pass.

Acceptance criteria:

- Workspace matrix/integrity gate passes or has documented non-runtime waivers.
- Direct component tests pass.
- FP/FN audit does not leave disputed implementation claims unresolved.
- The persona ER export has no orphan personas, skills, tools, guardrails, tests, or outcome metrics.
- Maturity claims in the architecture package are generated from current repo evidence.
- The architecture document, diagram, gap register, and evidence index agree.

Implementation-pass status:

- Representative tests passed for GHARRA, Bridge SDK, Prompt Engine, CSAA, CAID focused seeded-alignment/integrity paths, and workspace inventory.
- CAID FP/FN repo-level audits passed for `global-agent-registry` and `tool-library`; `global-agent-registry --component persona` returned `BLOCKED` because the component was not discovered in the CAID ledger.
- Full CAID suite timed out. The workspace-wide matrix loop still has known open sibling failures and is not marked complete.

## Task 12: Publish the architecture package

- [ ] Update the docs repo README to link to:
  - high-level architecture;
  - workspace review and gap plan;
  - diagram cross-check;
  - implementation plan;
  - assurance evidence.
- [ ] Update `docs\assurance\gap-register.md` with the workspace-level blocking gaps.
- [ ] Add an evidence index under `docs\assurance\symphonix-platform-evidence-index.md`.
- [x] Run docs repo tests:

```powershell
cd C:\Users\hgeec\github\symphonix-health-docs
python -m pytest tests -q
```

Acceptance criteria:

- A reviewer can start at the README, find the diagram, read the high-level architecture, inspect the gap plan, and trace every implementation claim to repo evidence or a named open gap.
