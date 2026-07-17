# Symphonix Health — Observability & Agent-First Refactoring Implementation Plan

**Source:** `SYMPHONIX_OBSERVABILITY_AGENT_GAP_ANALYSIS.md`
**Date:** April 2026
**Scope:** 34 repositories — gap remediation grouped by repository
**Approach:** Fix shared infrastructure first (Phase 0), then apply per-repo changes in priority order

---

## How to Use This Plan

1. **Complete Phase 0 first.** Every per-repo change depends on the shared packages built in Phase 0.
2. **Effort codes:** `XS` < 2h · `S` 2–4h · `M` 4–8h · `L` 1–2d · `XL` 2–5d
3. **Priority codes:** `P0` blocking · `P1` critical · `P2` high · `P3` medium · `P4` low
4. **Score notation:** `x/10 → y/10` = current pillar score → target after this phase's changes

---

## Phase 0 — Shared Infrastructure (Do Once, Apply Everywhere)

These changes create the reusable building blocks. All per-repo work in Phases 1–3 imports from these.

---

### 0.1 `symphonix-bridge-sdk` — Add Observability Package

**Effort:** `XL` | **Priority:** `P0`

All shared observability utilities should live in `symphonix-bridge-sdk` so every service installs one package.

#### Files to Create

**`observability/__init__.py`**
```python
from .logging import configure_logging, get_logger
from .tracing import init_tracer, traced
from .correlation import CorrelationIdMiddleware, get_correlation_id
from .metrics import PrometheusMetrics
from .sentry import init_sentry
from .audit import AuditLogger

__all__ = [
    "configure_logging", "get_logger",
    "init_tracer", "traced",
    "CorrelationIdMiddleware", "get_correlation_id",
    "PrometheusMetrics",
    "init_sentry",
    "AuditLogger",
]
```

**`observability/logging.py`** — Structured JSON logging
```python
import logging
import os
from pythonjsonlogger import jsonlogger

def configure_logging(service_name: str, level: str = "INFO") -> None:
    handler = logging.StreamHandler()
    formatter = jsonlogger.JsonFormatter(
        "%(asctime)s %(name)s %(levelname)s %(message)s %(trace_id)s %(span_id)s %(correlation_id)s",
        rename_fields={"asctime": "timestamp", "levelname": "level", "name": "logger"},
    )
    handler.setFormatter(formatter)
    root = logging.getLogger()
    root.handlers = [handler]
    root.setLevel(getattr(logging, level.upper(), logging.INFO))
    logging.getLogger().info("Logging configured", extra={"service": service_name})

def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
```

**`observability/correlation.py`** — Extracted from BulletTrain `observability/correlation.py`
```python
import uuid
from contextvars import ContextVar
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

_correlation_id: ContextVar[str] = ContextVar("correlation_id", default="")

def get_correlation_id() -> str:
    return _correlation_id.get()

class CorrelationIdMiddleware(BaseHTTPMiddleware):
    HEADER = "X-Correlation-ID"

    async def dispatch(self, request: Request, call_next):
        cid = request.headers.get(self.HEADER) or str(uuid.uuid4())
        _correlation_id.set(cid)
        response = await call_next(request)
        response.headers[self.HEADER] = cid
        return response
```

**`observability/metrics.py`** — Prometheus exporter wrapper
```python
from prometheus_client import Counter, Histogram, Gauge, make_asgi_app, CollectorRegistry

_registry = CollectorRegistry(auto_describe=True)

class PrometheusMetrics:
    def __init__(self, service_name: str):
        self.service = service_name
        self.request_count = Counter(
            "http_requests_total",
            "Total HTTP requests",
            ["method", "endpoint", "status"],
            registry=_registry,
        )
        self.request_latency = Histogram(
            "http_request_duration_seconds",
            "HTTP request latency",
            ["method", "endpoint"],
            registry=_registry,
        )

    def metrics_app(self):
        """Mount at /metrics via app.mount('/metrics', metrics.metrics_app())"""
        return make_asgi_app(registry=_registry)
```

**`observability/sentry.py`**
```python
import os
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration

_PHI_KEYS = {"patient_id", "external_nhs_number", "dob", "address", "name", "email"}

def _before_send(event, hint):
    """Strip PHI from Sentry payloads before transmission."""
    if extra := event.get("extra"):
        for key in list(extra.keys()):
            if key.lower() in _PHI_KEYS:
                del extra[key]
    return event

def init_sentry(service_name: str, environment: str = "production") -> None:
    dsn = os.getenv("SENTRY_DSN")
    if not dsn:
        return
    sentry_sdk.init(
        dsn=dsn,
        environment=environment,
        release=os.getenv("APP_VERSION", "unknown"),
        server_name=service_name,
        integrations=[FastApiIntegration(), SqlalchemyIntegration()],
        traces_sample_rate=0.1,
        before_send=_before_send,
    )
```

**`observability/audit.py`** — HL7 FHIR AuditEvent pattern (from etps)
```python
import json
import logging
from datetime import datetime, timezone
from typing import Any

_audit_log = logging.getLogger("audit")

class AuditLogger:
    """Emits HL7 FHIR R4 AuditEvent-compatible structured audit records."""

    def __init__(self, service_name: str):
        self.service = service_name

    def log(
        self,
        action: str,           # C | R | U | D | E
        resource_type: str,    # Patient, MedicationRequest, etc.
        resource_id: str,
        actor_id: str,
        outcome: str = "0",    # 0=success 4=minor-failure 8=serious-failure 12=major
        details: dict[str, Any] | None = None,
    ) -> None:
        event = {
            "resourceType": "AuditEvent",
            "type": {"system": "http://terminology.hl7.org/CodeSystem/audit-event-type", "code": "rest"},
            "action": action,
            "recorded": datetime.now(timezone.utc).isoformat(),
            "outcome": outcome,
            "agent": [{"who": {"identifier": {"value": actor_id}}, "requestor": True}],
            "entity": [{"what": {"reference": f"{resource_type}/{resource_id}"}}],
            "source": {"observer": {"display": self.service}},
        }
        if details:
            event["_details"] = details
        _audit_log.info(json.dumps(event))
```

**`observability/health.py`** — Standard health router
```python
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

class HealthResponse(BaseModel):
    status: str
    service: str
    version: str

def make_health_router(service_name: str, version: str = "unknown") -> APIRouter:
    r = APIRouter()

    @r.get("/health", response_model=HealthResponse, tags=["ops"])
    async def health():
        return HealthResponse(status="ok", service=service_name, version=version)

    @r.get("/readiness", response_model=HealthResponse, tags=["ops"])
    async def readiness():
        return HealthResponse(status="ok", service=service_name, version=version)

    @r.get("/liveness", response_model=HealthResponse, tags=["ops"])
    async def liveness():
        return HealthResponse(status="ok", service=service_name, version=version)

    return r
```

#### `pyproject.toml` / `setup.py` additions
```toml
[project.dependencies]
python-json-logger = ">=2.0"
prometheus-client = ">=0.20"
sentry-sdk = {version = ">=2.0", extras = ["fastapi"]}
opentelemetry-sdk = ">=1.24"
opentelemetry-instrumentation-fastapi = ">=0.45"
```

---

### 0.2 Docker Compose OTel Collector — Enable Log + Trace Shipping

**Effort:** `S` | **Priority:** `P0`

The workspace already has `docker-compose.infra.otel.yml`. Enable the Prometheus scrape config and Loki log shipping.

**`otel-collector-config.yml`** (add to infra):
```yaml
receivers:
  otlp:
    protocols:
      grpc:
        endpoint: 0.0.0.0:4317
      http:
        endpoint: 0.0.0.0:4318
  prometheus:
    config:
      scrape_configs:
        - job_name: symphonix-services
          static_configs:
            - targets: ["*:8000"]  # Replace with service discovery

processors:
  batch:
    timeout: 5s
  resource:
    attributes:
      - key: deployment.environment
        value: ${ENVIRONMENT}
        action: upsert

exporters:
  prometheus:
    endpoint: "0.0.0.0:8889"
  loki:
    endpoint: http://loki:3100/loki/api/v1/push
  jaeger:
    endpoint: jaeger:14250
    tls:
      insecure: true

service:
  pipelines:
    traces:
      receivers: [otlp]
      processors: [batch, resource]
      exporters: [jaeger]
    metrics:
      receivers: [otlp, prometheus]
      processors: [batch]
      exporters: [prometheus]
    logs:
      receivers: [otlp]
      processors: [batch, resource]
      exporters: [loki]
```

---

### 0.3 Shared Alertmanager Rules

**Effort:** `M` | **Priority:** `P0`

**`alerting/symphonix-base-rules.yml`**:
```yaml
groups:
  - name: symphonix.availability
    rules:
      - alert: ServiceDown
        expr: up == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "{{ $labels.job }} is down"

      - alert: HighErrorRate
        expr: rate(http_requests_total{status=~"5.."}[5m]) / rate(http_requests_total[5m]) > 0.05
        for: 2m
        labels:
          severity: warning
        annotations:
          summary: "Error rate > 5% on {{ $labels.job }}"

      - alert: SlowP95
        expr: histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) > 2
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "p95 latency > 2s on {{ $labels.job }}"

  - name: symphonix.clinical
    rules:
      - alert: CriticalValueNotificationFailure
        expr: increase(critical_value_notification_failures_total[5m]) > 0
        for: 0m
        labels:
          severity: critical
          team: clinical
        annotations:
          summary: "Critical lab value notification failure — patient safety risk"

      - alert: PrescriptionDeliveryFailure
        expr: increase(prescription_delivery_failures_total[5m]) > 0
        for: 0m
        labels:
          severity: critical
          team: pharmacy
        annotations:
          summary: "Prescription delivery failure detected"

      - alert: TriageApiUnavailable
        expr: up{job="triage-api"} == 0
        for: 30s
        labels:
          severity: critical
          team: clinical
        annotations:
          summary: "Triage API is down — patient safety risk"
```

---

### 0.4 Shared Grafana Dashboard Template

**Effort:** `M` | **Priority:** `P1`

Create `dashboards/symphonix-service-template.json` — a parameterised Grafana dashboard with variables for `job` and `service`. Each service gets its own dashboard by instantiating this template with its service name. Panels include:
- Request rate (RPS)
- Error rate %
- p50/p95/p99 latency
- Active connections
- Custom business metrics panel (empty, for service-specific additions)

---

## Phase 1 — Tier 1: Core Clinical Systems

---

### 1.1 `ambulance-ems` — 5/10 → 9/10

**Priority:** `P1` | **Effort:** `M`

| Gap | Fix |
|-----|-----|
| Metrics endpoint | Expose `metrics.py` custom metrics via Prometheus |
| Correlation IDs | Apply `CorrelationIdMiddleware` from `symphonix-bridge-sdk` |
| Sentry | `init_sentry("ambulance-ems")` in `main.py` |
| Alerting | Add EMS-specific rules to Alertmanager |
| Log shipping | Enable OTel log exporter in app init |
| Dashboard | Instantiate shared Grafana template + add `dispatch_response_time_seconds` panel |

#### Changes

**`main.py`** — add at startup:
```python
from symphonix_bridge_sdk.observability import (
    configure_logging, init_sentry, init_tracer,
    CorrelationIdMiddleware, PrometheusMetrics, make_health_router
)

configure_logging("ambulance-ems")
init_sentry("ambulance-ems")
init_tracer("ambulance-ems", otlp_endpoint=settings.OTEL_ENDPOINT)

app = FastAPI()
app.add_middleware(CorrelationIdMiddleware)
metrics = PrometheusMetrics("ambulance-ems")
app.mount("/metrics", metrics.metrics_app())
app.include_router(make_health_router("ambulance-ems", settings.VERSION))
```

**`metrics.py`** — replace internal dict with Prometheus counters/histograms:
```python
from prometheus_client import Counter, Histogram
from symphonix_bridge_sdk.observability.metrics import _registry

dispatch_requests = Counter(
    "ems_dispatch_requests_total", "Dispatch requests", ["outcome"], registry=_registry
)
response_time = Histogram(
    "ems_response_time_seconds", "EMS response time seconds", registry=_registry
)
```

**`alerting/ems-rules.yml`** (add to Alertmanager):
```yaml
groups:
  - name: ems.sla
    rules:
      - alert: EMSResponseTimeBreached
        expr: histogram_quantile(0.95, rate(ems_response_time_seconds_bucket[10m])) > 480
        for: 1m
        labels:
          severity: critical
          team: ems
        annotations:
          summary: "EMS p95 response time > 8 minutes — SLA breach"
```

---

### 1.2 `appointment-system` — 1/10 → 8/10

**Priority:** `P1` | **Effort:** `L`

Full greenfield instrumentation required. Only audit trail exists.

#### Changes

**`main.py`**:
```python
from symphonix_bridge_sdk.observability import (
    configure_logging, init_sentry, init_tracer,
    CorrelationIdMiddleware, PrometheusMetrics, make_health_router
)

configure_logging("appointment-system")
init_sentry("appointment-system")
init_tracer("appointment-system", otlp_endpoint=settings.OTEL_ENDPOINT)

app = FastAPI()
app.add_middleware(CorrelationIdMiddleware)
metrics = PrometheusMetrics("appointment-system")
app.mount("/metrics", metrics.metrics_app())
app.include_router(make_health_router("appointment-system", settings.VERSION))
```

**New file `observability/appt_metrics.py`**:
```python
from prometheus_client import Counter, Histogram, Gauge
from symphonix_bridge_sdk.observability.metrics import _registry

bookings_total = Counter(
    "appt_bookings_total", "Total appointment bookings", ["specialty", "outcome"], registry=_registry
)
booking_latency = Histogram(
    "appt_booking_duration_seconds", "Booking API latency", registry=_registry
)
waitlist_size = Gauge(
    "appt_waitlist_size", "Current waitlist size", ["specialty"], registry=_registry
)
slot_utilisation = Gauge(
    "appt_slot_utilisation_ratio", "Slot utilisation 0–1", ["specialty"], registry=_registry
)
```

**`services/booking_service.py`** — wrap booking logic with OTel span:
```python
from opentelemetry import trace
from .observability.appt_metrics import bookings_total, booking_latency

tracer = trace.get_tracer("appointment-system")

async def create_booking(request: BookingRequest) -> Booking:
    with tracer.start_as_current_span("booking.create") as span:
        span.set_attribute("appt.specialty", request.specialty)
        span.set_attribute("appt.urgency", request.urgency)
        with booking_latency.time():
            result = await _do_create_booking(request)
        bookings_total.labels(specialty=request.specialty, outcome="success").inc()
        return result
```

**`alerting/appt-rules.yml`**:
```yaml
groups:
  - name: appt.availability
    rules:
      - alert: BookingSystemDown
        expr: up{job="appointment-system"} == 0
        for: 1m
        labels:
          severity: critical
          team: scheduling
        annotations:
          summary: "Appointment system unavailable — patients cannot book"
      - alert: HighBookingFailureRate
        expr: rate(appt_bookings_total{outcome="failure"}[5m]) / rate(appt_bookings_total[5m]) > 0.1
        for: 3m
        labels:
          severity: warning
```

---

### 1.3 `BulletTrain` — 4/10 → 10/10

**Priority:** `P1` | **Effort:** `L`

BulletTrain already has OTel, correlation IDs, health endpoints, and audit. Complete the remaining 6 gaps.

#### Changes

**`main.py`** — add:
```python
from symphonix_bridge_sdk.observability import configure_logging, init_sentry, PrometheusMetrics

configure_logging("bullettrain")
init_sentry("bullettrain")
metrics = PrometheusMetrics("bullettrain")
app.mount("/metrics", metrics.metrics_app())
```

**`metrics.py`** — convert existing custom metrics to Prometheus:
```python
from prometheus_client import Counter, Histogram, Gauge
from symphonix_bridge_sdk.observability.metrics import _registry

hie_messages_total = Counter(
    "hie_messages_total", "HIE messages processed", ["source_system", "message_type"], registry=_registry
)
hie_latency = Histogram(
    "hie_processing_duration_seconds", "Message processing latency", registry=_registry
)
connected_systems = Gauge(
    "hie_connected_systems_count", "Active connected systems", registry=_registry
)
```

**`logging_config.py`** — replace stdlib with structured logging:
```python
# DELETE existing basicConfig calls, REPLACE with:
from symphonix_bridge_sdk.observability import configure_logging
configure_logging("bullettrain", level="INFO")
```

**`alerting/bullettrain-rules.yml`**:
```yaml
groups:
  - name: bullettrain.hie
    rules:
      - alert: HIEBackpressure
        expr: rate(hie_messages_total[1m]) < 1
        for: 5m
        labels:
          severity: warning
          team: platform
        annotations:
          summary: "HIE message throughput dropped — possible backpressure"
      - alert: HIEDown
        expr: up{job="bullettrain"} == 0
        for: 30s
        labels:
          severity: critical
        annotations:
          summary: "BulletTrain HIE is DOWN — all connected systems are affected"
```

**`dashboards/bullettrain.json`** — extend shared template with:
- HIE message throughput panel
- Connected systems gauge
- Per-system error rate breakdown
- Agent plan execution rate (when BEVAN is activated)

**Agent activation (BEVAN — Phase 3 dependency):**

In `agents/dx_agent.py`:
```python
# Replace stub LLM call with:
from azure.ai.inference import ChatCompletionsClient
from azure.core.credentials import AzureKeyCredential
from opentelemetry.instrumentation.openai import OpenAIInstrumentor

OpenAIInstrumentor().instrument()  # OTel Gen AI spans

client = ChatCompletionsClient(
    endpoint=settings.AZURE_AI_ENDPOINT,
    credential=AzureKeyCredential(settings.AZURE_AI_KEY),
)
```

---

### 1.4 `clinical-pathways` — 2/10 → 8/10

**Priority:** `P1` | **Effort:** `L`

OTel and audit are present. Need: health endpoint, Prometheus, structured logging, correlation IDs, Sentry, alerting, log shipping.

#### Changes

**`main.py`**:
```python
from symphonix_bridge_sdk.observability import (
    configure_logging, init_sentry, init_tracer,
    CorrelationIdMiddleware, PrometheusMetrics, make_health_router
)

configure_logging("clinical-pathways")
init_sentry("clinical-pathways")
app.add_middleware(CorrelationIdMiddleware)
metrics = PrometheusMetrics("clinical-pathways")
app.mount("/metrics", metrics.metrics_app())
app.include_router(make_health_router("clinical-pathways", settings.VERSION))
```

**New file `observability/pathway_metrics.py`**:
```python
from prometheus_client import Counter, Histogram
from symphonix_bridge_sdk.observability.metrics import _registry

pathway_executions = Counter(
    "pathway_executions_total",
    "Clinical pathway executions",
    ["pathway_code", "outcome"],
    registry=_registry,
)
decision_branch_hits = Counter(
    "pathway_decision_branches_total",
    "Decision branch traversals",
    ["pathway_code", "branch"],
    registry=_registry,
)
deviation_flags = Counter(
    "pathway_deviations_total",
    "Protocol deviations flagged",
    ["pathway_code", "deviation_type"],
    registry=_registry,
)
```

**`alerting/pathways-rules.yml`**:
```yaml
groups:
  - name: pathways.governance
    rules:
      - alert: PathwayDeviationSpike
        expr: rate(pathway_deviations_total[10m]) > 0.1
        for: 5m
        labels:
          severity: warning
          team: clinical-governance
        annotations:
          summary: "Protocol deviation rate elevated — clinical governance review needed"
```

---

### 1.5 `eps` — 5/10 → 9/10

**Priority:** `P1` | **Effort:** `M`

OTel, health endpoint, structured logging, and audit are present. Need: Prometheus endpoint, correlation IDs, Sentry, alerting, log shipping, dashboard.

#### Changes

**`main.py`** — add:
```python
from symphonix_bridge_sdk.observability import init_sentry, CorrelationIdMiddleware, PrometheusMetrics
init_sentry("eps")
app.add_middleware(CorrelationIdMiddleware)
metrics = PrometheusMetrics("eps")
app.mount("/metrics", metrics.metrics_app())
```

**`metrics.py`** — convert existing custom metrics to Prometheus:
```python
from prometheus_client import Counter, Histogram
from symphonix_bridge_sdk.observability.metrics import _registry

prescriptions_issued = Counter(
    "eps_prescriptions_total", "Prescriptions issued", ["prescriber_type", "outcome"], registry=_registry
)
dispense_latency = Histogram(
    "eps_dispense_duration_seconds", "Prescription to dispense latency", registry=_registry
)
rejection_total = Counter(
    "eps_rejections_total", "Prescription rejections", ["reason"], registry=_registry
)
```

**`alerting/eps-rules.yml`**:
```yaml
groups:
  - name: eps.safety
    rules:
      - alert: HighRejectionRate
        expr: rate(eps_rejections_total[5m]) / rate(eps_prescriptions_total[5m]) > 0.15
        for: 5m
        labels:
          severity: warning
          team: pharmacy
        annotations:
          summary: "EPS rejection rate > 15% — clinical review needed"
      - alert: EPSDown
        expr: up{job="eps"} == 0
        for: 1m
        labels:
          severity: critical
          team: pharmacy
```

---

### 1.6 `etps` — 3/10 → 8/10

**Priority:** `P1` | **Effort:** `M`

OTel, health endpoint, and audit (with HL7 AuditEvent — the gold standard pattern) are present. Need: Prometheus, structured logging, correlation IDs, Sentry, alerting.

#### Changes

**`main.py`** — add:
```python
from symphonix_bridge_sdk.observability import (
    configure_logging, init_sentry, CorrelationIdMiddleware, PrometheusMetrics
)
configure_logging("etps")
init_sentry("etps")
app.add_middleware(CorrelationIdMiddleware)
metrics = PrometheusMetrics("etps")
app.mount("/metrics", metrics.metrics_app())
```

**New file `observability/transfer_metrics.py`**:
```python
from prometheus_client import Counter, Histogram
from symphonix_bridge_sdk.observability.metrics import _registry

transfers_total = Counter(
    "etps_transfers_total", "Patient summary transfers", ["direction", "outcome"], registry=_registry
)
transfer_latency = Histogram(
    "etps_transfer_duration_seconds", "Transfer end-to-end latency", registry=_registry
)
transfer_failures = Counter(
    "etps_transfer_failures_total", "Transfer failures", ["failure_reason"], registry=_registry
)
```

**`alerting/etps-rules.yml`**:
```yaml
groups:
  - name: etps.transfers
    rules:
      - alert: TransferFailureSurge
        expr: rate(etps_transfer_failures_total[5m]) > 0.05
        for: 2m
        labels:
          severity: critical
          team: interoperability
        annotations:
          summary: "Patient summary transfer failures elevated — patients arriving without records"
```

**Note:** The `AuditEvent` implementation in etps is the canonical pattern for the portfolio. No changes needed to audit.py — it should be replicated to all other clinical repos as per Section 0.1.

---

### 1.7 `gp-system` — 0/10 → 9/10

**Priority:** `P1` | **Effort:** `XL`

All 10 pillars absent. Highest regulatory risk (CQC audit mandate). Full implementation required.

#### Changes

**`main.py`** (create from scratch or extend existing):
```python
from symphonix_bridge_sdk.observability import (
    configure_logging, init_sentry, init_tracer,
    CorrelationIdMiddleware, PrometheusMetrics, make_health_router, AuditLogger
)

configure_logging("gp-system")
init_sentry("gp-system")
init_tracer("gp-system", otlp_endpoint=settings.OTEL_ENDPOINT)

app = FastAPI()
app.add_middleware(CorrelationIdMiddleware)
metrics = PrometheusMetrics("gp-system")
app.mount("/metrics", metrics.metrics_app())
app.include_router(make_health_router("gp-system", settings.VERSION))
audit = AuditLogger("gp-system")
```

**New file `observability/gp_metrics.py`**:
```python
from prometheus_client import Counter, Histogram, Gauge
from symphonix_bridge_sdk.observability.metrics import _registry

consultations_total = Counter(
    "gp_consultations_total", "GP consultations", ["consultation_type", "outcome"], registry=_registry
)
referrals_total = Counter(
    "gp_referrals_total", "Outbound referrals", ["specialty", "urgency"], registry=_registry
)
qof_score = Gauge(
    "gp_qof_score", "Quality and Outcomes Framework score", ["indicator"], registry=_registry
)
```

**`api/patient_router.py`** — add CQC-mandated audit on every record access:
```python
from ..observability.audit import audit  # instance from main.py

@router.get("/patients/{patient_id}")
async def get_patient(patient_id: str, current_user=Depends(get_current_user)):
    audit.log(
        action="R",
        resource_type="Patient",
        resource_id=patient_id,
        actor_id=current_user.id,
        details={"reason": "clinical_review"},
    )
    return await patient_service.get(patient_id)
```

**`alerting/gp-rules.yml`**:
```yaml
groups:
  - name: gp.availability
    rules:
      - alert: GPSystemDown
        expr: up{job="gp-system"} == 0
        for: 1m
        labels:
          severity: critical
          team: primary-care
        annotations:
          summary: "GP system unavailable during clinical hours"
```

---

### 1.8 `HMIS` — 1/10 → 7/10

**Priority:** `P2` | **Effort:** `L`

OTel is present. Need: health endpoint, Prometheus, structured logging, audit trail, correlation IDs, Sentry, alerting.

#### Changes

**`main.py`** — add:
```python
from symphonix_bridge_sdk.observability import (
    configure_logging, init_sentry, CorrelationIdMiddleware,
    PrometheusMetrics, make_health_router, AuditLogger
)
configure_logging("hmis")
init_sentry("hmis")
app.add_middleware(CorrelationIdMiddleware)
metrics = PrometheusMetrics("hmis")
app.mount("/metrics", metrics.metrics_app())
app.include_router(make_health_router("hmis", settings.VERSION))
audit = AuditLogger("hmis")
```

**New file `observability/hmis_metrics.py`**:
```python
from prometheus_client import Counter, Gauge, Histogram
from symphonix_bridge_sdk.observability.metrics import _registry

data_ingestion_events = Counter(
    "hmis_ingestion_events_total", "Data ingestion events", ["source", "status"], registry=_registry
)
report_generation_duration = Histogram(
    "hmis_report_generation_seconds", "Report generation latency", ["report_type"], registry=_registry
)
data_freshness_seconds = Gauge(
    "hmis_data_freshness_seconds", "Seconds since last data update", ["dataset"], registry=_registry
)
```

**`alerting/hmis-rules.yml`**:
```yaml
groups:
  - name: hmis.pipeline
    rules:
      - alert: HMISDataStaleness
        expr: hmis_data_freshness_seconds > 86400
        for: 10m
        labels:
          severity: warning
          team: analytics
        annotations:
          summary: "HMIS data is more than 24h stale — national reporting at risk"
```

---

### 1.9 `insurance-eclaims` — 3/10 → 8/10

**Priority:** `P2` | **Effort:** `M`

OTel, health endpoint, and audit are present. Need: Prometheus, structured logging, correlation IDs, Sentry, alerting.

#### Changes

**`main.py`** — add:
```python
from symphonix_bridge_sdk.observability import (
    configure_logging, init_sentry, CorrelationIdMiddleware, PrometheusMetrics
)
configure_logging("insurance-eclaims")
init_sentry("insurance-eclaims")
app.add_middleware(CorrelationIdMiddleware)
metrics = PrometheusMetrics("insurance-eclaims")
app.mount("/metrics", metrics.metrics_app())
```

**New file `observability/claims_metrics.py`**:
```python
from prometheus_client import Counter, Histogram, Gauge
from symphonix_bridge_sdk.observability.metrics import _registry

claims_submitted = Counter(
    "eclaims_submitted_total", "Claims submitted", ["payer", "claim_type"], registry=_registry
)
claims_adjudicated = Counter(
    "eclaims_adjudicated_total", "Claims adjudicated", ["payer", "outcome"], registry=_registry
)
claim_value = Histogram(
    "eclaims_value_distribution", "Claim value in local currency", registry=_registry
)
pending_claims = Gauge(
    "eclaims_pending_count", "Claims awaiting adjudication", ["payer"], registry=_registry
)
```

**`alerting/eclaims-rules.yml`**:
```yaml
groups:
  - name: eclaims.financial
    rules:
      - alert: HighDenialRate
        expr: rate(eclaims_adjudicated_total{outcome="denied"}[30m]) / rate(eclaims_adjudicated_total[30m]) > 0.2
        for: 10m
        labels:
          severity: warning
          team: revenue-cycle
        annotations:
          summary: "Claim denial rate > 20% — billing team review needed"
```

---

### 1.10 `lis` — 5/10 → 9/10

**Priority:** `P1` | **Effort:** `M`

OTel, health endpoint, structured logging, and audit are present. Need: Prometheus endpoint, correlation IDs, Sentry, alerting, log shipping, dashboard.

#### Changes

**`main.py`** — add:
```python
from symphonix_bridge_sdk.observability import init_sentry, CorrelationIdMiddleware, PrometheusMetrics
init_sentry("lis")
app.add_middleware(CorrelationIdMiddleware)
metrics = PrometheusMetrics("lis")
app.mount("/metrics", metrics.metrics_app())
```

**`metrics.py`** — convert to Prometheus:
```python
from prometheus_client import Counter, Histogram, Gauge
from symphonix_bridge_sdk.observability.metrics import _registry

specimens_received = Counter(
    "lis_specimens_received_total", "Specimens received", ["specimen_type"], registry=_registry
)
tat_seconds = Histogram(
    "lis_turnaround_time_seconds",
    "Specimen-to-result turnaround time",
    ["test_type"],
    buckets=[300, 600, 1800, 3600, 7200, 14400],
    registry=_registry,
)
critical_values_pending = Gauge(
    "lis_critical_values_pending", "Critical values awaiting notification", registry=_registry
)
critical_value_notification_failures = Counter(
    "critical_value_notification_failures_total", "Failed critical value notifications", registry=_registry
)
```

**`alerting/lis-rules.yml`**:
```yaml
groups:
  - name: lis.patient-safety
    rules:
      - alert: CriticalValueNotificationFailure
        expr: increase(critical_value_notification_failures_total[5m]) > 0
        for: 0m
        labels:
          severity: critical
          team: laboratory
          pagerduty: "true"
        annotations:
          summary: "CRITICAL: Lab critical value notification failed — immediate clinical response required"
      - alert: LISTATBreached
        expr: histogram_quantile(0.95, rate(lis_turnaround_time_seconds_bucket[30m])) > 3600
        for: 10m
        labels:
          severity: warning
          team: laboratory
        annotations:
          summary: "LIS p95 TAT > 1 hour — ISO 15189 SLA at risk"
```

---

### 1.11 `pacs-ris` — 5/10 → 9/10

**Priority:** `P1` | **Effort:** `M`

OTel, health endpoint, structured logging, and audit are present. Need: Prometheus endpoint, correlation IDs, Sentry, alerting, log shipping, dashboard.

#### Changes

**`main.py`** — add:
```python
from symphonix_bridge_sdk.observability import init_sentry, CorrelationIdMiddleware, PrometheusMetrics
init_sentry("pacs-ris")
app.add_middleware(CorrelationIdMiddleware)
metrics = PrometheusMetrics("pacs-ris")
app.mount("/metrics", metrics.metrics_app())
```

**`metrics.py`** — convert to Prometheus:
```python
from prometheus_client import Counter, Histogram, Gauge
from symphonix_bridge_sdk.observability.metrics import _registry

studies_received = Counter(
    "pacs_studies_received_total", "DICOM studies received", ["modality"], registry=_registry
)
reporting_tat = Histogram(
    "pacs_reporting_tat_seconds",
    "Study receipt to report seconds",
    ["modality", "priority"],
    buckets=[1800, 3600, 14400, 86400],
    registry=_registry,
)
unreported_studies = Gauge(
    "pacs_unreported_studies_count", "Studies awaiting report", ["modality"], registry=_registry
)
storage_utilisation = Gauge(
    "pacs_storage_utilisation_ratio", "DICOM storage utilisation 0–1", registry=_registry
)
```

**`alerting/pacs-rules.yml`**:
```yaml
groups:
  - name: pacs.operations
    rules:
      - alert: PACSStorageCritical
        expr: pacs_storage_utilisation_ratio > 0.9
        for: 5m
        labels:
          severity: critical
          team: radiology-it
        annotations:
          summary: "PACS storage > 90% — urgent expansion required"
      - alert: UnreportedStudiesBacklog
        expr: pacs_unreported_studies_count > 50
        for: 30m
        labels:
          severity: warning
          team: radiology
        annotations:
          summary: "Radiology reporting backlog > 50 studies"
```

---

### 1.12 `pharmacy-system` — 5/10 → 9/10

**Priority:** `P1` | **Effort:** `M`

OTel, health endpoint, structured logging, and audit are present. Need: Prometheus endpoint, correlation IDs, Sentry, alerting, log shipping, dashboard.

#### Changes

**`main.py`** — add:
```python
from symphonix_bridge_sdk.observability import init_sentry, CorrelationIdMiddleware, PrometheusMetrics
init_sentry("pharmacy-system")
app.add_middleware(CorrelationIdMiddleware)
metrics = PrometheusMetrics("pharmacy-system")
app.mount("/metrics", metrics.metrics_app())
```

**`metrics.py`** — convert to Prometheus:
```python
from prometheus_client import Counter, Histogram, Gauge
from symphonix_bridge_sdk.observability.metrics import _registry

dispensing_events = Counter(
    "pharmacy_dispensing_total", "Dispensing events", ["drug_class", "outcome"], registry=_registry
)
prescription_delivery_failures = Counter(
    "prescription_delivery_failures_total", "Failed prescription deliveries", registry=_registry
)
stock_level = Gauge(
    "pharmacy_stock_level_units", "Current stock level", ["drug_name"], registry=_registry
)
```

**`alerting/pharmacy-rules.yml`**:
```yaml
groups:
  - name: pharmacy.safety
    rules:
      - alert: PrescriptionDeliveryFailure
        expr: increase(prescription_delivery_failures_total[5m]) > 0
        for: 0m
        labels:
          severity: critical
          team: pharmacy
          pagerduty: "true"
      - alert: CriticalDrugStockLow
        expr: pharmacy_stock_level_units{drug_name=~"insulin|adrenaline|morphine"} < 10
        for: 5m
        labels:
          severity: critical
          team: pharmacy
```

---

## Phase 2 — Tier 2: Infrastructure & Platform Systems

---

### 2.1 `analytics-bi` — 2/10 → 8/10

**Priority:** `P2` | **Effort:** `L`

OTel and health endpoint present. Need: Prometheus, structured logging, audit trail, correlation IDs, Sentry, alerting, dashboard (for the BI system's own health — required).

#### Changes

**`main.py`** — add:
```python
from symphonix_bridge_sdk.observability import (
    configure_logging, init_sentry, CorrelationIdMiddleware,
    PrometheusMetrics, AuditLogger
)
configure_logging("analytics-bi")
init_sentry("analytics-bi")
app.add_middleware(CorrelationIdMiddleware)
metrics = PrometheusMetrics("analytics-bi")
app.mount("/metrics", metrics.metrics_app())
audit = AuditLogger("analytics-bi")
```

**New file `observability/bi_metrics.py`**:
```python
from prometheus_client import Counter, Histogram, Gauge
from symphonix_bridge_sdk.observability.metrics import _registry

queries_total = Counter(
    "bi_queries_total", "BI queries executed", ["dataset", "user_role"], registry=_registry
)
query_duration = Histogram(
    "bi_query_duration_seconds", "Query execution time", ["dataset"], registry=_registry
)
data_freshness = Gauge(
    "bi_data_freshness_seconds", "Seconds since last ETL refresh", ["dataset"], registry=_registry
)
```

**`api/query_router.py`** — audit all clinical data queries:
```python
@router.post("/query")
async def run_query(request: QueryRequest, user=Depends(get_current_user)):
    audit.log(action="E", resource_type="Dataset", resource_id=request.dataset,
              actor_id=user.id, details={"query_preview": request.sql[:100]})
    ...
```

---

### 2.2 `caid-agent` — 2/10 → 9/10

**Priority:** `P1` | **Effort:** `L`

OTel and health endpoint present. Need: structured logging, audit trail, Prometheus, Sentry, alerting, plus agent-specific OTel spans.

#### Changes

**`main.py`** — add:
```python
from symphonix_bridge_sdk.observability import (
    configure_logging, init_sentry, CorrelationIdMiddleware,
    PrometheusMetrics, AuditLogger
)
configure_logging("caid-agent")
init_sentry("caid-agent")
app.add_middleware(CorrelationIdMiddleware)
metrics = PrometheusMetrics("caid-agent")
app.mount("/metrics", metrics.metrics_app())
audit = AuditLogger("caid-agent")
```

**New file `observability/agent_metrics.py`** — OTel Gen AI semantic conventions:
```python
from prometheus_client import Counter, Histogram, Gauge
from symphonix_bridge_sdk.observability.metrics import _registry

agent_plans_total = Counter(
    "caid_agent_plans_total", "Agent plan executions", ["plan_type", "outcome"], registry=_registry
)
tool_calls_total = Counter(
    "caid_tool_calls_total", "Tool call invocations", ["tool_name", "outcome"], registry=_registry
)
plan_duration = Histogram(
    "caid_plan_duration_seconds", "Agent plan end-to-end duration", registry=_registry
)
token_usage = Counter(
    "caid_llm_tokens_total", "LLM tokens consumed", ["model", "direction"], registry=_registry
)
```

**`agent_planner.py`** — wrap each plan step with OTel Gen AI span:
```python
from opentelemetry import trace
from .observability.agent_metrics import agent_plans_total, plan_duration, tool_calls_total

tracer = trace.get_tracer("caid-agent", schema_url="https://opentelemetry.io/schemas/1.27.0")

async def execute_plan(plan: Plan) -> PlanResult:
    with tracer.start_as_current_span("gen_ai.agent.plan") as span:
        span.set_attribute("gen_ai.system", "caid")
        span.set_attribute("gen_ai.operation.name", "plan")
        span.set_attribute("gen_ai.request.model", plan.model)
        with plan_duration.time():
            for step in plan.steps:
                with tracer.start_as_current_span("gen_ai.agent.tool_call") as tool_span:
                    tool_span.set_attribute("gen_ai.tool.name", step.tool)
                    result = await execute_step(step)
                    tool_calls_total.labels(tool_name=step.tool, outcome=result.status).inc()
        agent_plans_total.labels(plan_type=plan.type, outcome="success").inc()
```

**Correlation ID as Plan ID** — ensure every plan carries a `plan_id` propagated as the correlation ID so all tool call logs are linkable.

---

### 2.3 `global-agent-registry` (GHARRA) — 3/10 → 9/10

**Priority:** `P1` | **Effort:** `M`

OTel, health endpoint, and correlation IDs present. Need: Prometheus endpoint, structured logging, audit trail, Sentry, alerting.

#### Changes

**`main.py`** — add:
```python
from symphonix_bridge_sdk.observability import (
    configure_logging, init_sentry, PrometheusMetrics, AuditLogger
)
configure_logging("gharra")
init_sentry("gharra")
metrics = PrometheusMetrics("gharra")
app.mount("/metrics", metrics.metrics_app())
audit = AuditLogger("gharra")
```

**`metrics.py`** — convert to Prometheus:
```python
from prometheus_client import Counter, Histogram, Gauge
from symphonix_bridge_sdk.observability.metrics import _registry

agent_registrations = Counter(
    "gharra_agent_registrations_total", "Agent registration events", ["agent_type", "action"], registry=_registry
)
routing_requests = Counter(
    "gharra_routing_requests_total", "Agent routing requests", ["outcome"], registry=_registry
)
routing_latency = Histogram(
    "gharra_routing_duration_seconds", "Agent discovery latency", registry=_registry
)
registered_agents = Gauge(
    "gharra_registered_agents_count", "Active registered agents", ["capability"], registry=_registry
)
```

**`gateway.py`** — add audit on registration changes:
```python
@router.post("/agents/register")
async def register_agent(request: AgentRegistration, user=Depends(get_current_user)):
    audit.log(action="C", resource_type="Agent", resource_id=request.agent_id,
              actor_id=user.id, details={"capabilities": request.capabilities})
    ...
```

**`alerting/gharra-rules.yml`**:
```yaml
groups:
  - name: gharra.registry
    rules:
      - alert: GHARRADown
        expr: up{job="gharra"} == 0
        for: 30s
        labels:
          severity: critical
          team: platform
        annotations:
          summary: "GHARRA agent registry is down — all agent routing is broken"
```

---

### 2.4 `health-agent-workspace` — 0/10 → 6/10

**Priority:** `P3` | **Effort:** `M`

All pillars absent. Development/testing workspace — implement OTel, structured logging, and agent session tracing. Full production observability not required for a workspace.

#### Changes

**`main.py`** (or equivalent entry point):
```python
from symphonix_bridge_sdk.observability import (
    configure_logging, init_tracer, make_health_router
)
configure_logging("health-agent-workspace", level="DEBUG")
init_tracer("health-agent-workspace", otlp_endpoint=settings.OTEL_ENDPOINT)
app.include_router(make_health_router("health-agent-workspace"))
```

**`planner.py`** — add plan session tracing (same pattern as caid-agent above).

---

### 2.5 `nexus-a2a-protocol` — 3/10 → 9/10

**Priority:** `P1` | **Effort:** `L`

OTel, health endpoint, and audit present. **Critical requirement:** W3C Trace Context propagation in every A2A message envelope. Without this, agent-to-agent chains are invisible.

#### Changes

**`main.py`** — add:
```python
from symphonix_bridge_sdk.observability import (
    configure_logging, init_sentry, CorrelationIdMiddleware, PrometheusMetrics
)
configure_logging("nexus-a2a")
init_sentry("nexus-a2a")
app.add_middleware(CorrelationIdMiddleware)
metrics = PrometheusMetrics("nexus-a2a")
app.mount("/metrics", metrics.metrics_app())
```

**`protocol/message.py`** — inject W3C Trace Context into A2A envelope:
```python
from opentelemetry import trace
from opentelemetry.propagators.textmap import TraceContextTextMapPropagator

propagator = TraceContextTextMapPropagator()

class A2AMessage(BaseModel):
    sender_id: str
    receiver_id: str
    payload: dict
    trace_context: dict = {}  # W3C traceparent/tracestate

    @classmethod
    def create(cls, sender_id: str, receiver_id: str, payload: dict) -> "A2AMessage":
        carrier: dict = {}
        propagator.inject(carrier)  # Injects traceparent from current active span
        return cls(sender_id=sender_id, receiver_id=receiver_id,
                   payload=payload, trace_context=carrier)

    def restore_context(self) -> trace.Context:
        return propagator.extract(self.trace_context)
```

**New file `observability/a2a_metrics.py`**:
```python
from prometheus_client import Counter, Histogram
from symphonix_bridge_sdk.observability.metrics import _registry

messages_total = Counter(
    "nexus_a2a_messages_total", "A2A messages exchanged", ["sender", "receiver", "outcome"], registry=_registry
)
message_latency = Histogram(
    "nexus_a2a_delivery_seconds", "A2A message delivery latency", registry=_registry
)
```

---

### 2.6 `provider-portal` — 3/10 → 8/10

**Priority:** `P2` | **Effort:** `M`

OTel, health endpoint, audit present. Need: Prometheus, structured logging, correlation IDs, Sentry, alerting.

#### Changes

**`main.py`** — add:
```python
from symphonix_bridge_sdk.observability import (
    configure_logging, init_sentry, CorrelationIdMiddleware, PrometheusMetrics
)
configure_logging("provider-portal")
init_sentry("provider-portal")
app.add_middleware(CorrelationIdMiddleware)
metrics = PrometheusMetrics("provider-portal")
app.mount("/metrics", metrics.metrics_app())
```

**`alerting/provider-portal-rules.yml`**:
```yaml
groups:
  - name: portal.availability
    rules:
      - alert: ProviderPortalDuringClinicalHours
        expr: up{job="provider-portal"} == 0 and (hour() >= 7 and hour() <= 20)
        for: 2m
        labels:
          severity: critical
          team: clinical-it
        annotations:
          summary: "Provider portal down during clinical hours"
```

---

### 2.7 `REA-Agent-mcp` — 1/10 → 7/10

**Priority:** `P2` | **Effort:** `L`

OTel present. Need: health endpoint, Prometheus, structured logging, audit trail, correlation IDs, Sentry, alerting. Also: adopt official MCP SDK.

#### Changes

**`main.py`** — add:
```python
from symphonix_bridge_sdk.observability import (
    configure_logging, init_sentry, CorrelationIdMiddleware,
    PrometheusMetrics, make_health_router, AuditLogger
)
configure_logging("rea-agent-mcp")
init_sentry("rea-agent-mcp")
app.add_middleware(CorrelationIdMiddleware)
metrics = PrometheusMetrics("rea-agent-mcp")
app.mount("/metrics", metrics.metrics_app())
app.include_router(make_health_router("rea-agent-mcp"))
audit = AuditLogger("rea-agent-mcp")
```

**`requirements.txt`** — add official MCP SDK (replaces hand-rolled):
```
mcp>=1.0.0       # Official Python MCP SDK (FastMCP-compatible)
```

**`server.py`** — migrate to FastMCP pattern:
```python
from mcp.server.fastmcp import FastMCP
from symphonix_bridge_sdk.observability import configure_logging, init_tracer

mcp = FastMCP("rea-agent-mcp")

@mcp.tool()
async def query_resource_event(resource_id: str, event_type: str) -> dict:
    """Query REA resource events."""
    with tracer.start_as_current_span("mcp.tool.query_resource_event") as span:
        span.set_attribute("gen_ai.tool.name", "query_resource_event")
        ...
```

---

### 2.8 `scheduling-gateway` — 0/10 → 8/10

**Priority:** `P1` | **Effort:** `L`

All pillars absent. Gateway = entry point for correlation ID injection (must be first to inject).

#### Changes

**`main.py`**:
```python
from symphonix_bridge_sdk.observability import (
    configure_logging, init_sentry, init_tracer,
    CorrelationIdMiddleware, PrometheusMetrics, make_health_router, AuditLogger
)

configure_logging("scheduling-gateway")
init_sentry("scheduling-gateway")
init_tracer("scheduling-gateway", otlp_endpoint=settings.OTEL_ENDPOINT)

app = FastAPI()
app.add_middleware(CorrelationIdMiddleware)  # Must be first — injects X-Correlation-ID
metrics = PrometheusMetrics("scheduling-gateway")
app.mount("/metrics", metrics.metrics_app())
app.include_router(make_health_router("scheduling-gateway"))
audit = AuditLogger("scheduling-gateway")
```

**New file `observability/gateway_metrics.py`**:
```python
from prometheus_client import Counter, Histogram
from symphonix_bridge_sdk.observability.metrics import _registry

routing_requests = Counter(
    "gateway_routing_requests_total", "Scheduling gateway routing requests",
    ["target_system", "outcome"], registry=_registry
)
upstream_latency = Histogram(
    "gateway_upstream_duration_seconds", "Upstream system call latency",
    ["target_system"], registry=_registry
)
```

---

### 2.9 `signalbox-mcp` — 0/10 → 7/10

**Priority:** `P1` | **Effort:** `L`

All pillars absent. MCP signal router — every routing decision is a clinical audit event.

#### Changes

**`main.py`** (or equivalent MCP server entrypoint):
```python
from mcp.server.fastmcp import FastMCP
from symphonix_bridge_sdk.observability import (
    configure_logging, init_sentry, init_tracer, AuditLogger
)

configure_logging("signalbox-mcp")
init_sentry("signalbox-mcp")
init_tracer("signalbox-mcp")
audit = AuditLogger("signalbox-mcp")

mcp = FastMCP("signalbox-mcp")
```

**Audit every signal routing decision:**
```python
@mcp.tool()
async def route_clinical_signal(signal_type: str, patient_id: str, priority: str) -> dict:
    audit.log(
        action="E",
        resource_type="ClinicalSignal",
        resource_id=f"{signal_type}/{patient_id}",
        actor_id="system",
        details={"priority": priority},
    )
    ...
```

---

### 2.10 `supply-chain-erp` — 3/10 → 8/10

**Priority:** `P2` | **Effort:** `M`

OTel, health endpoint, audit present. Need: Prometheus, structured logging, correlation IDs, Sentry, alerting.

#### Changes

**`main.py`** — add:
```python
from symphonix_bridge_sdk.observability import (
    configure_logging, init_sentry, CorrelationIdMiddleware, PrometheusMetrics
)
configure_logging("supply-chain-erp")
init_sentry("supply-chain-erp")
app.add_middleware(CorrelationIdMiddleware)
metrics = PrometheusMetrics("supply-chain-erp")
app.mount("/metrics", metrics.metrics_app())
```

**`alerting/supply-chain-rules.yml`**:
```yaml
groups:
  - name: supply.critical-stock
    rules:
      - alert: CriticalMedicalSupplyLow
        expr: pharmacy_stock_level_units{drug_name=~".*"} < 20
        for: 5m
        labels:
          severity: warning
          team: procurement
        annotations:
          summary: "Critical medical supply stock low — procurement action required"
```

---

### 2.11 `tool-library` — 3/10 → 9/10

**Priority:** `P1` | **Effort:** `M`

OTel, health endpoint, audit present. Shared tool library: **every tool execution must emit an OTel child span** — this is the most impactful single change across the agent platform.

#### Changes

**`main.py`** — add:
```python
from symphonix_bridge_sdk.observability import (
    configure_logging, init_sentry, CorrelationIdMiddleware, PrometheusMetrics
)
configure_logging("tool-library")
init_sentry("tool-library")
app.add_middleware(CorrelationIdMiddleware)
metrics = PrometheusMetrics("tool-library")
app.mount("/metrics", metrics.metrics_app())
```

**New file `decorators/traced_tool.py`** — apply to ALL exported tools:
```python
import functools
from opentelemetry import trace
from prometheus_client import Counter, Histogram
from symphonix_bridge_sdk.observability.metrics import _registry

tracer = trace.get_tracer("tool-library")

_tool_calls = Counter(
    "tool_library_calls_total", "Tool calls", ["tool_name", "outcome"], registry=_registry
)
_tool_duration = Histogram(
    "tool_library_duration_seconds", "Tool execution latency", ["tool_name"], registry=_registry
)

def traced_tool(func):
    """Decorator: wraps any tool function with OTel Gen AI span + Prometheus metrics."""
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        tool_name = func.__name__
        with tracer.start_as_current_span(f"gen_ai.tool.{tool_name}") as span:
            span.set_attribute("gen_ai.tool.name", tool_name)
            try:
                with _tool_duration.labels(tool_name=tool_name).time():
                    result = await func(*args, **kwargs)
                _tool_calls.labels(tool_name=tool_name, outcome="success").inc()
                return result
            except Exception as e:
                _tool_calls.labels(tool_name=tool_name, outcome="error").inc()
                span.record_exception(e)
                raise
    return wrapper
```

**Usage in all tool files:**
```python
from tool_library.decorators.traced_tool import traced_tool

@traced_tool
async def check_drug_interactions(drug_a: str, drug_b: str) -> InteractionResult:
    ...
```

---

## Phase 3 — Tier 3: Portal / SDK / Supporting Systems

---

### 3.1 `citizen-portal` — 2/10 → 7/10

**Priority:** `P2` | **Effort:** `M`

Health endpoint and audit present. Need: OTel, Prometheus, structured logging, correlation IDs, Sentry, alerting.

#### Changes

**`main.py`** — add:
```python
from symphonix_bridge_sdk.observability import (
    configure_logging, init_sentry, init_tracer,
    CorrelationIdMiddleware, PrometheusMetrics
)
configure_logging("citizen-portal")
init_sentry("citizen-portal")
init_tracer("citizen-portal")
app.add_middleware(CorrelationIdMiddleware)
metrics = PrometheusMetrics("citizen-portal")
app.mount("/metrics", metrics.metrics_app())
```

**Frontend (React) — `src/sentry.ts`**:
```typescript
import * as Sentry from "@sentry/react";

Sentry.init({
  dsn: import.meta.env.VITE_SENTRY_DSN,
  environment: import.meta.env.VITE_ENVIRONMENT,
  integrations: [Sentry.browserTracingIntegration()],
  tracesSampleRate: 0.1,
  beforeSend(event) {
    // Strip PHI fields from Sentry breadcrumbs
    if (event.breadcrumbs?.values) {
      event.breadcrumbs.values = event.breadcrumbs.values.map(b => ({
        ...b,
        data: undefined, // Don't ship breadcrumb data
      }));
    }
    return event;
  },
});
```

---

### 3.2 `csaa` — 0/10 → 7/10

**Priority:** `P3` | **Effort:** `L`

All pillars absent. Full baseline implementation.

#### Changes

Same pattern as `scheduling-gateway` (full greenfield). Apply all imports from `symphonix-bridge-sdk` observability package. Add clinical admin-specific audit logging for user and permission changes.

**`api/admin_router.py`**:
```python
@router.post("/users/{user_id}/permissions")
async def update_permissions(user_id: str, permissions: PermissionUpdate, admin=Depends(get_admin)):
    audit.log(action="U", resource_type="UserPermission", resource_id=user_id,
              actor_id=admin.id, details={"permissions": permissions.dict()})
    ...
```

---

### 3.3 `design-system` — 0/10 → 2/10

**Priority:** `P4` | **Effort:** `S`

Only applicable gap: React error boundary reporting to Sentry.

#### Changes

**`packages/design-system/src/sentry.ts`**:
```typescript
import * as Sentry from "@sentry/react";

export function initDesignSystemErrorTracking(dsn: string) {
  if (typeof window !== "undefined" && dsn) {
    Sentry.init({ dsn, environment: process.env.NODE_ENV });
  }
}
```

**`packages/design-system/src/components/ErrorBoundary.tsx`**:
```tsx
import * as Sentry from "@sentry/react";
export const SymphonixErrorBoundary = Sentry.withErrorBoundary;
```

**Storybook CI** — add Storybook test coverage report to CI pipeline so component regression is visible in dashboards.

---

### 3.4 `erp` — 1/10 → 7/10

**Priority:** `P3` | **Effort:** `L`

Health endpoint present. Need: OTel, Prometheus, structured logging, audit trail, correlation IDs, Sentry, alerting.

#### Changes

**`main.py`**:
```python
from symphonix_bridge_sdk.observability import (
    configure_logging, init_sentry, init_tracer,
    CorrelationIdMiddleware, PrometheusMetrics, AuditLogger
)
configure_logging("erp")
init_sentry("erp")
init_tracer("erp")
app.add_middleware(CorrelationIdMiddleware)
metrics = PrometheusMetrics("erp")
app.mount("/metrics", metrics.metrics_app())
audit = AuditLogger("erp")
```

**`api/financial_router.py`** — financial governance audit:
```python
@router.post("/transactions")
async def create_transaction(tx: Transaction, user=Depends(get_current_user)):
    audit.log(action="C", resource_type="FinancialTransaction", resource_id=str(tx.id),
              actor_id=user.id, details={"amount": tx.amount, "cost_centre": tx.cost_centre})
    ...
```

---

### 3.5 `picis-system` — 0/10 → 8/10

**Priority:** `P1` | **Effort:** `XL`

All pillars absent. **Highest unaddressed clinical risk**: perioperative audit is CQC-mandated. Full implementation required.

#### Changes

Same full baseline as `gp-system`. Additional perioperative-specific items:

**New file `observability/picis_metrics.py`**:
```python
from prometheus_client import Counter, Histogram, Gauge
from symphonix_bridge_sdk.observability.metrics import _registry

surgical_cases_total = Counter(
    "picis_surgical_cases_total", "Surgical cases", ["procedure_type", "outcome"], registry=_registry
)
anaesthetic_events = Counter(
    "picis_anaesthetic_events_total", "Anaesthetic events", ["event_type"], registry=_registry
)
pacu_length_of_stay = Histogram(
    "picis_pacu_los_minutes", "PACU length of stay minutes", registry=_registry
)
theatre_utilisation = Gauge(
    "picis_theatre_utilisation_ratio", "Theatre utilisation 0–1", ["theatre_id"], registry=_registry
)
```

**`alerting/picis-rules.yml`**:
```yaml
groups:
  - name: picis.patient-safety
    rules:
      - alert: PICISDown
        expr: up{job="picis-system"} == 0
        for: 30s
        labels:
          severity: critical
          team: perioperative
          pagerduty: "true"
        annotations:
          summary: "PICIS system down — perioperative care record unavailable"
```

---

### 3.6 `prompt-engine` — 0/10 → 7/10

**Priority:** `P1` | **Effort:** `L`

All pillars absent. LLM-specific observability required in addition to baseline. The prompt engine is foundational to all AI agent work.

#### Changes

**`main.py`**:
```python
from symphonix_bridge_sdk.observability import (
    configure_logging, init_sentry, init_tracer,
    CorrelationIdMiddleware, PrometheusMetrics, make_health_router, AuditLogger
)
configure_logging("prompt-engine")
init_sentry("prompt-engine")
init_tracer("prompt-engine")
app.add_middleware(CorrelationIdMiddleware)
metrics = PrometheusMetrics("prompt-engine")
app.mount("/metrics", metrics.metrics_app())
app.include_router(make_health_router("prompt-engine"))
audit = AuditLogger("prompt-engine")
```

**New file `observability/llm_metrics.py`** — LLM-specific (OTel Gen AI semantic conventions):
```python
from prometheus_client import Counter, Histogram, Gauge
from symphonix_bridge_sdk.observability.metrics import _registry

prompt_renders_total = Counter(
    "prompt_renders_total", "Prompt template renders", ["template_id", "model"], registry=_registry
)
prompt_tokens_total = Counter(
    "prompt_tokens_total", "Tokens in rendered prompts", ["template_id", "model"], registry=_registry
)
prompt_latency = Histogram(
    "prompt_render_duration_seconds", "Prompt render latency", ["template_id"], registry=_registry
)
active_prompt_version = Gauge(
    "prompt_active_version", "Active prompt version number", ["template_id"], registry=_registry
)
```

**`services/prompt_service.py`** — audit prompt version changes:
```python
@traced_tool
async def publish_prompt_version(template_id: str, version: PromptVersion, user_id: str):
    audit.log(action="U", resource_type="PromptTemplate", resource_id=template_id,
              actor_id=user_id, details={"version": version.number, "model": version.target_model})
    ...
```

---

### 3.7 `symphonix-bridge-sdk` — 0/10 → 8/10

**Priority:** `P0` | **Effort:** `XL`

Already covered in Phase 0 (Section 0.1). The SDK itself needs the observability package added to it. Additionally:

**OTel context propagation for all HTTP clients in the SDK:**
```python
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor

HTTPXClientInstrumentor().instrument()
RequestsInstrumentor().instrument()
```

This ensures any HTTP call made by the bridge SDK carries W3C Trace Context headers automatically, enabling end-to-end tracing through external integration partners.

---

### 3.8 `triage-api` — 0/10 → 9/10

**Priority:** `P0` | **Effort:** `XL`

All pillars absent. **Highest value + highest risk** repo in the entire portfolio. Every triage decision is a CQC-auditable clinical action. Full implementation + HITL safeguard.

#### Changes

**`main.py`**:
```python
from symphonix_bridge_sdk.observability import (
    configure_logging, init_sentry, init_tracer,
    CorrelationIdMiddleware, PrometheusMetrics, make_health_router, AuditLogger
)

configure_logging("triage-api")
init_sentry("triage-api")
init_tracer("triage-api", otlp_endpoint=settings.OTEL_ENDPOINT)

app = FastAPI()
app.add_middleware(CorrelationIdMiddleware)
metrics = PrometheusMetrics("triage-api")
app.mount("/metrics", metrics.metrics_app())
app.include_router(make_health_router("triage-api"))
audit = AuditLogger("triage-api")
```

**New file `observability/triage_metrics.py`**:
```python
from prometheus_client import Counter, Histogram, Gauge
from symphonix_bridge_sdk.observability.metrics import _registry

triage_assessments_total = Counter(
    "triage_assessments_total", "Triage assessments performed",
    ["acuity_level", "outcome"], registry=_registry
)
triage_duration = Histogram(
    "triage_assessment_duration_seconds", "Triage assessment latency", registry=_registry
)
triage_queue_length = Gauge(
    "triage_queue_length", "Patients awaiting triage", registry=_registry
)
```

**`api/triage_router.py`** — every triage call is a clinical audit event:
```python
@router.post("/triage")
async def perform_triage(request: TriageRequest, clinician=Depends(get_current_clinician)):
    with tracer.start_as_current_span("triage.assess") as span:
        span.set_attribute("triage.chief_complaint", request.chief_complaint)
        span.set_attribute("triage.acuity_category", request.acuity_hint)

        result = await triage_service.assess(request)

        audit.log(
            action="E",
            resource_type="TriageAssessment",
            resource_id=result.assessment_id,
            actor_id=clinician.id,
            outcome="0" if result.success else "8",
            details={
                "acuity_level": result.acuity,
                "recommended_care_area": result.care_area,
                "ai_assisted": result.ai_assisted,
                "clinician_confirmed": result.clinician_confirmed,  # HITL gate
            },
        )
        triage_assessments_total.labels(acuity_level=result.acuity, outcome="complete").inc()
        return result
```

**`alerting/triage-rules.yml`**:
```yaml
groups:
  - name: triage.patient-safety
    rules:
      - alert: TriageAPIDown
        expr: up{job="triage-api"} == 0
        for: 30s
        labels:
          severity: critical
          team: emergency
          pagerduty: "true"
        annotations:
          summary: "CRITICAL: Triage API is DOWN — patient safety risk"
      - alert: TriageQueueBacklog
        expr: triage_queue_length > 10
        for: 5m
        labels:
          severity: warning
          team: emergency
        annotations:
          summary: "Triage queue > 10 patients — surge protocol may be needed"
```

---

## Phase 4 — External Organisation Repositories

---

### 4.1 `kenya-uhc-implementation` — 0/10 → 6/10

**Priority:** `P3` | **Effort:** `L`

Apply baseline observability. UHC-specific:
- Audit trail for enrolment and claims events (accountability to Kenya MoH/NHIF funders)
- Gauge for UHC coverage rate (enrolees vs. target population)
- Alerting if data pipeline stops (WHO reporting dependency)

---

### 4.2 `Tedam-Technologies-UK-Ltd/elocute` — 0/10 → 5/10

**Priority:** `P4` | **Effort:** `M`

Apply: structured logging, Sentry (session errors), health endpoint, OTel. Speech therapy session logging (session duration, exercise completion rate, pronunciation score distribution) as custom metrics.

---

### 4.3 `GmailTedam/africa-marketplace` — 0/10 → 5/10

**Priority:** `P4` | **Effort:** `M`

Apply baseline observability. Marketplace-specific:
- Order funnel metrics (product views → cart → checkout → payment)
- Sentry for both frontend and backend
- Fraud detection counter (failed payment attempts per user)

---

## Phase 5 — Agent Activation (After Phase 1–4 Complete)

---

### 5.1 Activate BulletTrain BEVAN Agents

**Effort:** `XL` | **Priority:** `P1`

Wire existing agent stubs to Azure AI Foundry:

```python
# agents/dx_agent.py
from azure.ai.inference import ChatCompletionsClient
from azure.core.credentials import AzureKeyCredential

client = ChatCompletionsClient(
    endpoint=os.environ["AZURE_AI_ENDPOINT"],
    credential=AzureKeyCredential(os.environ["AZURE_AI_KEY"]),
)

async def assess_diagnosis(patient_summary: str) -> DiagnosticAssessment:
    with tracer.start_as_current_span("gen_ai.bevan.dx_assess") as span:
        span.set_attribute("gen_ai.system", "azure_openai")
        response = await client.complete(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": BEVAN_SYSTEM_PROMPT},
                {"role": "user", "content": patient_summary},
            ],
        )
        token_usage.labels(model="gpt-4o", direction="input").inc(response.usage.prompt_tokens)
        token_usage.labels(model="gpt-4o", direction="output").inc(response.usage.completion_tokens)
        return DiagnosticAssessment.from_response(response)
```

---

### 5.2 Build Triage AI Agent

**Effort:** `XL` | **Priority:** `P1`

Extend `triage-api` with LLM-grounded triage reasoning. **Mandatory HITL**: AI recommendation is shown to triaging clinician; clinician must confirm before it is recorded.

```python
# services/ai_triage_service.py
from mcp import ClientSession
from tool_library.tools import assess_chief_complaint, calculate_esi_score

async def ai_triage_assist(request: TriageRequest) -> AITriageRecommendation:
    """Returns a recommendation; clinician must confirm via /triage/confirm endpoint."""
    async with ClientSession() as session:
        esi = await calculate_esi_score(
            chief_complaint=request.chief_complaint,
            vitals=request.vitals,
        )
        rationale = await assess_chief_complaint(
            complaint=request.chief_complaint,
            esi=esi,
        )
    return AITriageRecommendation(
        esi_level=esi.level,
        rationale=rationale,
        requires_clinician_confirmation=True,  # Always True
    )
```

---

### 5.3 Register All Agents in GHARRA

**Effort:** `M` | **Priority:** `P1`

Once each agent is activated, register in `global-agent-registry`:

```python
# Shared startup pattern for all agents:
from gharra_client import AgentRegistration, register_agent

await register_agent(AgentRegistration(
    agent_id="triage-api-agent",
    display_name="Symphonix Triage Agent",
    capabilities=["triage.assess", "triage.esi_score"],
    protocols=["a2a/1.0", "mcp/1.0"],
    health_endpoint="https://triage-api/health",
    tool_manifest_url="https://triage-api/.well-known/mcp.json",
))
```

---

## Summary: Target State Per Repository

| Repository | Current | Target | Phase | Effort |
|-----------|---------|--------|-------|--------|
| ambulance-ems | 5/10 | 9/10 | P1 | M |
| appointment-system | 1/10 | 8/10 | P1 | L |
| BulletTrain | 4/10 | 10/10 | P1 | L |
| clinical-pathways | 2/10 | 8/10 | P1 | L |
| eps | 5/10 | 9/10 | P1 | M |
| etps | 3/10 | 8/10 | P1 | M |
| gp-system | 0/10 | 9/10 | P1 | XL |
| HMIS | 1/10 | 7/10 | P2 | L |
| insurance-eclaims | 3/10 | 8/10 | P2 | M |
| lis | 5/10 | 9/10 | P1 | M |
| pacs-ris | 5/10 | 9/10 | P1 | M |
| pharmacy-system | 5/10 | 9/10 | P1 | M |
| analytics-bi | 2/10 | 8/10 | P2 | L |
| caid-agent | 2/10 | 9/10 | P1 | L |
| global-agent-registry | 3/10 | 9/10 | P1 | M |
| health-agent-workspace | 0/10 | 6/10 | P3 | M |
| nexus-a2a-protocol | 3/10 | 9/10 | P1 | L |
| provider-portal | 3/10 | 8/10 | P2 | M |
| REA-Agent-mcp | 1/10 | 7/10 | P2 | L |
| scheduling-gateway | 0/10 | 8/10 | P1 | L |
| signalbox-mcp | 0/10 | 7/10 | P1 | L |
| supply-chain-erp | 3/10 | 8/10 | P2 | M |
| tool-library | 3/10 | 9/10 | P1 | M |
| citizen-portal | 2/10 | 7/10 | P2 | M |
| csaa | 0/10 | 7/10 | P3 | L |
| design-system | 0/10 | 2/10 | P4 | S |
| erp | 1/10 | 7/10 | P3 | L |
| picis-system | 0/10 | 8/10 | P1 | XL |
| prompt-engine | 0/10 | 7/10 | P1 | L |
| symphonix-bridge-sdk | 0/10 | 8/10 | P0 | XL |
| triage-api | 0/10 | 9/10 | P0 | XL |
| kenya-uhc-implementation | 0/10 | 6/10 | P3 | L |
| elocute | 0/10 | 5/10 | P4 | M |
| africa-marketplace | 0/10 | 5/10 | P4 | M |

**Total estimated effort to reach target state across all 34 repos:**
- Phase 0 (shared infrastructure): ~5 days
- Phase 1 (Tier 1 clinical, 12 repos): ~20 days
- Phase 2 (Tier 2 platform, 11 repos): ~15 days
- Phase 3 (Tier 3 supporting, 8 repos): ~10 days
- Phase 4 (external org repos, 3 repos): ~5 days
- Phase 5 (agent activation, 3 agents): ~10 days
- **Total: ~65 engineering days** (~13 weeks at 5 engineers)

---

*All code patterns reference `symphonix-bridge-sdk` observability package defined in Phase 0. All clinical audit patterns use the HL7 FHIR AuditEvent model validated in `etps`. All Prometheus metric names follow the [Prometheus naming conventions](https://prometheus.io/docs/practices/naming/). All OTel agent spans use the [OpenTelemetry Semantic Conventions for Generative AI](https://opentelemetry.io/docs/specs/semconv/gen-ai/).*
