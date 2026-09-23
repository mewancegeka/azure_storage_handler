# Data Model: ADLS SAS File Manager Library

## Entities

### StorageConnectionConfig

Represents the configuration needed to connect to one ADLS Gen2 storage account and resolve its
SAS token.

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `account_name` | `str` | Yes | Storage account name (without domain suffix); used to build `https://{account_name}.dfs.core.windows.net`. |
| `key_vault_url` | `str` | Conditionally | Required unless `sas_token` is supplied directly. Full URL of the Key Vault, e.g. `https://my-vault.vault.azure.net/`. |
| `key_vault_secret_name` | `str` | Conditionally | Required unless `sas_token` is supplied directly. Name of the secret holding the SAS token string. |
| `sas_token` | `str` \| `None` | No | Optional direct override. When provided, Key Vault is not consulted for the SAS token. |

**Validation rules**:
- `account_name` MUST be non-empty; validated at initialization, before any network call (FR-014,
  User Story 3 acceptance scenario 1).
- Either `sas_token` must be provided, or both `key_vault_url` and `key_vault_secret_name` must be
  provided; otherwise initialization MUST fail with a configuration error (FR-005a).
- None of these fields are ever logged in full; `sas_token` and any resolved token value MUST be
  excluded from log/error output (FR-013).

### FileSystem (Container)

Represents the top-level namespace within the storage account. Identified by `file_system_name`
(a `str`). Not a persisted object in this library; it is a parameter passed to operations and/or
an internal SDK client handle (`FileSystemClient`) obtained from the account-level client.

### Directory

A path within a file system that can contain files and subdirectories.

| Field | Type | Notes |
|-------|------|-------|
| `file_system_name` | `str` | Owning file system. |
| `path` | `str` | Directory path within the file system, e.g. `source_name/year/month/day`. |

**Supported operations**: create (idempotent — no error if it already exists), list contents,
rename/move to a new path within the same file system, delete (recursive delete of contents).

**State/behavior notes**:
- Create: if the directory already exists, treat as success (FR-005).
- List: returns names of immediate files and subdirectories under `path`.
- Rename/Move: target path format is `{file_system_name}/{new_directory_path}`.
- Delete: removes the directory and its contents.

### File

A path within a directory (or directly within a file system) that holds byte content.

| Field | Type | Notes |
|-------|------|-------|
| `file_system_name` | `str` | Owning file system. |
| `directory_path` | `str` | Parent directory path. |
| `file_name` | `str` | Name of the file; for uploads, the library MUST append a timestamp to keep the name unique (FR-009a). |

**Supported operations**: upload (local file or in-memory bytes; overwrite enabled by default),
download (to a local path), append data (bytes appended at the current end-of-file offset, then
flushed), delete.

### JsonPayloadRecord

Represents a JSON-serializable payload the caller wants persisted as a `.json` file under a given
directory path (e.g., `source_name/year/month/day/`), per Acceptance Scenario 7 of User Story 1.

| Field | Type | Notes |
|-------|------|-------|
| `directory_path` | `str` | Target directory (created if missing, per Directory create semantics). |
| `payload` | `dict` \| `list` \| any JSON-serializable value | Serialized to UTF-8 JSON text before upload. |
| `file_name` | `str` \| `None` | Optional explicit file name (without extension apply rules below); if omitted, the library generates one that includes a timestamp. |

**Validation rules**:
- `payload` MUST be JSON-serializable; a serialization failure MUST raise a clear error before any
  network call is attempted.
- The resulting file MUST be written with a timestamp in its name (reuses File upload semantics,
  FR-009a) and a `.json` extension.

## Relationships

```text
StorageConnectionConfig 1 --- 1 AdlsSasFileManager (the public class)
AdlsSasFileManager 1 --- * FileSystem (by name, per call)
FileSystem 1 --- * Directory
Directory 1 --- * Directory (subdirectories)
Directory 1 --- * File
JsonPayloadRecord --- writes to --- File (a File whose content is JSON text)
```

## Error Model

All library-raised errors are typed exceptions (see `contracts/exceptions.md`) rather than
unmodified Azure SDK exceptions, so callers can catch specific, documented failure categories
without depending on `azure-core`/`azure-storage-file-datalake` exception types directly:

- `ConfigurationError` — invalid/missing required configuration (e.g., empty `account_name`,
  neither `sas_token` nor Key Vault settings provided).
- `SecretRetrievalError` — Key Vault secret could not be retrieved (missing vault, missing secret,
  access denied); never includes the attempted secret value.
- `AuthorizationError` — the SAS token was rejected or lacks required permissions for the
  attempted operation.
- `PathNotFoundError` — the target directory/file does not exist for an operation that requires
  it to exist (e.g., download, rename, delete, append).
- `StorageOperationError` — a catch-all for other storage-service failures (network errors,
  service-side errors) not covered by the above.
