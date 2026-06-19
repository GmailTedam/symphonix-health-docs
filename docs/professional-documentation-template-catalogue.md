# Professional documentation template catalogue

Repository: `symphonix-health-docs`

This document is the platform-level documentation catalogue for the
profession-aware documentation capability. It records the minimum templates
that CAID and product repos must support before claiming readiness for
user-facing or clinician-facing generated documentation.

The catalogue is intentionally conservative. It covers common medical,
nursing, pharmacy, allied-health, mental-health, urgent-care, handover, safety,
and patient-facing document types. Product repos may add local templates, but
they must preserve the metadata and safety contract below.

## Metadata contract

Every template must include:

`template_id`, `template_name`, `template_family`, `profession`,
`superpersona`, `audience`, `document_type`, `clinical_setting`,
`risk_level`, `status`, `version`, `owner`, `requires_human_review`,
`requires_signature`, `supports_patient_facing_variant`, `export_formats`,
`required_sections`, and `safety_checks`.

The minimum required sections are organisation header, patient banner,
document status, author role, clinical summary, structured sections, risk and
safety, plan and next steps, sign-off, and AI provenance.

The minimum safety checks are visible missing information, scope-of-practice
boundaries, visible red flags, blocked silent filing, and human sign-off before
final filing.

## Minimum go-live catalogue

| Template ID | Template name | Family | Profession | Superpersona | Document type | Risk |
| --- | --- | --- | --- | --- | --- | --- |
| DOC-TPL-001 | Generic consultation | clinical-note | medical | Medical Practitioner | consultation | standard |
| DOC-TPL-002 | SOAP note | clinical-note | medical | Medical Practitioner | soap | standard |
| DOC-TPL-003 | Initial assessment | clinical-note | allied-health | Allied Health/Rehab | assessment | standard |
| DOC-TPL-004 | Review note | clinical-note | multi-professional | Medical Practitioner | review | standard |
| DOC-TPL-005 | Discharge summary | letter | medical | Medical Practitioner | discharge | high |
| DOC-TPL-006 | Referral letter | letter | medical | Medical Practitioner | referral | standard |
| DOC-TPL-007 | Clinic letter | letter | medical | Medical Practitioner | clinic-letter | standard |
| DOC-TPL-008 | MDT summary | handover | multi-professional | Community/Social Care Interface | mdt | standard |
| DOC-TPL-009 | SBAR handover | handover | multi-professional | Emergency/Urgent Care | sbar | high |
| DOC-TPL-010 | Patient care plan | patient-facing | multi-professional | Community/Social Care Interface | care-plan | standard |
| DOC-TPL-011 | Physiotherapy initial assessment | clinical-note | physiotherapy | Allied Health/Rehab | assessment | standard |
| DOC-TPL-012 | Physiotherapy review | clinical-note | physiotherapy | Allied Health/Rehab | review | standard |
| DOC-TPL-013 | Physiotherapy discharge | letter | physiotherapy | Allied Health/Rehab | discharge | standard |
| DOC-TPL-014 | Home exercise plan | patient-facing | physiotherapy | Allied Health/Rehab | exercise-plan | standard |
| DOC-TPL-015 | Falls risk and mobility | safety-risk | physiotherapy | Allied Health/Rehab | falls-risk | high |
| DOC-TPL-016 | Rehab progress | clinical-note | allied-health | Allied Health/Rehab | progress | standard |
| DOC-TPL-017 | Nursing shift note | clinical-note | nursing | Nursing and Midwifery | shift-note | standard |
| DOC-TPL-018 | Nursing care plan | clinical-note | nursing | Nursing and Midwifery | care-plan | standard |
| DOC-TPL-019 | Wound care | clinical-note | nursing | Nursing and Midwifery | wound-care | high |
| DOC-TPL-020 | Clinical risk assessment | safety-risk | multi-professional | Medical Practitioner | risk-assessment | high |
| DOC-TPL-021 | Escalation note | safety-risk | multi-professional | Emergency/Urgent Care | escalation | critical |
| DOC-TPL-022 | Medicines reconciliation | clinical-note | pharmacy | Pharmacy and Medicines | medicines-reconciliation | high |
| DOC-TPL-023 | Medication review | clinical-note | pharmacy | Pharmacy and Medicines | medication-review | high |
| DOC-TPL-024 | Pharmacy intervention | clinical-note | pharmacy | Pharmacy and Medicines | intervention | standard |
| DOC-TPL-025 | Patient medication counselling | patient-facing | pharmacy | Pharmacy and Medicines | counselling | standard |
| DOC-TPL-026 | Mental health session | clinical-note | mental-health | Mental Health/Psychological Therapies | session | high |
| DOC-TPL-027 | Risk assessment and safety plan | safety-risk | mental-health | Mental Health/Psychological Therapies | safety-plan | critical |
| DOC-TPL-028 | Safeguarding concern | safety-risk | multi-professional | Community/Social Care Interface | safeguarding | critical |
| DOC-TPL-029 | Triage note | clinical-note | urgent-care | Emergency/Urgent Care | triage | high |
| DOC-TPL-030 | Urgent care handover | handover | urgent-care | Emergency/Urgent Care | handover | critical |

## Product repo responsibilities

Product repos that generate or display documentation must map each generated
document to one of the catalogue templates or record a gap. The selected
template must be visible in the rendered document metadata, and the document
must expose provenance, confidence or freshness, owner, next action, and human
review state.

AI-authored clinical documents are drafts. Final clinical filing requires a
qualified human signer and an audit trail. Silent filing is not permitted.

## Gap handling

If no catalogue template fits a document, the repo must record the gap in its
local gap register, name the responsible owner, and block final filing until
the template is approved or the document is completed manually.
