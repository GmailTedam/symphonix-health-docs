# BulletTrain Integration Doctrine

**Status:** Draft for adoption  
**Applies to:** Symphonix Health platform services, sibling applications, AI agents, analytics services, registries, and shared-record components  
**Companion:** [AI Agent-First Strategy](agent-first.md), [BulletTrain Integration Constitution](../../caid-agent/docs/architecture/bullettrain-integration-constitution.md)

## Decision

No sibling system in Symphonix Health directly exchanges, synchronises, reads, writes, polls, scrapes, or updates another sibling system's data.

All cross-system data movement goes through the BulletTrain Integration Engine. This applies to clinical, operational, administrative, analytics, registry, and AI-agent data flows.

This is not a preference for centralisation. It is the control that makes longitudinal health records, patient identity, consent, audit, provenance, analytics, and AI safe enough to operate as one regulated health platform.

## Scope

The doctrine applies to, at minimum:

- Shared Health Record and Patient360 capabilities.
- Client Registry / EMPI, provider registry, facility registry, and terminology services.
- HMIS, analytics-BI, public-health reporting, and data marts.
- LIS, pharmacy, PACS/RIS, e-prescribing, claims, scheduling, ambulance, maternity, community, GP, and provider/citizen portals.
- AI agents, MCP tools, Nexus A2A participants, GHARRA-routed agents, and closed-loop policy services.
- Caches, read models, feature stores, and bulk-export consumers.

External consumers may still use a service's published public contract where that contract is explicitly intended for external access. Sibling-to-sibling platform data exchange is different: it is always mediated by BulletTrain.

## Architecture Rule

Symphonix Health uses a mediated health-information-exchange pattern:

```
Sibling service
  -> BulletTrain connector / hub / event bus / bulk export
  -> identity, terminology, consent, provenance, audit, validation, routing
  -> authoritative service, subscriber, analytics mart, or AI context API
```

Forbidden pattern:

```
Sibling service -> sibling service private API / database / queue / scrape
```

Allowed patterns:

- A sibling emits a canonical event to BulletTrain.
- A sibling requests data through a BulletTrain connector or hub API.
- A sibling submits a proposed update to the authoritative service through BulletTrain.
- Analytics-BI receives BulletTrain-governed bulk export, stream, or event feeds.
- AI agents use BulletTrain-approved FHIR/context/tool APIs and create reviewable actions through BulletTrain.
- Derivative read models and caches are populated from BulletTrain-governed feeds.

## System-of-Record Principle

Services own domain data. BulletTrain owns exchange.

| Domain | Authoritative owner | BulletTrain responsibility |
|---|---|---|
| Patient identity and demographics | Client Registry / EMPI | Match, merge, alias, publish demographic updates, route proposed corrections |
| Longitudinal clinical record | Shared Health Record | Normalise, version, preserve provenance, support query/retrieve and subscriptions |
| Facilities, providers, organisations | Registry services | Resolve identifiers and publish authoritative directory updates |
| Laboratory, pharmacy, imaging, claims | Domain systems | Route orders, results, dispenses, reports, claims, and acknowledgements |
| HMIS and reporting | HMIS / reporting services | Receive governed aggregate and patient-derived feeds with lineage |
| Analytics-BI | Analytics platform | Consume governed bulk/event feeds, not operational databases |
| AI agents and feature stores | Agent platform / BulletTrain context APIs | Ground reasoning in consented, provenance-bearing, current data |

When a consuming service detects a likely correction, it does not mutate the owning system directly. It submits a proposed update through BulletTrain to the authoritative owner. The owner validates, accepts, rejects, or routes to human review.

## Clinical Case

Integrated digital health records fail when identity, medications, allergies, diagnoses, results, encounters, and care plans drift across systems. Direct point-to-point sharing creates exactly that failure mode: every bilateral link becomes its own mapping, consent interpretation, retry policy, audit trail, and data-quality rule.

BulletTrain mediation is clinically necessary because it provides:

- One patient identity resolution path instead of duplicate matching logic in every sibling.
- One consent and access-policy enforcement point for cross-system data.
- One provenance and audit chain for clinical and administrative changes.
- One terminology and schema normalisation layer.
- One reliable update-propagation mechanism for subscribers.
- One place to distinguish source-of-record writes from derivative read-model updates.

For clinicians, this means the Shared Health Record can be trusted as a longitudinal record rather than a collage of stale fragments. For operators, HMIS and analytics-BI can rely on lineage. For regulators, the platform can explain who saw or changed what, when, why, under which policy, and from which source.

## AI-First Implication

The AI-first strategy strengthens the need for BulletTrain mediation.

AI agents are only as safe as the data plane that grounds them. If an agent can query one sibling directly, scrape another, and write a third, the platform loses consent enforcement, context completeness, provenance, reproducibility, and clinical accountability.

BulletTrain enables agent capabilities that are difficult or unsafe in legacy point-to-point systems:

- Longitudinal patient summaries assembled from current, consented, provenance-bearing data.
- Clinical safety agents that reason over allergies, medicines, diagnoses, observations, results, and encounters.
- Care-gap and pathway-deviation agents across GP, hospital, community, pharmacy, and diagnostics.
- Duplicate-patient and demographic-reconciliation agents with human review workflows.
- Analytics agents that answer population-health questions from governed extracts instead of live operational databases.
- Closed-loop agents that sense, decide, act, and measure feedback through a single auditable plane.

AI agents may recommend, draft, classify, route, or create proposed updates. They do not directly mutate sibling records unless the action is mediated by BulletTrain, authorised by policy, and auditable against the system of record.

## Update Semantics

Cross-system updates use one of four patterns:

| Pattern | Use when | Write authority |
|---|---|---|
| Event publication | A source records a fact others need to know | Source system emits; subscribers update derivative views |
| Query / retrieve | A service needs current authoritative data | Authoritative service responds through BulletTrain |
| Proposed update | A service or AI agent detects a likely correction elsewhere | Authoritative owner accepts, rejects, or sends to human review |
| Bulk export | Analytics, HMIS, public health, model evaluation, or reporting needs population data | BulletTrain-governed export with lineage, filters, and consent controls |

No pattern requires a sibling to call another sibling directly.

## Required Controls

Every BulletTrain-mediated cross-system flow must provide:

- FHIR-aligned or canonical schema validation where patient/clinical data is involved.
- Patient, provider, facility, tenant, and source identifiers.
- Consent, access-policy, and tenant-isolation enforcement.
- Audit events and correlation IDs.
- Provenance and source-system lineage.
- Retry, timeout, idempotency, and error-normalisation policy.
- Terminology mapping where clinical codes cross service boundaries.
- Versioning or append-only history for clinical facts and proposed corrections.
- Monitoring for latency, failure rate, backlog, and stale feed conditions.

## Enforcement

The doctrine is enforced through:

- The [BulletTrain Integration Constitution](../../caid-agent/docs/architecture/bullettrain-integration-constitution.md).
- The [integration anti-pattern catalogue](../../caid-agent/docs/architecture/integration-anti-patterns.md).
- `caid scan-integration` corpus checks.
- Write-time blocking hooks for direct sibling, vendor, credential, and endpoint bypasses.
- PR review rejection for direct sibling integration.
- Test design that exercises the real BulletTrain hub instead of peer-to-peer shims.

## Standards Alignment

The doctrine aligns with established health-information-exchange practice:

- OpenHIE architecture: health information exchange layer mediating registries, shared health records, and point-of-service systems.
- WHO Digital Health Platform guidance: shared digital services and interoperability layers rather than isolated vertical systems.
- HL7 FHIR: RESTful clinical APIs, resources, subscriptions, and bulk data exchange.
- IHE profiles: cross-enterprise identity, document sharing, discovery, and exchange patterns.
- CDS Hooks / SMART on FHIR: governed decision-support and app integration at the point of care.

References:

- [OpenHIE Architecture](https://guides.ohie.org/arch-spec/dev-1/architecture-specification/overview-of-the-architecture)
- [WHO Digital Health Platform Handbook](https://www.who.int/publications/i/item/9789240013728)
- [HL7 FHIR](https://hl7.org/fhir/)
- [HL7 Bulk Data IG](https://build.fhir.org/ig/HL7/bulk-data/en/)
- [IHE HIE Whitepaper](https://profiles.ihe.net/ITI/HIE-Whitepaper/index.html)
- [CDS Hooks](https://hl7.github.io/cds-hooks-hl7-site/)

## One-Sentence Standard

Systems own their domain data; BulletTrain owns all cross-system exchange, update propagation, audit, provenance, consent enforcement, transformation, and AI grounding.
