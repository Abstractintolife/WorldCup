# Requirements Document

## Introduction

This feature establishes an automated **testing and static-analysis CI environment** for the World Cup Console (世界杯赛事终端), a Python 3.12/3.13 + PyQt6 desktop application. The environment runs entirely inside GitHub Actions and, on every push and pull request to `main`, lints, type-checks, and runs a deterministic test suite against a Python version matrix so regressions in the pure-logic layers are caught before merge.

The work is purely additive testing infrastructure: a `tests/` package (pytest unit tests, Hypothesis property tests, mocked-transport API client tests, and headless UI import-smoke tests), a `requirements-dev.txt` dev/test toolchain manifest, central tool configuration in `pyproject.toml` (pytest, coverage, ruff, mypy), shared fixtures in `tests/conftest.py` for filesystem/network/timezone/Qt isolation, and one or more GitHub Actions workflow files under `.github/workflows/`. No application source under `app/` or `main.py` is modified, and no test performs real network access.

## Glossary

- **CI_Pipeline**: The GitHub Actions workflow (`.github/workflows/ci.yml`) that orchestrates checkout, environment setup, lint, type-check, and test execution on each push/PR to `main`.
- **Build_Matrix**: The CI job strategy that runs the pipeline independently against each supported Python version (3.12 and 3.13) on `ubuntu-latest`.
- **Lint_Gate**: The `ruff check` step that validates code style and correctness rules over `app` and `tests`.
- **Type_Check_Gate**: The `mypy` step that statically type-checks the logic core under `app`.
- **Test_Runner**: The `pytest` step (with coverage) that discovers and executes the `tests/` suite under a headless Qt platform.
- **Test_Suite**: The collection of tests in the `tests/` package (unit, property-based, API client, and UI smoke tests).
- **Dev_Manifest**: The `requirements-dev.txt` file pinning the dev/test/lint/type-check toolchain.
- **Tool_Config**: The configuration declared in `pyproject.toml` for pytest, coverage, ruff, and mypy.
- **Test_Fixtures**: The shared pytest fixtures in `tests/conftest.py` that isolate tests from the real filesystem, network, timezone, and display.
- **API_Client_Test**: Tests that drive `app/api/client.py` through a mocked HTTP transport.
- **UI_Smoke_Test**: Tests that import every `app.ui.*` module and instantiate selected leaf widgets under `QT_QPA_PLATFORM=offscreen`.
- **Property_Test**: A Hypothesis-based test that asserts a universally-quantified invariant over generated inputs.
- **Logic_Core**: The deterministic, network-free application layers under `app/models`, `app/services`, `app/utils`, and `app/config`.
- **Offscreen_Platform**: The headless Qt rendering platform selected via the `QT_QPA_PLATFORM=offscreen` environment variable.
- **Mock_Transport**: An `httpx.MockTransport` (or `respx` mock) that returns canned dongqiudi-shaped JSON without opening a real socket.
- **JSON_CACHE_TTL**: The freshness window of the API client's disk cache during which a repeated fetch is served from cache.

## Requirements

### Requirement 1: CI pipeline triggering

**User Story:** As a maintainer, I want the CI pipeline to run automatically on pushes and pull requests targeting `main`, so that regressions are detected before code is merged.

#### Acceptance Criteria

1. WHEN a commit is pushed to the `main` branch, THE CI_Pipeline SHALL start a pipeline run.
2. WHEN a pull request targeting the `main` branch is opened or updated, THE CI_Pipeline SHALL start a pipeline run.
3. THE CI_Pipeline SHALL execute the Lint_Gate, then the Type_Check_Gate, then the Test_Runner in that order within each Build_Matrix job.
4. IF the Lint_Gate, the Type_Check_Gate, or the Test_Runner exits with a non-zero status, THEN THE CI_Pipeline SHALL report the affected Build_Matrix job as failed.
5. IF a Build_Matrix job encounters a runner error, a timeout, or a dependency installation failure, THEN THE CI_Pipeline SHALL report the affected Build_Matrix job as failed.
6. THE CI_Pipeline SHALL report an overall success status only WHEN every gate passes on every Build_Matrix job.

### Requirement 2: Python version matrix

**User Story:** As a maintainer, I want the suite to run against every supported Python version, so that compatibility across 3.12 and 3.13 is verified.

#### Acceptance Criteria

1. THE Build_Matrix SHALL execute the pipeline against Python version 3.12 and Python version 3.13.
2. THE Build_Matrix SHALL run on the `ubuntu-latest` runner.
3. THE Build_Matrix SHALL run each Python version as an independent job whose outcome does not depend on any other version's outcome.
4. WHEN one Build_Matrix job fails, THE CI_Pipeline SHALL continue running and report the remaining Build_Matrix jobs.
5. THE Build_Matrix SHALL exclude Python version 3.14 from the version set.

### Requirement 3: Headless Qt environment

**User Story:** As a maintainer, I want PyQt6 modules to import and instantiate without a physical display, so that UI smoke tests run on a headless CI runner.

#### Acceptance Criteria

1. THE CI_Pipeline SHALL install the Qt system libraries `libegl1`, `libgl1`, `libxkbcommon0`, and `libdbus-1-3` on the runner before executing the Test_Runner.
2. WHEN the Test_Runner executes, THE CI_Pipeline SHALL set the environment variable `QT_QPA_PLATFORM` to `offscreen`.
3. THE Test_Fixtures SHALL set `QT_QPA_PLATFORM` to `offscreen` before any PyQt6 module is imported.
4. THE CI_Pipeline SHALL install `xvfb` on the runner as a fallback headless display option.

### Requirement 4: Static analysis gates

**User Story:** As a maintainer, I want linting and type-checking enforced in CI, so that style and type regressions block merges.

#### Acceptance Criteria

1. THE Lint_Gate SHALL run `ruff check` over the `app` and `tests` directories.
2. IF the Lint_Gate detects a lint violation, THEN THE CI_Pipeline SHALL fail the affected Build_Matrix job.
3. THE Type_Check_Gate SHALL run `mypy` over the `app` directory.
4. IF the Type_Check_Gate detects a type error in the Logic_Core, THEN THE CI_Pipeline SHALL fail the affected Build_Matrix job.
5. WHERE a module matches `app.ui.*`, THE Type_Check_Gate SHALL ignore type errors in that module.
6. THE Tool_Config SHALL select the ruff rule sets `E`, `F`, `I`, `B`, and `UP`.

### Requirement 5: Dev dependency manifest

**User Story:** As a developer, I want a single dev dependency manifest, so that CI and contributors can install the full test toolchain with one command.

#### Acceptance Criteria

1. THE Dev_Manifest SHALL include the runtime dependencies declared in `requirements.txt`.
2. THE Dev_Manifest SHALL pin `pytest`, `pytest-cov`, `pytest-asyncio`, `hypothesis`, `ruff`, `mypy`, and `respx`.
3. WHEN the CI_Pipeline installs dependencies, THE CI_Pipeline SHALL install from the Dev_Manifest.
4. THE Dev_Manifest SHALL leave the runtime `requirements.txt` file unchanged.

### Requirement 6: Tooling configuration

**User Story:** As a developer, I want centralized tool configuration, so that test discovery, coverage scope, and analysis rules are consistent and declarative.

#### Acceptance Criteria

1. THE Tool_Config SHALL set the pytest test discovery path to the `tests` directory.
2. THE Tool_Config SHALL register the `ui` and `property` pytest markers.
3. THE Tool_Config SHALL measure coverage over the `app` source and exclude `app/ui/*` from coverage measurement.
4. THE Tool_Config SHALL configure ruff with a line length of 100 and exempt `app/ui/**` and `tests/**` from the line-length rule.
5. THE Tool_Config SHALL configure mypy to check the Logic_Core, to ignore missing third-party stubs, and to ignore errors in `app.ui.*`.

### Requirement 7: Test isolation fixtures

**User Story:** As a developer, I want every test isolated from the real filesystem, network, timezone, and display, so that results are deterministic and side-effect free.

#### Acceptance Criteria

1. WHEN a test executes, THE Test_Fixtures SHALL redirect the cache and data directories into a per-test temporary directory by setting `XDG_CACHE_HOME` and `XDG_DATA_HOME`.
2. IF the directory redirection setup fails, THEN THE Test_Fixtures SHALL allow the test to continue running.
3. THE Test_Fixtures SHALL prevent any test from writing to the real operating-system cache or data directories.
4. WHERE a test requires deterministic timezone behavior, THE Test_Fixtures SHALL pin the `WC_LOCAL_TZ` environment variable to `Asia/Shanghai`.
5. THE Test_Fixtures SHALL provide a single reusable `QApplication` instance for UI tests.
6. THE Test_Fixtures SHALL provide a Mock_Transport that returns canned dongqiudi-shaped JSON.

### Requirement 8: Logic core unit tests

**User Story:** As a developer, I want the deterministic logic core unit-tested, so that model parsing, prediction math, and time utilities are verified.

#### Acceptance Criteria

1. THE Test_Suite SHALL include unit tests for `app/models` parsing, validators, and derived properties.
2. THE Test_Suite SHALL include unit tests for `app/services/prediction.py` probability and odds computations.
3. THE Test_Suite SHALL include unit tests for `app/utils/time_utils.py` timezone conversions and formatting.
4. THE Test_Suite SHALL include unit tests for `app/services/favorites.py` JSON persistence using an isolated temporary directory.
5. WHILE coverage measurement over the Logic_Core is enabled, THE Test_Suite SHALL achieve at least 80% coverage.

### Requirement 9: Property-based tests

**User Story:** As a developer, I want property-based tests over numeric and parsing invariants, so that edge cases across the input space are exercised.

#### Acceptance Criteria

1. THE Test_Suite SHALL include Property_Test cases implemented with Hypothesis.
2. WHEN a tz-aware UTC datetime is converted to local time and back to UTC, THE time utilities SHALL produce the original instant.
3. WHEN win probabilities are computed for any team indices in the range 0 to 100, THE prediction service SHALL produce values that each lie within 0 to 1 and that sum to 1.0 within a tolerance of 1e-10.
4. WHEN a raw match payload with missing or malformed fields is parsed, THE `Match.from_raw` parser SHALL complete without raising an unexpected exception and SHALL produce a `winner_id` that is one of the two team identifiers or null.
5. WHERE a raw match payload is severely malformed, THE `Match.from_raw` parser SHALL signal the failure through a returned null or sentinel result rather than raising an unexpected exception.
6. EACH Property_Test SHALL execute at least 100 generated iterations.

### Requirement 10: API client behavioral tests

**User Story:** As a developer, I want the API client tested against a mocked transport, so that caching behavior is verified without real network calls.

#### Acceptance Criteria

1. THE API_Client_Test SHALL drive `app/api/client.py` through a Mock_Transport so that no real socket is opened.
2. WHEN a payload is fetched and then fetched again within the JSON_CACHE_TTL, THE API client SHALL invoke the Mock_Transport exactly once and serve the second call from cache.
3. WHEN a cache entry is expired and a fetch occurs, THE API client SHALL return the stale data immediately and schedule a background revalidation.
4. IF a network fetch fails and no cache entry exists, THEN THE API client SHALL raise a `RuntimeError`.
5. IF a network fetch fails and a stale cache entry exists, THEN THE API client SHALL return the stale data.

### Requirement 11: UI import smoke tests

**User Story:** As a developer, I want every UI module imported under a headless platform, so that import-time and constructor errors are caught.

#### Acceptance Criteria

1. WHILE the Offscreen_Platform is active, THE UI_Smoke_Test SHALL import every module under `app.ui.*`.
2. IF importing any `app.ui.*` module raises an error, THEN THE UI_Smoke_Test SHALL fail and report the failing module name.
3. WHILE the Offscreen_Platform is active, THE UI_Smoke_Test SHALL pass as long as no explicit import error occurs, even when some optional modules are skipped.
4. THE UI_Smoke_Test SHALL be registered unconditionally under the `ui` pytest marker, independent of whether the Offscreen_Platform is active.
5. THE Tool_Config SHALL exclude UI_Smoke_Test modules from coverage gating.

### Requirement 12: Network isolation guarantee

**User Story:** As a maintainer, I want the suite to never reach the live data provider, so that CI runs are deterministic and avoid rate limits.

#### Acceptance Criteria

1. FOR ALL tests in the Test_Suite, THE Test_Fixtures SHALL ensure the number of real outbound HTTP requests is zero.
2. IF a test attempts a real outbound network connection, THEN THE Test_Fixtures SHALL fail that test and report the un-mocked target.

### Requirement 13: Coverage artifact publication

**User Story:** As a maintainer, I want coverage results published from each matrix job, so that I can review coverage per Python version.

#### Acceptance Criteria

1. WHEN the Test_Runner completes, THE CI_Pipeline SHALL upload the coverage data file as a build artifact named with the Python version.
2. IF the coverage artifact naming fails, THEN THE CI_Pipeline SHALL still upload the available coverage data.
3. WHILE a Build_Matrix job has failed, THE CI_Pipeline SHALL still upload the available coverage artifact for that job.

### Requirement 14: Non-invasive infrastructure

**User Story:** As a maintainer, I want the testing infrastructure to be purely additive, so that existing application behavior is not altered.

#### Acceptance Criteria

1. THE Test_Suite SHALL leave all source under `app/` and `main.py` unchanged.
2. THE CI_Pipeline SHALL pin each GitHub Action it uses to a major version tag.
3. THE CI_Pipeline SHALL operate without storing credentials except those strictly required for an explicit deployment or package-publication step.
