# Non-functional requirements specification

Repository: `symphonix-health-docs`.

## Scope

This specification records the repo-specific non-functional requirements observed from requirement IDs, code ownership paths, seeded healthcare profiles, and canonical use-case coverage. It uses the REA Agent quality scope model: ISO/IEC 25010-style quality attributes, healthcare safety and privacy overlays, traceability, and feedback from audit evidence into future requirement refinement.

## Source evidence

- Requirement ledger: `seeded_alignment_trace.py`
- Healthcare superset profile: `tests/harness/healthcare_requirements_superset.json`
- Canonical matrix: `tests/harness/reduced_json_matrices/seeded_alignment_trace.14col.json`
- Seed evidence: `seed_data/seeded_requirement_traceability.json`
- Framework and tooling evidence: repo-local tooling.

Observed implementation paths:
- `brand/showcase.html`
- `seeded_alignment_trace.py`
- `strategy/helixcare-rl-implementation-plan.html`

## Non-functional requirement IDs

- `NFR-CO-001`, `NFR-CO-002`, `NFR-FL-001`, `NFR-FL-002`, `NFR-IC-001`, `NFR-MA-001`, `NFR-MA-002`, `NFR-MA-003`
- `NFR-MA-004`, `NFR-PE-001`, `NFR-RE-001`, `NFR-RE-002`, `NFR-RE-003`, `NFR-SA-001`, `NFR-SA-002`, `NFR-SE-001`
- `NFR-SE-002`, `NFR-SE-003`, `NFR-SE-004`, `NFR-SHD-001`, `NFR-SHD-002`

## Non-functional requirement clauses

| Requirement ID | Canonical use-case evidence | Specification obligation |
|---|---|---|
| `NFR-CO-001` | `SA-SHD-00103`, `SA-SHD-SRC-00103` | Maintain repo-owned quality attribute evidence through requirements, canonical matrices, implementation ownership, tests, and seeded data. |
| `NFR-CO-002` | `SA-SHD-00104`, `SA-SHD-SRC-00104` | Maintain repo-owned quality attribute evidence through requirements, canonical matrices, implementation ownership, tests, and seeded data. |
| `NFR-FL-001` | `SA-SHD-00105`, `SA-SHD-SRC-00105` | Maintain repo-owned quality attribute evidence through requirements, canonical matrices, implementation ownership, tests, and seeded data. |
| `NFR-FL-002` | `SA-SHD-00106`, `SA-SHD-SRC-00106` | Maintain repo-owned quality attribute evidence through requirements, canonical matrices, implementation ownership, tests, and seeded data. |
| `NFR-IC-001` | `SA-SHD-00107`, `SA-SHD-SRC-00107` | Maintain repo-owned quality attribute evidence through requirements, canonical matrices, implementation ownership, tests, and seeded data. |
| `NFR-MA-001` | `SA-SHD-00108`, `SA-SHD-SRC-00108` | Maintain repo-owned quality attribute evidence through requirements, canonical matrices, implementation ownership, tests, and seeded data. |
| `NFR-MA-002` | `SA-SHD-00109`, `SA-SHD-SRC-00109` | Maintain repo-owned quality attribute evidence through requirements, canonical matrices, implementation ownership, tests, and seeded data. |
| `NFR-MA-003` | `SA-SHD-00110`, `SA-SHD-SRC-00110` | Maintain repo-owned quality attribute evidence through requirements, canonical matrices, implementation ownership, tests, and seeded data. |
| `NFR-MA-004` | `SA-SHD-00111`, `SA-SHD-SRC-00111` | Maintain repo-owned quality attribute evidence through requirements, canonical matrices, implementation ownership, tests, and seeded data. |
| `NFR-PE-001` | `SA-SHD-00112`, `SA-SHD-SRC-00112` | Maintain repo-owned quality attribute evidence through requirements, canonical matrices, implementation ownership, tests, and seeded data. |
| `NFR-RE-001` | `SA-SHD-00113`, `SA-SHD-SRC-00113` | Maintain repo-owned quality attribute evidence through requirements, canonical matrices, implementation ownership, tests, and seeded data. |
| `NFR-RE-002` | `SA-SHD-00114`, `SA-SHD-SRC-00114` | Maintain repo-owned quality attribute evidence through requirements, canonical matrices, implementation ownership, tests, and seeded data. |
| `NFR-RE-003` | `SA-SHD-00115`, `SA-SHD-SRC-00115` | Maintain repo-owned quality attribute evidence through requirements, canonical matrices, implementation ownership, tests, and seeded data. |
| `NFR-SA-001` | `SA-SHD-00116`, `SA-SHD-SRC-00116` | Maintain repo-owned quality attribute evidence through requirements, canonical matrices, implementation ownership, tests, and seeded data. |
| `NFR-SA-002` | `SA-SHD-00117`, `SA-SHD-SRC-00117` | Maintain repo-owned quality attribute evidence through requirements, canonical matrices, implementation ownership, tests, and seeded data. |
| `NFR-SE-001` | `SA-SHD-00118`, `SA-SHD-SRC-00118` | Maintain repo-owned quality attribute evidence through requirements, canonical matrices, implementation ownership, tests, and seeded data. |
| `NFR-SE-002` | `SA-SHD-00119`, `SA-SHD-SRC-00119` | Maintain repo-owned quality attribute evidence through requirements, canonical matrices, implementation ownership, tests, and seeded data. |
| `NFR-SE-003` | `SA-SHD-00120`, `SA-SHD-SRC-00120` | Maintain repo-owned quality attribute evidence through requirements, canonical matrices, implementation ownership, tests, and seeded data. |
| `NFR-SE-004` | `SA-SHD-00121`, `SA-SHD-SRC-00121` | Maintain repo-owned quality attribute evidence through requirements, canonical matrices, implementation ownership, tests, and seeded data. |
| `NFR-SHD-001` | `SA-SHD-00122`, `SA-SHD-SRC-00122` | Maintain repo-owned quality attribute evidence through requirements, canonical matrices, implementation ownership, tests, and seeded data. |
| `NFR-SHD-002` | `SA-SHD-00123`, `SA-SHD-SRC-00123` | Maintain repo-owned quality attribute evidence through requirements, canonical matrices, implementation ownership, tests, and seeded data. |

## Quality model

| Quality area | Repo obligation | Verification evidence |
|---|---|---|
| Safety and clinical governance | Preserve auditable decisions, role-aware workflows, and escalation paths for clinical or operational use. | Requirement IDs, canonical matrices, and repo-local traceability tests. |
| Security and privacy | Keep tenant, role, and data-scope boundaries explicit. Do not use internal mocks as readiness evidence. | Traceability ledger, seed profiles, and FP/FN audit output. |
| Reliability and observability | Keep failures inspectable through logs, metrics, reports, or documented operational evidence where applicable. | Architecture specification, tests, and audit reports. |
| Performance and scalability | Treat throughput and latency targets as deployment-profile constraints unless the repo owns concrete runtime thresholds. | Repo tests, harness matrices, and deployment documentation. |
| Accessibility and usability | Clinical and administrative surfaces must remain keyboard-operable and readable under the Symphonix Health design guidance. | Design specification and UI/accessibility tests where present. |

## Acceptance rule

Every non-functional requirement above must remain traceable to the canonical matrix and seeded evidence. Any repo change that affects safety, privacy, reliability, performance, accessibility, or operational posture must update this specification and the aligned test evidence.
