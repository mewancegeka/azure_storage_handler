# Tasks: ADLS SAS File Manager Library

**Input**: Design documents from `/specs/001-adls-sas-file-manager/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/adls_sas_file_manager.md, quickstart.md

**Tests**: Included. The constitution's Testable Changes principle (III) requires focused
automated tests for every behavior change and integration tests when a change depends on a real
storage/authentication flow; plan.md and research.md already commit to a pytest-based unit +
integration test strategy.

**Organization**: Tasks are grouped by user story (from spec.md) to enable independent
implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

Single-project library layout per plan.md:

- `src/adls_sas_file_manager/` — library source
- `tests/unit/` — mocked-SDK unit tests
- `tests/integration/` — live Key Vault + ADLS tests (skipped unless configured)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [ ] T001 Create project structure per plan.md: `src/adls_sas_file_manager/` (with `_internal/` subpackage), `tests/unit/`, `tests/integration/`
- [ ] T002 Initialize the Python 3.13 project with `pyproject.toml` declaring runtime dependencies `azure-storage-file-datalake`, `azure-keyvault-secrets`, `azure-identity` and dev dependency `pytest`, per research.md
- [ ] T003 [P] Configure VS Code workspace settings in `.vscode/settings.json` to select the Python 3.13 interpreter and enable pytest test discovery, per quickstart.md

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T004 Create the exception hierarchy (`AdlsSasFileManagerError`, `ConfigurationError`, `SecretRetrievalError`, `AuthorizationError`, `PathNotFoundError`, `StorageOperationError`) in `src/adls_sas_file_manager/errors.py`, per contracts/adls_sas_file_manager.md
- [ ] T005 [P] Create `StorageConnectionConfig` in `src/adls_sas_file_manager/config.py` implementing the data-model.md validation rules: `account_name` MUST be non-empty; either `sas_token` OR both `key_vault_url` and `key_vault_secret_name` MUST be provided, else raise `ConfigurationError`
- [ ] T006 [P] Implement SAS token resolution in `src/adls_sas_file_manager/_internal/secret_resolver.py`: use `azure.identity.DefaultAzureCredential` + `azure.keyvault.secrets.SecretClient.get_secret` to retrieve the SAS token when `sas_token` is not supplied directly, wrapping any Key Vault failure as `SecretRetrievalError` without including the secret name/value or vault URL contents in the error message (FR-013)
- [ ] T007 Create `AdlsSasFileManager.__init__` in `src/adls_sas_file_manager/client.py`: validate config via T005, resolve the SAS token via T006, and construct the `azure.storage.filedatalake.DataLakeServiceClient` using `https://{account_name}.dfs.core.windows.net` and the resolved SAS token as credential
- [ ] T008 Create `src/adls_sas_file_manager/__init__.py` exporting `AdlsSasFileManager` and all exception types from T004
- [ ] T009 [P] Create shared pytest fixtures in `tests/unit/conftest.py` that provide a mocked `DataLakeServiceClient` (and its `FileSystemClient`/`DataLakeDirectoryClient`/`DataLakeFileClient`) so unit tests never contact real Azure services

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - Manage directories and files in ADLS via a reusable library (Priority: P1) 🎯 MVP

**Goal**: Provide create/list/rename/delete for directories, upload/download/append/delete for
files, and saving JSON payloads as timestamped `.json` files, all through one class.

**Independent Test**: Instantiate `AdlsSasFileManager` against a test ADLS account (or the mocked
fixtures from T009), perform each directory and file operation, and verify the resulting state.

### Tests for User Story 1 ⚠️

- [ ] T010 [P] [US1] Unit test: `create_directory` succeeds on first call and is idempotent (no error) when the directory already exists, in `tests/unit/test_client_directories.py`
- [ ] T011 [P] [US1] Unit test: `list_directory` returns contained file/subdirectory names, and raises `PathNotFoundError` for a nonexistent directory, in `tests/unit/test_client_directories.py`
- [ ] T012 [P] [US1] Unit test: `rename_directory` moves a directory to the new path (old path no longer resolves), in `tests/unit/test_client_directories.py`
- [ ] T013 [P] [US1] Unit test: `delete_directory` removes the directory and its contents, in `tests/unit/test_client_directories.py`
- [ ] T014 [P] [US1] Unit test: `upload_file` stores the file with a timestamp in its name and overwrite enabled by default, in `tests/unit/test_client_files.py`
- [ ] T015 [P] [US1] Unit test: `download_file` produces a local copy that matches the remote file's content byte-for-byte, in `tests/unit/test_client_files.py`
- [ ] T016 [P] [US1] Unit test: `append_to_file` results in original content followed by appended bytes, in `tests/unit/test_client_files.py`
- [ ] T017 [P] [US1] Unit test: `delete_file` removes the file, in `tests/unit/test_client_files.py`
- [ ] T018 [P] [US1] Unit test: `save_json` serializes a JSON-serializable payload, writes it as a timestamped `.json` file under the given directory path (creating the directory if missing), and raises `ConfigurationError` for a non-serializable payload before any network call, in `tests/unit/test_client_json_payloads.py`

### Implementation for User Story 1

- [ ] T019 [US1] Implement `create_directory(file_system_name, directory_path)` in `src/adls_sas_file_manager/client.py`: treat an already-existing directory as success (FR-005)
- [ ] T020 [US1] Implement `list_directory(file_system_name, directory_path)` in `src/adls_sas_file_manager/client.py` using `FileSystemClient.get_paths`, raising `PathNotFoundError` when the path does not exist (depends on T019)
- [ ] T021 [US1] Implement `rename_directory(file_system_name, directory_path, new_directory_path)` in `src/adls_sas_file_manager/client.py` using `DataLakeDirectoryClient.rename_directory` with the `{file_system}/{new_path}` format (depends on T019)
- [ ] T022 [US1] Implement `delete_directory(file_system_name, directory_path)` in `src/adls_sas_file_manager/client.py` (depends on T019)
- [ ] T023 [US1] Implement `upload_file(file_system_name, directory_path, local_file_path, file_name=None)` in `src/adls_sas_file_manager/client.py`: generate a timestamped stored file name and call `upload_data(..., overwrite=True)` (FR-009a), returning the stored file name
- [ ] T024 [US1] Implement `download_file(file_system_name, directory_path, file_name, local_destination_path)` in `src/adls_sas_file_manager/client.py` (depends on T023)
- [ ] T025 [US1] Implement `append_to_file(file_system_name, directory_path, file_name, data)` in `src/adls_sas_file_manager/client.py` using `append_data` at the current file size offset followed by `flush_data` (depends on T023)
- [ ] T026 [US1] Implement `delete_file(file_system_name, directory_path, file_name)` in `src/adls_sas_file_manager/client.py` (depends on T023)
- [ ] T027 [US1] Implement `save_json(file_system_name, directory_path, payload, file_name=None)` in `src/adls_sas_file_manager/client.py`: validate `payload` is JSON-serializable (else raise `ConfigurationError`), ensure the directory exists via `create_directory` (T019), and upload the serialized UTF-8 JSON text via `upload_file` (T023) with a `.json` extension
- [ ] T028 [US1] Add error translation in `src/adls_sas_file_manager/client.py` mapping Azure SDK exceptions (`ResourceNotFoundError` → `PathNotFoundError`, `ClientAuthenticationError`/403 responses → `AuthorizationError`, other `HttpResponseError`/`ServiceRequestError` → `StorageOperationError`) across all methods implemented in T019-T027, ensuring no exception message includes the SAS token value (FR-013)

**Checkpoint**: User Story 1 is fully functional and independently testable

---

## Phase 4: User Story 2 - Authorize storage access using a SAS token retrieved from Azure Key Vault (Priority: P1)

**Goal**: Configure the library with Key Vault settings so the SAS token is retrieved securely,
with an optional direct-token override.

**Independent Test**: Store a SAS token as a secret in a test Key Vault, configure the library
with the vault URL and secret name, and verify it authorizes ADLS requests without the caller ever
supplying the raw SAS token value; separately verify the direct-token override path.

### Tests for User Story 2 ⚠️

- [ ] T029 [P] [US2] Unit test: initializing `AdlsSasFileManager` with valid `key_vault_url`/`key_vault_secret_name` retrieves the SAS token from the mocked `SecretClient` and uses it for the `DataLakeServiceClient` credential, in `tests/unit/test_secret_resolver.py`
- [ ] T030 [P] [US2] Unit test: a nonexistent secret/vault raises `SecretRetrievalError` whose message contains no secret value, vault URL secret content, or SAS token, in `tests/unit/test_secret_resolver.py`
- [ ] T031 [P] [US2] Unit test: supplying `sas_token` directly bypasses Key Vault retrieval entirely (the mocked `SecretClient` is never called), in `tests/unit/test_secret_resolver.py`

### Implementation for User Story 2

- [ ] T032 [US2] Harden `src/adls_sas_file_manager/_internal/secret_resolver.py` (built in T006) so every Key Vault SDK exception is caught and re-raised as `SecretRetrievalError` with a generic, non-sensitive message
- [ ] T033 [US2] Confirm and, if needed, adjust `AdlsSasFileManager.__init__` in `src/adls_sas_file_manager/client.py` so a supplied `sas_token` always takes precedence over Key Vault settings (FR-005a), with a unit-testable branch point (depends on T007, T032)

**Checkpoint**: User Stories 1 AND 2 both work independently

---

## Phase 5: User Story 3 - Discover configuration and connection errors early (Priority: P2)

**Goal**: Surface clear, actionable errors for invalid configuration or authorization failures
instead of ambiguous low-level SDK exceptions.

**Independent Test**: Supply invalid configuration values (missing account name, invalid vault
URL, expired/invalid SAS token, insufficient SAS permissions) and verify each produces a
distinguishable, descriptive error rather than an unhandled exception or silent failure.

### Tests for User Story 3 ⚠️

- [ ] T034 [P] [US3] Unit test: `AdlsSasFileManager(account_name="")` raises `ConfigurationError` before any network/Key Vault call, in `tests/unit/test_client_config_validation.py`
- [ ] T035 [P] [US3] Unit test: an expired/invalid or under-permissioned SAS token causes any storage operation to raise `AuthorizationError` naming the attempted operation, with no SAS token value present in the exception message, in `tests/unit/test_client_files.py`

### Implementation for User Story 3

- [ ] T036 [US3] Add upfront validation in `AdlsSasFileManager.__init__` (`src/adls_sas_file_manager/client.py`) that raises `ConfigurationError` for an empty/missing `account_name` before constructing any SDK client or contacting Key Vault (depends on T007)
- [ ] T037 [US3] Extend the error-translation logic from T028 in `src/adls_sas_file_manager/client.py` so `AuthorizationError` messages identify which operation failed (e.g., "upload_file", "delete_directory") while still excluding the SAS token value

**Checkpoint**: All user stories are independently functional

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T038 [P] Add `README.md` documenting installation and a usage example that mirrors quickstart.md
- [ ] T039 Manually review `src/adls_sas_file_manager/` to confirm no log statement or exception message includes a SAS token, secret name, or secret value (constitution: Secure by Default; FR-013)
- [ ] T040 Run `pytest tests/unit` and confirm all tests from Phases 3-5 pass
- [ ] T041 [P] Create the skippable integration test skeleton in `tests/integration/test_adls_live.py`, gated by the environment variables documented in quickstart.md, marked so it is skipped by default when those variables are absent

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion — BLOCKS all user stories
- **User Story 1 (Phase 3)**: Depends on Foundational (Phase 2) completion; no dependency on US2/US3
- **User Story 2 (Phase 4)**: Depends on Foundational (Phase 2) completion; independently testable, though it hardens code (`secret_resolver.py`) also exercised by US1's `__init__` path
- **User Story 3 (Phase 5)**: Depends on Foundational (Phase 2) completion; extends error-translation code introduced in US1 (T028) and construction code from Foundational (T007)
- **Polish (Phase 6)**: Depends on all desired user stories being complete

### Within Each User Story

- Tests are written before their corresponding implementation tasks and should fail first
- Directory operations before file operations (file paths in US1 build on directory existence)
- Core implementation (T019-T027) before cross-cutting error translation (T028)

### Parallel Opportunities

- T003 (Setup) can run in parallel with T002
- T005, T006, T009 (Foundational) can run in parallel with each other (different files); T004 blocks T005/T006/T007 only insofar as they raise the exception types it defines
- All US1 test tasks (T010-T018) can run in parallel (different test files/functions)
- All US2 test tasks (T029-T031) can run in parallel
- All US3 test tasks (T034-T035) can run in parallel
- T038 and T041 (Polish) can run in parallel with each other

---

## Parallel Example: User Story 1

```bash
# Launch all US1 test tasks together (different files/functions, no shared state):
Task: "Unit test create_directory idempotency in tests/unit/test_client_directories.py"
Task: "Unit test list_directory contents and PathNotFoundError in tests/unit/test_client_directories.py"
Task: "Unit test rename_directory in tests/unit/test_client_directories.py"
Task: "Unit test delete_directory in tests/unit/test_client_directories.py"
Task: "Unit test upload_file timestamped overwrite in tests/unit/test_client_files.py"
Task: "Unit test download_file byte-for-byte round trip in tests/unit/test_client_files.py"
Task: "Unit test append_to_file in tests/unit/test_client_files.py"
Task: "Unit test delete_file in tests/unit/test_client_files.py"
Task: "Unit test save_json serialization and directory creation in tests/unit/test_client_json_payloads.py"
```

## Implementation Strategy

### MVP First (User Story 1 + 2 together)

User Story 1 and User Story 2 are both P1 and mutually foundational (per plan.md/spec.md): a
usable MVP requires directory/file management (US1) AND secure SAS retrieval (US2), since US1's
`__init__` construction path is exercised by the same code US2 hardens. Recommended order:

1. Complete Phase 1 (Setup) and Phase 2 (Foundational)
2. Complete Phase 3 (User Story 1) — validate independently against mocked fixtures
3. Complete Phase 4 (User Story 2) — validate independently against mocked fixtures
4. **STOP and VALIDATE**: Run `pytest tests/unit`, confirm all US1 + US2 tests pass — this is the MVP
5. Add Phase 5 (User Story 3) for improved error clarity
6. Finish with Phase 6 (Polish)

### Incremental Delivery

Each user story phase ends with a checkpoint where the delivered subset is independently testable,
allowing the MVP (US1 + US2) to be validated and used before US3's error-clarity refinements are
added.
