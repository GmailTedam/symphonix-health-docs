# Prompt Engineering System for BulletTrain Services

## Executive Summary

This document defines a **prompt engineering system** for the BulletTrain health platform ecosystem — integrating a formal Prompt-Orchestrator DSL with a research-backed clause library. It replaces two prior documents (a clause catalogue and a DSL specification) by merging them into a single implementable reference.

The system improves performance, reliability, and accuracy of AI services across:
- **BulletTrain** — healthcare interoperability and orchestration engine
- **Nexus A2A Protocol** — agent-to-agent communication
- **Global Agent Registry** — trust and identity layer
- **Clinical Pathways** — care coordination workflows
- **GHARRA/Conductor** — scenario execution and validation

### Design Principles (Evidence-Based)

These principles are grounded in 2025-2026 prompt engineering research:

1. **Context engineering over prompt wording** — What data you feed matters more than how you phrase the request (Anthropic, 2025). Organize context first, queries last.
2. **Structured examples over complex chains** — 3-5 well-chosen examples yield 10-20% improvement. Complex recursive chains rarely beat clear direct instructions (Wharton Generative AI Lab, 2025).
3. **XML structuring for tool interactions** — Reduces misinterpretation by 5-15% on parsing tasks (arxiv 2411.10541).
4. **Adaptive thinking over manual forcing** — Let models decide reasoning depth. Extended thinking improves Claude Sonnet from 42.2% to 61.4% on real-world tasks (Anthropic, 2025).
5. **Empirical validation over intuition** — Every prompt spec must have measurable success criteria. Test before deploying.

---

## 1. Core Concepts

### 1.1 Prompt DSL Entities

| Entity | Purpose | Key Fields |
|--------|---------|------------|
| **PromptSpec** | Complete prompt definition | role, template, clauses, reasoning_modes, policies, model_preferences |
| **Template** | Reusable prompt scaffold with placeholders | sections, content, variables |
| **Clause** | Atomic reasoning instruction | instruction, tags, evidence_level |
| **ReasoningMode** | Named collection of clauses for a thinking style | default_clauses, trigger_clause |
| **Policy** | Constraint/guardrail on prompts or outputs | rules, enforcement |
| **PromptExecution** | Runtime log of a prompt invocation | prompt_type, model, result, metrics |

### 1.2 What Changed from Prior Documents

| Prior Document | Strength Kept | Weakness Removed |
|---|---|---|
| Clause Catalogue (.docx) | All 12 clause types, thinking modes, composite patterns | Removed repetitive examples, ungrounded claims, speculative multi-chain techniques |
| Prompt-Orchestrator DSL (.md) | YAML schemas, execution lifecycle, API contracts, governance | Updated model references to Claude 4.6, populated empty abstractions with real clause content |

---

## 2. YAML Schema Specification

```
apiVersion: reasoning/v1
```

### 2.1 PromptSpec

```yaml
apiVersion: reasoning/v1
kind: Prompt
metadata:
  name: <prompt_name>       # unique identifier
  version: <semver>          # e.g. 1.0.0
spec:
  description: <string>
  role: <string>             # persona (e.g. "senior_systems_architect")
  context: <string>          # static context or system instructions
  template: <template_name>  # reference to a Template
  reasoning_modes: [<mode>, ...]
  clauses: [<clause>, ...]
  policies: [<policy>, ...]
  output_structure: [<section>, ...]
  model_preferences:
    - name: <model_id>       # e.g. claude-opus-4-6, claude-sonnet-4-6
      temperature: <0.0-1.0>
      extended_thinking: <bool>     # enable adaptive thinking
      thinking_budget: <int>        # max thinking tokens (0 = adaptive)
    - name: <fallback_model_id>
      temperature: <float>
  variables: {<name>: <value>, ...}
  examples:                  # 3-5 structured examples (evidence-backed)
    - input: <string>
      output: <string>
  execution_settings:
    default:
      max_tokens: <int>
      stop: [<strings>]
  success_criteria:          # required — what good output looks like
    - <measurable criterion>
```

### 2.2 Template

```yaml
apiVersion: reasoning/v1
kind: Template
metadata:
  name: <template_name>
spec:
  description: <string>
  sections:
    - <section_name>: <string or placeholder>
  content: >-
    <multiline text with {variable} placeholders>
```

### 2.3 Clause

```yaml
apiVersion: reasoning/v1
kind: Clause
metadata:
  name: <clause_name>
spec:
  instruction: <string>      # the actual prompt text
  tags: [<tag>, ...]
  evidence_level: <strong|moderate|emerging>  # research backing
  reasoning_dimension: <string>  # what cognitive mode it activates
```

### 2.4 ReasoningMode

```yaml
apiVersion: reasoning/v1
kind: ReasoningMode
metadata:
  name: <mode_name>
spec:
  description: <string>
  trigger_clause: <string>   # the phrase that activates this mode
  default_clauses: [<clause>, ...]
  typical_use: [<string>, ...]
```

### 2.5 Policy

```yaml
apiVersion: reasoning/v1
kind: Policy
metadata:
  name: <policy_name>
spec:
  rules:
    - <human-readable rule or check reference>
  enforcement: <"reject"|"sanitize"|"warn">
```

---

## 3. Clause Library

This is the core content — the actual prompt instructions that populate the DSL. Each clause is graded by evidence level.

### 3.1 Tier 1: Strong Evidence (Reliably improve output quality)

These clauses are supported by multiple studies and Anthropic's own guidance.

#### First Principles Reasoning
```yaml
name: first_principles
instruction: "Derive the answer from first principles."
evidence_level: strong
reasoning_dimension: conceptual_analysis
```
**Effect:** Forces reasoning from fundamental concepts rather than surface patterns. Produces structured logic chains. Most effective single clause for analytical depth.

#### Structured Output
```yaml
name: structured_output
instruction: "Structure your response using the following sections: {output_structure}"
evidence_level: strong
reasoning_dimension: organization
```
**Effect:** XML/section-structured outputs are 5-15% more accurate and parseable.

#### Explicit Context Anchoring
```yaml
name: context_anchor
instruction: "Given the following constraints: {constraints}. Your analysis must account for each of these."
evidence_level: strong
reasoning_dimension: constraint_satisfaction
```
**Effect:** Anchors reasoning in specific assumptions. Prevents drift. Anthropic recommends this as a top-tier technique.

#### Few-Shot Examples
```yaml
name: few_shot
instruction: "Here are examples of the expected analysis format: {examples}"
evidence_level: strong
reasoning_dimension: pattern_demonstration
```
**Effect:** 3-5 well-chosen examples consistently yield 10-20% improvement across tasks.

#### Role Assignment
```yaml
name: role_assignment
instruction: "You are acting as a {role} with expertise in {domain}."
evidence_level: strong
reasoning_dimension: domain_activation
```
**Effect:** Focuses model behavior and vocabulary. 5-10% improvement in domain-appropriate responses.

### 3.2 Tier 2: Moderate Evidence (Effective in specific contexts)

#### Hidden Assumptions
```yaml
name: hidden_assumptions
instruction: "Identify hidden assumptions in this analysis."
evidence_level: moderate
reasoning_dimension: critical_thinking
```
**Effect:** Reveals implicit biases. Particularly valuable for architecture reviews and policy evaluation.

#### Second-Order Effects
```yaml
name: second_order_effects
instruction: "Identify second-order effects that may emerge."
evidence_level: moderate
reasoning_dimension: systems_thinking
```
**Effect:** Encourages analysis of indirect consequences. Useful for platform strategy and ecosystem analysis.

#### Counter-Arguments
```yaml
name: counter_arguments
instruction: "Identify the strongest counterarguments to this position."
evidence_level: moderate
reasoning_dimension: adversarial_reasoning
```
**Effect:** Produces risk analysis, logical critique, adversarial reasoning. Useful for architecture design and strategy validation.

#### Evidence Grounding
```yaml
name: evidence_grounding
instruction: "Support conclusions with specific examples, mechanisms, or empirical evidence."
evidence_level: moderate
reasoning_dimension: evidential_reasoning
```
**Effect:** Reduces unsupported claims. Pushes model toward case studies and concrete mechanisms.

#### Precision
```yaml
name: precision
instruction: "Be precise about mechanisms. Distinguish between {concept_a} and {concept_b}. Define key terms."
evidence_level: moderate
reasoning_dimension: specificity
```
**Effect:** Reduces vague language. Drives technical depth and clear definitions.

#### Scenario Reasoning
```yaml
name: scenario_reasoning
instruction: "Consider a scenario where {scenario_description}. How would the system behave?"
evidence_level: moderate
reasoning_dimension: simulation
```
**Effect:** Activates scenario reasoning for architecture design, policy modelling, system simulation.

### 3.3 Tier 3: Emerging Evidence (Useful but validate empirically)

These techniques show promise but have limited or mixed research support. Use them, but measure their impact.

#### Cognitive Forcing
```yaml
name: cognitive_forcing
instruction: >
  Before giving your conclusion:
  1. Identify the obvious interpretation.
  2. Identify at least one alternative interpretation.
  3. Examine assumptions underlying each.
  4. Then provide your final assessment.
evidence_level: emerging
reasoning_dimension: deliberate_analysis
```
**Effect:** Reduces premature conclusions. Research (Croskerry, 2003) supports this in clinical reasoning; LLM evidence is promising but limited.

#### Challenge the Obvious
```yaml
name: challenge_obvious
instruction: "Challenge the most obvious interpretation of this system's role."
evidence_level: emerging
reasoning_dimension: contrarian_analysis
```
**Effect:** Prevents shallow conclusions. Can produce unexpected insights but may also produce forced contrarianism.

#### Long-Term Evolution
```yaml
name: long_term_evolution
instruction: "Project how this system might evolve over the next decade."
evidence_level: emerging
reasoning_dimension: strategic_foresight
```
**Effect:** Shifts from present functionality to future trajectory. Speculative but useful for strategic planning.

#### Adjacent Possible
```yaml
name: adjacent_possible
instruction: "Identify innovations that become possible because this system exists, even if unintended."
evidence_level: emerging
reasoning_dimension: innovation_discovery
```
**Effect:** Based on Kauffman's complexity theory. Produces future-oriented insights about ecosystems.

#### Synthesis Across Sources
```yaml
name: synthesis
instruction: "Synthesize insights across these {count} inputs into a unified interpretation."
evidence_level: emerging
reasoning_dimension: integrative_reasoning
```
**Effect:** Promotes novel connections between concepts. Most effective when combined with structured output.

---

## 4. Reasoning Modes

Reasoning modes are named collections of clauses. When a mode is activated, its clauses are injected into the prompt.

### 4.1 Mode Definitions

```yaml
# --- Systems Thinking ---
name: systems_thinking
trigger_clause: "Analyse the system as a complex interacting whole."
default_clauses: [first_principles, second_order_effects, hidden_assumptions]
typical_use: [infrastructure_platforms, healthcare_ecosystems, digital_transformation]

# --- Critical Review ---
name: critical_review
trigger_clause: "Identify the strongest counterarguments."
default_clauses: [counter_arguments, hidden_assumptions, evidence_grounding]
typical_use: [architecture_reviews, policy_evaluation, investment_decisions]

# --- First Principles ---
name: first_principles_mode
trigger_clause: "Derive the answer from first principles."
default_clauses: [first_principles, precision, structured_output]
typical_use: [engineering_analysis, system_design, root_cause_investigation]

# --- Adversarial ---
name: adversarial_thinking
trigger_clause: "Assume the role of an attacker or critic."
default_clauses: [counter_arguments, scenario_reasoning, hidden_assumptions]
typical_use: [security_reviews, risk_assessment, stress_testing]

# --- Strategic Analysis ---
name: strategic_analysis
trigger_clause: "Evaluate the long-term strategic significance."
default_clauses: [second_order_effects, long_term_evolution, adjacent_possible]
typical_use: [platform_strategy, ecosystem_analysis, investment_evaluation]

# --- Scientific Method ---
name: scientific_method
trigger_clause: "Evaluate hypotheses against available evidence."
default_clauses: [first_principles, evidence_grounding, hidden_assumptions, counter_arguments]
typical_use: [research_analysis, clinical_evaluation, data_interpretation]

# --- Design Thinking ---
name: design_thinking
trigger_clause: "Consider the problem from the user's perspective."
default_clauses: [scenario_reasoning, precision, synthesis]
typical_use: [product_design, workflow_optimization, user_experience]

# --- Failure Analysis ---
name: failure_analysis
trigger_clause: "Consider plausible failure scenarios."
default_clauses: [scenario_reasoning, hidden_assumptions, counter_arguments]
typical_use: [reliability_engineering, incident_review, system_hardening]
```

### 4.2 Composite Patterns (Evidence-Based)

Research shows that the strongest prompts combine **3 elements**:

1. **Intent clause** — what the model should do ("Make the strongest case for...")
2. **Context clause** — what constraints apply ("Given that patient data quality is incomplete...")
3. **Reasoning clause** — how to think ("Derive from first principles...")

Adding more than 3-4 clause types per prompt shows diminishing returns and can degrade coherence (Wharton, 2025).

**Recommended composite for analytical tasks:**
```
Role: {domain expert}
Task: {specific problem}
Context: {key constraints}
Reasoning: Derive from first principles. Identify hidden assumptions. Consider second-order effects.
Output: {structured sections}
```

**Recommended composite for strategic tasks:**
```
Role: {strategist role}
Task: {evaluation objective}
Context: {system description and constraints}
Reasoning: Challenge the obvious interpretation. Identify what the designers may have unintentionally built. Project evolution over the next decade.
Output: {structured sections}
```

---

## 5. Execution Lifecycle

```
User Input/Task
    |
    v
[1. Classify] --> Determine prompt type or intent
    |
    v
[2. Select Template] --> Retrieve PromptSpec from registry
    |
    v
[3. Inject Clauses] --> Insert clauses from spec + active ReasoningModes
    |
    v
[4. Assemble Prompt] --> Render template with variables, clauses, context
    |                     DATA FIRST, QUERY LAST (Anthropic guidance)
    v
[5. Route to Model] --> Select model from preferences (Claude 4.6 primary)
    |
    v
[6. Execute] --> Call LLM with adaptive thinking enabled
    |
    v
[7. Validate] --> Check output against policies and success_criteria
    |
    v
[8. Log & Learn] --> Record PromptExecution, update metrics
```

### Key Rules

- **Data placement:** Put context/data at the top of assembled prompts. Queries and instructions go at the bottom. This improves performance by up to 30% on long-context tasks (Anthropic, 2025).
- **XML structuring:** Use `<context>`, `<instructions>`, `<examples>`, `<output_format>` tags for multi-part prompts.
- **Model selection:** Default to `claude-opus-4-6` for complex reasoning, `claude-sonnet-4-6` for high-throughput tasks, `claude-haiku-4-5` for classification/routing.
- **Thinking budget:** Enable adaptive thinking by default. Only set fixed budgets for latency-critical paths.
- **Policy enforcement:** Sanitize inputs before assembly (block injection vectors). Validate outputs against policies after execution.

---

## 6. Prompt Specs for BulletTrain Services

### 6.1 Architecture Analysis

```yaml
apiVersion: reasoning/v1
kind: Prompt
metadata:
  name: architecture-analysis
  version: 2.0.0
spec:
  description: "Analyse system architecture for BulletTrain components."
  role: "senior_systems_architect"
  context: "You are evaluating distributed healthcare orchestration infrastructure."
  template: analysis_template
  reasoning_modes: [first_principles_mode, systems_thinking, critical_review]
  clauses: [hidden_assumptions, second_order_effects, evidence_grounding]
  policies: [no_pii, no_country_shaming]
  output_structure: [overview, architecture_assessment, risks, opportunities, recommendations]
  model_preferences:
    - name: claude-opus-4-6
      temperature: 0.3
      extended_thinking: true
      thinking_budget: 0  # adaptive
    - name: claude-sonnet-4-6
      temperature: 0.4
  examples:
    - input: "Evaluate the BulletTrain orchestration engine's workflow coordination."
      output: |
        ## Overview
        BulletTrain implements a distributed workflow coordination pattern...
        ## Architecture Assessment
        The system acts as a control plane for healthcare service orchestration...
  success_criteria:
    - "Identifies at least 3 architectural patterns"
    - "Provides evidence-backed risk assessment"
    - "Recommendations are actionable and specific"
  execution_settings:
    default:
      max_tokens: 4000
```

### 6.2 Clinical Pathway Validation

```yaml
apiVersion: reasoning/v1
kind: Prompt
metadata:
  name: clinical-pathway-validation
  version: 1.0.0
spec:
  description: "Validate clinical pathway definitions against medical evidence and system constraints."
  role: "clinical_informatics_specialist"
  context: >
    You are validating clinical pathways for a digital health platform.
    Patient data quality may be incomplete. Historical records may be missing.
    Pathways must work across different healthcare systems with varying capabilities.
  template: validation_template
  reasoning_modes: [scientific_method, failure_analysis]
  clauses: [first_principles, hidden_assumptions, scenario_reasoning, evidence_grounding]
  policies: [no_pii, clinical_safety, no_country_shaming]
  output_structure: [pathway_assessment, evidence_gaps, failure_scenarios, recommendations]
  model_preferences:
    - name: claude-opus-4-6
      temperature: 0.2
      extended_thinking: true
  success_criteria:
    - "All clinical decision points have evidence citations"
    - "At least 2 failure scenarios identified per pathway"
    - "Edge cases for incomplete data are addressed"
  execution_settings:
    default:
      max_tokens: 3000
```

### 6.3 Agent Protocol Analysis (Nexus A2A)

```yaml
apiVersion: reasoning/v1
kind: Prompt
metadata:
  name: nexus-protocol-analysis
  version: 1.0.0
spec:
  description: "Analyse agent-to-agent protocol interactions for correctness and emergent behavior."
  role: "distributed_systems_engineer"
  context: >
    You are analysing the Nexus A2A protocol — an agent-to-agent communication
    protocol enabling AI agents to communicate across organisational boundaries.
    The protocol must handle partial failures, trust boundaries, and message ordering.
  template: protocol_analysis_template
  reasoning_modes: [systems_thinking, adversarial_thinking, failure_analysis]
  clauses: [first_principles, counter_arguments, scenario_reasoning, second_order_effects]
  policies: [no_pii, security_review]
  output_structure: [protocol_assessment, failure_modes, security_analysis, scalability, recommendations]
  model_preferences:
    - name: claude-opus-4-6
      temperature: 0.2
      extended_thinking: true
  success_criteria:
    - "Identifies message ordering and delivery guarantees"
    - "At least 3 failure modes analysed"
    - "Security boundary analysis included"
```

### 6.4 Risk Assessment

```yaml
apiVersion: reasoning/v1
kind: Prompt
metadata:
  name: risk-assessment
  version: 2.0.0
spec:
  description: "Perform risk assessment for healthcare system components."
  role: "security_analyst"
  context: >
    You are performing risk assessment for healthcare infrastructure that
    handles sensitive patient data across multiple jurisdictions.
  template: risk_template
  reasoning_modes: [adversarial_thinking, failure_analysis]
  clauses: [hidden_assumptions, counter_arguments, scenario_reasoning, evidence_grounding]
  policies: [no_pii, confidentiality_required, no_country_shaming]
  output_structure: [threats, likelihood, impact, existing_controls, recommended_mitigations]
  model_preferences:
    - name: claude-opus-4-6
      temperature: 0.2
      extended_thinking: true
  success_criteria:
    - "Each threat has likelihood and impact ratings"
    - "Mitigations are specific and implementable"
    - "Compliance considerations included"
```

### 6.5 Scenario Generation (GHARRA/Conductor)

```yaml
apiVersion: reasoning/v1
kind: Prompt
metadata:
  name: scenario-generation
  version: 1.0.0
spec:
  description: "Generate test scenarios in JSON format for BulletTrain validation."
  role: "quality_assurance_engineer"
  context: >
    Generate test scenarios following the BulletTrain reduced_json_matrices pattern.
    Output must be valid JSON, never CSV. Scenarios must cover edge cases
    including incomplete data, missing historical records, and cross-system failures.
  template: scenario_template
  reasoning_modes: [failure_analysis, systems_thinking]
  clauses: [scenario_reasoning, hidden_assumptions, precision]
  policies: [json_output_only, no_pii]
  output_structure: [scenario_matrix]
  model_preferences:
    - name: claude-sonnet-4-6
      temperature: 0.3
  examples:
    - input: "Generate scenarios for patient referral workflow"
      output: |
        [
          {
            "id": "referral_001",
            "description": "Standard referral with complete data",
            "preconditions": {"patient_data": "complete", "provider_registered": true},
            "steps": [...],
            "expected_outcome": "referral_accepted"
          }
        ]
  success_criteria:
    - "All output is valid JSON"
    - "100% of scenarios must pass when executed"
    - "Edge cases for incomplete data are included"
  execution_settings:
    default:
      max_tokens: 8000
```

---

## 7. Policies

```yaml
# --- No PII ---
name: no_pii
rules:
  - "Never include personally identifiable information in prompts or outputs."
  - "Use synthetic identifiers in examples."
enforcement: sanitize

# --- No Country Shaming ---
name: no_country_shaming
rules:
  - "Never name countries alongside their healthcare problems in marketing or analysis."
  - "Use 'your system' or 'healthcare systems facing X challenge' language instead."
enforcement: reject

# --- JSON Output Only ---
name: json_output_only
rules:
  - "Test scenarios must always be in JSON format, never CSV."
  - "Follow BulletTrain reduced_json_matrices pattern."
enforcement: reject

# --- Clinical Safety ---
name: clinical_safety
rules:
  - "Clinical recommendations must cite evidence."
  - "Flag uncertainty explicitly — never present uncertain guidance as definitive."
  - "Include contraindication checks for pathway modifications."
enforcement: reject

# --- Security Review ---
name: security_review
rules:
  - "Sanitize inputs for injection vectors."
  - "Never embed credentials or tokens in prompts."
  - "Flag potential data exfiltration patterns."
enforcement: reject

# --- Confidentiality ---
name: confidentiality_required
rules:
  - "Do not expose internal system details in external-facing outputs."
  - "Redact infrastructure specifics from reports."
enforcement: sanitize
```

---

## 8. API Contracts

### `POST /prompt/compose`

Assemble a prompt from a PromptSpec.

**Request:**
```json
{
  "promptType": "architecture-analysis",
  "context": {
    "system_description": "BulletTrain orchestration engine with FHIR adapters",
    "focus_area": "scalability under multi-tenant load"
  },
  "variables": {
    "audience": "engineering team"
  }
}
```

**Response (200):**
```json
{
  "promptText": "<context>...</context><instructions>...</instructions>",
  "model": "claude-opus-4-6",
  "estimatedTokens": 1200,
  "usedClauses": ["first_principles", "hidden_assumptions", "second_order_effects"],
  "usedModes": ["first_principles_mode", "systems_thinking", "critical_review"],
  "appliedPolicies": ["no_pii", "no_country_shaming"]
}
```

### `POST /prompt/optimize`

Refine an existing prompt using DSPy-style optimization.

**Request:**
```json
{
  "promptText": "Analyse the BulletTrain architecture.",
  "goals": ["specificity", "structured_output", "evidence_grounding"],
  "evaluationData": [
    {"input": "...", "expectedOutput": "...", "actualOutput": "...", "score": 0.7}
  ]
}
```

**Response (200):**
```json
{
  "optimizedPrompt": "...",
  "changeLog": "Added role assignment, structured output sections, evidence grounding clause.",
  "predictedImprovement": "~15% based on similar optimizations"
}
```

---

## 9. Governance

### Versioning
- All specs use semantic versioning.
- Stored in Git alongside application code.
- Changes require code review.

### Testing
- **Snapshot tests:** Given fixed template + clauses, does assembled prompt match expectations?
- **Output validation:** Run prompts against test inputs; verify outputs meet `success_criteria`.
- **Policy tests:** Verify that policy violations are caught and enforced.
- **Regression tests:** When updating clauses or templates, re-run validation suite.
- **100% pass requirement:** All generated scenarios must pass before delivery (per project standards).

### Metrics
- **Quality:** Task-specific metrics (accuracy, completeness, structural compliance).
- **Telemetry:** Clauses used, model selected, token count, latency, success/failure.
- **A/B testing:** Version prompt specs and compare success rates across versions.
- **Clause effectiveness:** Track which clauses correlate with higher output quality.

### Integration with Real Services
Per project standards: always use real services (Nexus, GHARRA, Conductor) for validation — never mocks or simulations. Rate limiting should be configurable, not worked around.

---

## 10. Implementation Path

### Phase 1: Clause Library (Immediate)
- Implement the Tier 1 clauses as reusable prompt fragments in the codebase.
- Add `success_criteria` to all existing prompts.
- Update model references to Claude 4.6 family.
- Enable adaptive thinking by default.

### Phase 2: Template System (Short-term)
- Create YAML-defined templates for the 5 prompt specs above.
- Build a simple template renderer (Jinja-based) that assembles prompts from specs.
- Add policy enforcement as pre/post-processing middleware.

### Phase 3: Orchestrator Service (Medium-term)
- Implement `/prompt/compose` and `/prompt/optimize` endpoints via FastAPI.
- Connect to prompt registry (start with file-based YAML, migrate to Neo4j if scale demands).
- Add telemetry and A/B testing infrastructure.

### Phase 4: Optimization (Ongoing)
- Integrate DSPy-style automated optimization for high-traffic prompt specs.
- Build clause effectiveness dashboard from telemetry data.
- Continuously refine clause library based on measured outcomes.

---

## Appendix A: Techniques Evaluated and Excluded

The following techniques from the original clause catalogue were evaluated against current research and either excluded or downgraded:

| Technique | Decision | Reason |
|-----------|----------|--------|
| 10+ step recursive chains | **Excluded** | Research shows diminishing returns past 3-4 reasoning steps. Simpler direct prompts often win (Wharton, 2025). |
| Multi-role simulation (5+ roles) | **Downgraded to 2-3 max** | Internal role diversity helps, but 5+ simulated analysts adds token cost without proportional quality gain. |
| "Assume designers underestimated their system" | **Moved to strategic-only** | Useful for investor/strategy contexts but produces forced insights in technical analysis. |
| "Technology historian" framing | **Excluded from defaults** | Speculative framing. Use only when explicitly doing strategic/vision work. |
| Meta-prompt framework (7-stage) | **Simplified to 4 stages max** | Models handle 3-4 structured stages well; 7 stages cause coherence degradation. |
| Raw Chain-of-Thought forcing | **Replaced by adaptive thinking** | Anthropic's adaptive thinking outperforms manual CoT triggers on Claude 4.6. |

## Appendix B: The Five Power Clauses

For quick reference, these five short phrases consistently produce the highest-quality analytical output:

1. **"Derive from first principles."** — Conceptual depth
2. **"Identify hidden assumptions."** — Critical thinking
3. **"Identify second-order effects."** — Systems thinking
4. **"Challenge the most obvious interpretation."** — Contrarian analysis
5. **"Project how this might evolve over the next decade."** — Strategic foresight

For most complex prompts, combining any 3 of these with a clear role, context, and structured output is sufficient.

## Appendix C: References

- Anthropic (2025). Claude Prompting Best Practices. platform.claude.com
- Anthropic (2025). Extended Thinking. platform.claude.com
- Brown, T. B., et al. (2020). Language models are few-shot learners. NeurIPS.
- Croskerry, P. (2003). Cognitive errors in diagnosis. Academic Medicine, 78(8).
- Kauffman, S. A. (2000). Investigations. Oxford University Press.
- Arthur, W. B. (2009). The Nature of Technology. Free Press.
- Baldwin, C. Y., & Clark, K. B. (2000). Design Rules: The Power of Modularity. MIT Press.
- White, J., Hays, S., & Schmidt, D. (2023). Prompt engineering patterns. IEEE Software, 40(5).
- Wharton Generative AI Lab (2025). The Decreasing Value of Chain of Thought. Tech Report.
- Does Prompt Formatting Have Any Impact on LLM Performance? (2024). arXiv:2411.10541.
- Madaan, A., et al. (2023). Self-Refine: Iterative Refinement with Self-Feedback. arXiv:2303.17651.
