<!--
Sync Impact Report:
Version: 0.0.0 → 1.0.0
Modified Principles: Initial creation - all principles new
  - I. Package-Based Architecture (NEW)
  - II. Experiment Reproducibility (NEW)
  - III. Test-First Development (NEW)
  - IV. CLI-Driven Automation (NEW)
  - V. Shared Code Discipline (NEW)
Added Sections: Technical Standards, Development Workflow, Governance
Removed Sections: None
Templates Status:
  ✅ plan-template.md - Constitution check section aligns
  ✅ spec-template.md - User stories and requirements sections align
  ✅ tasks-template.md - Task categorization aligns
Follow-up TODOs: None
-->

# Financial Analyst Constitution

## Core Principles

### I. Package-Based Architecture

Every experiment or feature MUST be developed as an independent package under `packages/`.
Each package MUST:

- Be self-contained with its own `pyproject.toml` defining dependencies
- Have a clear purpose and domain boundary
- Include tests under `tests/` directory
- Be installable as an editable workspace member via uv
- Include an AzureML job configuration (`aml-job.yaml`) for cloud execution

Code belongs in one of two locations:

- **Experiment packages** (`packages/experiment/`, or newly created packages):
  Domain-specific logic for specific analysis or modeling tasks
- **Shared package** (`packages/shared/`): Code reused across TWO OR MORE
  packages

**Rationale**: Package isolation ensures experiments are independently
deployable, testable, and maintainable. Clear boundaries prevent tangled
dependencies.

### II. Experiment Reproducibility

All experiments MUST be traceable and reproducible. Every AzureML run MUST:

- Be associated with a git commit containing all code and configuration
- Log metrics using `azureml_logger` for tracking (numerical values via `log_metrics()`)
- Set tags for input parameters via `set_tags()` for reproducibility
- Write outputs to the designated outputs directory (`../outputs` relative to src)
- Use versioned data assets registered in AzureML

Experiment tracking via git MUST follow the experiments branch workflow:

- Experimental changes committed to dedicated experiments branch
- Commit message describes the experiment purpose
- AzureML job references the exact git commit for full traceability

**Rationale**: ML experiments are research activities requiring perfect reproducibility.
Git history + AzureML metadata = complete audit trail from code to results.

### III. Test-First Development (NON-NEGOTIABLE)

Test-Driven Development is MANDATORY. The workflow MUST be:

1. Write test cases covering acceptance scenarios
2. Get user approval on test cases
3. Run tests → verify they fail (RED)
4. Implement minimum code to pass (GREEN)
5. Refactor while keeping tests green (REFACTOR)

Every package MUST include:

- Unit tests for core logic functions (`tests/test_*.py`)
- Tests MUST be runnable via pytest from workspace root
- Coverage tracking enabled (omitting test files)
- Tests integrated into VSCode for local development

**Rationale**: Tests are the specification. User-approved tests prevent
misaligned implementation. TDD catches bugs early and enables confident
refactoring.

### IV. CLI-Driven Automation

All development operations MUST be scriptable via CLI tools in `bin/`. Scripts MUST:

- Follow bash best practices: `set -eo pipefail`, absolute paths
- Provide `--help` documentation explaining purpose and usage
- Output to stdout for success, stderr for diagnostics/errors
- Be composable (pipeable, scriptable)
- Maintain idempotency where possible

Core workflows automated:

- Package lifecycle: `bin/pkg/new`, `bin/pkg/rm`
- Pipeline operations: `bin/pipe/new`, `bin/pipe/local`, `bin/pipe/aml`
- Data management: `bin/data/register`, `bin/data/download`, `bin/data/list`
- Testing and linting: `bin/dev/test`, `bin/lint/{py,md,shell}`

**Rationale**: Automation reduces errors, enables CI/CD, and makes workflows
transparent and reproducible. CLI-first ensures all operations work in both
local and automated contexts.

### V. Shared Code Discipline

The `packages/shared/` package is for cross-cutting utilities only. Code
belongs in shared ONLY if:

- It is used by TWO OR MORE other packages
- It is domain-agnostic (logging, utilities, common data structures)
- It has NO package-specific dependencies

The shared package MUST:

- Define NO dependencies in its own `pyproject.toml`
- Be dependency-injected by consuming packages (each consumer declares needed
  dependencies)
- Remain lightweight and focused on reusability

**Rationale**: Shared code without discipline becomes a dumping ground. This
rule keeps shared truly shared and prevents dependency bloat.

## Technical Standards

### Language and Environment

- **Python Version**: 3.12 (strict, enforced via
  `requires-python = "==3.12.*"`)
- **Package Manager**: uv with workspace member architecture
- **Type Checking**: Pyright in basic mode (enforced via `pyproject.toml`)
- **Code Quality**: Ruff linter with bugbear, pycodestyle, pyflakes, import
  order, pyupgrade rules
- **Testing**: pytest with strict markers and importlib mode

### AzureML Integration

- All compute-intensive experiments MUST run on AzureML
- Local development MUST work seamlessly (via `bin/pkg/local` or VSCode)
- Environment defined via Dockerfile in `packages/*/environment/Dockerfile`
- Data assets registered and versioned in AzureML, referenced in job configs

### Project Structure

```text
packages/
  experiment/        # Default experiment package (can create more via bin/pkg/new)
    src/experiment/  # Python package with __init__.py, __main__.py
    tests/           # pytest tests
    environment/     # Dockerfile for AzureML
    aml-job.yaml     # AzureML job configuration
    pyproject.toml   # Package dependencies
  shared/            # Cross-package utilities
    src/shared/      # Logging, common utilities
    tests/
    pyproject.toml   # NO dependencies defined here
bin/                 # CLI automation scripts
  pkg/, pipe/, data/, dev/, lint/
pipelines/           # AzureML pipeline definitions
runs/                # Tracked experiment snapshots
data/                # Local data cache (not committed)
```

## Development Workflow

### Adding New Experiments

1. Create package: `bin/pkg/new <experiment-name>`
2. Implement in `packages/<experiment-name>/src/<experiment-name>/`
3. Write tests in `packages/<experiment-name>/tests/`
4. Test locally via VSCode or `bin/dev/test`
5. Submit to AzureML: `bin/pkg/aml <experiment-name> --exp "description"`

### Modifying Shared Code

1. Identify if code is TRULY needed by 2+ packages
2. Add to `packages/shared/src/shared/`
3. Update consuming packages' `pyproject.toml` with any new dependencies
4. Test all dependent packages

### Code Quality Gates

- All code MUST pass `bin/lint/py` (ruff + pyright)
- All tests MUST pass via `bin/dev/test`
- Coverage tracking enabled (excluding test files)
- Markdown documentation MUST pass `bin/lint/md`
- Shell scripts MUST pass `bin/lint/shell`

### Experiment Lifecycle

1. **Development**: Local iteration with VSCode and pytest
2. **Submission**: Automated experiment commit via `bin/pkg/aml --exp`
3. **Tracking**: Git commit + AzureML job linked for reproducibility
4. **Results**: Metrics logged to AzureML, outputs written to outputs directory

## Governance

This constitution supersedes all other development practices and patterns.
Changes require:

- Documentation of rationale in amendment commit
- Version bump following semantic versioning (see below)
- Migration plan for affected code if breaking changes introduced

### Constitution Versioning

- **MAJOR**: Breaking principle changes (e.g., removing TDD requirement)
- **MINOR**: New principles or expanded guidance (e.g., adding security section)
- **PATCH**: Clarifications, typo fixes, non-semantic improvements

### Compliance

- All feature specifications (`specs/*/spec.md`) MUST align with these
  principles
- All implementation plans (`specs/*/plan.md`) MUST include Constitution Check
  section
- Code reviews MUST verify adherence to package architecture and test-first
  workflow
- Complexity that violates principles MUST be justified in plan's Complexity
  Tracking section

### Living Document

The constitution is authoritative but not immutable. Propose amendments when:

- Principles conflict with project realities
- New technologies require architectural changes
- Team learns better practices through experience

All amendments require documentation of WHY and WHAT changed, committed
alongside the updated constitution.

**Version**: 1.0.0 | **Ratified**: 2025-11-25 | **Last Amended**: 2025-11-25
