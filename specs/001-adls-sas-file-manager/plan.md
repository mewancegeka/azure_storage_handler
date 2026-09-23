# Implementation Plan: ADLS SAS File Manager Library

**Branch**: `001-adls-sas-file-manager` | **Date**: 2026-09-23 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/001-adls-sas-file-manager/spec.md`

**Note**: This template is filled in by the `/speckit-plan` command; its definition describes the execution workflow.

## Summary

Build a single importable Python class that manages directories and files in an Azure Data Lake
Storage (ADLS) Gen2 account, authorizing all storage operations with a SAS token. The SAS token
(and any other secrets) is retrieved from Azure Key Vault at initialization using
caller-supplied Key Vault settings (vault URL, secret name), with an optional direct SAS token
override for callers who do not want Key Vault retrieval. The class supports creating (idempotent),
listing, renaming/moving, and deleting directories, and uploading (timestamped, overwrite-enabled),
downloading, appending to, and deleting files, plus saving JSON payloads as JSON files under a
given directory path. The technical approach follows the SAS-token authentication pattern from the
Microsoft Learn reference article and uses the official `azure-storage-file-datalake` and
`azure-keyvault-secrets`/`azure-identity` SDKs.

## Technical Context

**Language/Version**: Python 3.13 (latest version supported by both required Azure SDKs; see research.md)

**Primary Dependencies**: `azure-storage-file-datalake` (ADLS Gen2 operations), `azure-keyvault-secrets` and `azure-identity` (Key Vault secret retrieval)

**Storage**: Azure Data Lake Storage Gen2 (hierarchical-namespace-enabled storage account); no local database

**Testing**: `pytest`, with `unittest.mock` for unit tests against mocked Azure SDK clients, plus an optional/skippable integration test suite for real Key Vault + ADLS accounts

**Target Platform**: Cross-platform Python library (Windows/Linux/macOS runtime); developed using VS Code as the IDE

**Project Type**: Library (single project, importable Python package; no CLI, web, or mobile surface)

**Performance Goals**: No throughput/latency targets specified beyond the SDK's own defaults; operations should complete within the Azure Storage SDK's default retry/timeout behavior (see research.md)

**Constraints**: SAS token and Key Vault secret values MUST NOT appear in logs or error messages (constitution: Secure by Default); directory creation MUST be idempotent; uploads MUST use timestamped file names with overwrite enabled by default

**Scale/Scope**: Single storage account and single SAS token per library instance; one public class covering 8 spec'd operations (create directory, list directory, rename/move directory, delete directory, upload file, download file, append to file, delete file) plus JSON-payload-to-file saving

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Gate | Status |
|-----------|------|--------|
| I. Clear Contracts | Single class with documented, small methods per operation; no leaking of SDK-specific types beyond what's needed (paths, bytes, JSON-serializable payloads) | PASS |
| II. Correctness and Data Integrity | Directory creation is idempotent; upload overwrite behavior is explicit; nonexistent-path and expired-token edge cases are enumerated in spec and must be covered by tests in Phase 1 contracts | PASS (contracts to enumerate error behavior in Phase 1) |
| III. Testable Changes | Unit tests with mocked SDK clients for every operation; integration tests required because the feature depends on real Key Vault + ADLS Gen2 authentication flows | PASS (planned in research.md testing strategy) |
| IV. Secure by Default | SAS token sourced from Key Vault by default; direct-token override is opt-in, not default; no secret values logged; Key Vault settings passed as parameters, not hardcoded | PASS |
| V. Observable and Operationally Simple | Single-project library layout, minimal dependencies (2 Azure SDK families), clear typed exceptions instead of ambiguous SDK errors leaking through unchanged | PASS |

No violations requiring the Complexity Tracking table.

## Project Structure

### Documentation (this feature)

```text
specs/001-adls-sas-file-manager/
├── plan.md              # This file (/speckit-plan command output)
├── research.md          # Phase 0 output (/speckit-plan command)
├── data-model.md        # Phase 1 output (/speckit-plan command)
├── quickstart.md        # Phase 1 output (/speckit-plan command)
├── contracts/           # Phase 1 output (/speckit-plan command)
└── tasks.md             # Phase 2 output (/speckit-tasks command - NOT created by /speckit-plan)
```

### Source Code (repository root)

```text
src/
└── adls_sas_file_manager/
    ├── __init__.py
    ├── client.py            # Public class: AdlsSasFileManager
    ├── config.py            # Storage/Key Vault connection configuration
    ├── errors.py            # Typed exceptions (configuration, auth, operation errors)
    └── _internal/
        └── secret_resolver.py  # Key Vault SAS token retrieval / direct-token override logic

tests/
├── unit/
│   ├── test_client_directories.py
│   ├── test_client_files.py
│   ├── test_client_json_payloads.py
│   └── test_secret_resolver.py
└── integration/
    └── test_adls_live.py    # Skipped unless real Key Vault/ADLS credentials are configured
```

**Structure Decision**: Single-project library layout under `src/adls_sas_file_manager/` with a
matching `tests/` tree (`unit/` mocked-SDK tests required for every change; `integration/` for the
real Key Vault + ADLS Gen2 flow, skipped by default). This is Option 1 (single project) from the
template; Option 2 (web app) and Option 3 (mobile+API) are not applicable since this feature is a
library with no frontend, backend service, or mobile component.

