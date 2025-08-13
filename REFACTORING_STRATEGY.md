# Refactoring Strategy

## 1. Goals
- Improve maintainability, extensibility, and consistency across modules
- Separate responsibilities among prompt construction, LLM invocation, and output persistence
- Increase testability and reliability while preserving current behavior and quality

## 2. Guiding Principles
- Single Responsibility: isolate domain logic, service orchestration, and I/O concerns
- Unidirectional Dependencies: Domain (models) → Services (business) → Infrastructure (I/O)
- Type Safety and Validation: prefer Pydantic models and explicit conversion utilities
- Observability by Default: structured logging, metrics, and clear error categorization
- Incremental Delivery: small, reviewable PRs with regression tests

## 3. Target Architecture
- Domain (Pydantic models): Question, GuideEntry, CoverLetterResponse, SaveDecision, AgentState (validated)
- Services:
  - PromptBuilder (Cover Letter): title/hook rules, prose constraints, personal narrative guidance
  - LengthController: character/byte measurement, 90–98% target expansion, final trimming
  - LLMClient: model options, timeouts, retries/backoff, unified errors
- Agents (thin orchestration): ResumeWriter, CoverLetterWriter, QualityManager
- Graph: uniform node pattern (validate → build context → call service → update state) and reusable revision helpers
- Infrastructure: OutputManager (file I/O only) + Serializers (model → JSON/text)

## 4. Workstreams & Scope
1) Data Models & Validation
- Introduce Pydantic models: Question, GuideEntry, CoverLetterResponse, SaveDecision
- Clarify AgentState fields (nullable, defaults) and add validators
- Normalization utilities for mixed-type inputs (e.g., string/list for experience/projects)

2) Prompt & Length Control
- Implement PromptBuilder(Cover Letter) encapsulating: title/hook, prose-only body, personal narrative (feelings, context, risks, actions, outcomes, reflection)
- Implement LengthController supporting character/UTF‑8 byte measurement, 90–98% target expansion (≤ 2 refinement loops), final safe trim
- Refactor CoverLetterWriter to use these services only

3) LLM Client Abstraction
- Create LLMClient interface with: model config, max tokens, temperature, timeout, retries/backoff, error mapping
- Agents depend only on LLMClient.invoke(messages)

4) Graph & Agents Simplification
- Thin agents (assembly role) and shared revision/evaluation helper (create_revision_node)
- Consistent node lifecycle: validate → build context → invoke service → merge results

5) Output & Serialization
- OutputManager handles I/O (analysis_results, summary, guides, cover_letter.txt, cover_letters/*)
- Serializer module converts models to serializable payloads and filenames (sanitize, max length)

6) Logging, Metrics, Error Handling
- Structured logs: stage/node/questionIndex/model/tokens/duration
- Metrics: quality score, length-target attainment, revision counts, save success rate
- Error categories: input, network, format, LLM, persistence; define retry/fallback policy

7) Testing & CI
- Unit tests: PromptBuilder, LengthController, Serializers, OutputManager
- Integration tests: example run → outputs snapshot; length rules verification per question
- Regression tests: per-question file save; string projects handling
- CI: GitHub Actions (py3.11/3.12), pre-commit (black/isort/flake8)

8) Developer Tooling
- Pre-commit hooks, type checks, lint and format in CI
- Local snapshot test helpers for stable prompt outputs

## 5. Milestones & Timeline (2–3 weeks)
- Week 0 (0.5 day): CI scaffold, pre-commit, minimal snapshots
- Week 1: Data models and normalization utils; AgentState validation; regression tests
- Week 2: PromptBuilder/LengthController; refactor CoverLetterWriter; length compliance tests
- Week 3: LLMClient abstraction; graph revision helper; Output serialization improvements; docs update

## 6. Acceptance Criteria (DoD)
- cover_letter.txt (combined) and cover_letters/*.txt (per-question) generated
- ≥ 90% of answers meet 90–98% of char/byte limits per question
- Quality score maintained at or above current baseline
- Test coverage: ≥ 80% lines on core modules (PromptBuilder, LengthController, OutputManager)
- Docs updated: Development Strategy, README, Usage Guide

## 7. Risks & Mitigations
- Tone drift from prompt tweaks → snapshot baselines, incremental adjustments
- Model/version variability → encapsulated options in LLMClient, config presets
- Filename/encoding issues → sanitize and max-length enforcement
- Regression surface → add targeted tests for previously failing cases

## 8. Deliverables
- New modules: services/prompt_builder.py, services/length_controller.py, services/llm_client.py, utils/serializers.py
- Refactored agents: production/cover_letter_writer.py uses services
- Graph helpers for revision/evaluation
- Comprehensive unit/integration tests and CI configuration
- Updated documentation (strategy, README, usage)

## 9. Appendix: Proposed File Layout
- resumeagents/
  - agents/
    - production/
      - cover_letter_writer.py (thin; uses services)
      - resume_writer.py
      - quality_manager.py
  - graph/
    - resume_graph.py (uniform node pattern; revision helper)
  - services/
    - prompt_builder.py
    - length_controller.py
    - llm_client.py
  - utils/
    - serializers.py
    - output_manager.py (I/O only)
  - models/ (optional)
- tests/
  - unit/ (prompt, length, serializers, output)
  - integration/ (end-to-end snapshots) 