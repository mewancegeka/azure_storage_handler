# Research: ADLS SAS File Manager Library

## Decision: Language & runtime version

- **Decision**: Python 3.13
- **Rationale**: The user requested "the latest compatible Python version." The two required
  Azure SDKs — `azure-storage-file-datalake` (12.25.0) and `azure-keyvault-secrets` (4.11.2) —
  both officially classify support up to Python 3.13. `azure-storage-file-datalake` also lists
  3.14, but `azure-keyvault-secrets` does not yet, so 3.13 is the newest version supported by
  every required dependency simultaneously.
- **Alternatives considered**: Python 3.14 (rejected: not yet classified as supported by
  `azure-keyvault-secrets`, would risk untested behavior); Python 3.9–3.12 (rejected: not the
  latest compatible version, though they remain valid fallback targets if 3.13 is unavailable in
  a consumer's environment).

## Decision: Core dependencies

- **Decision**: `azure-storage-file-datalake` for ADLS Gen2 directory/file operations,
  `azure-keyvault-secrets` + `azure-identity` for Key Vault secret retrieval.
- **Rationale**: These are the official Microsoft-maintained SDKs for the exact operations named
  in the spec (create/list/rename/delete directory; upload/download/append/delete file) and for
  retrieving secrets from Key Vault. Reference: the Microsoft Learn article the user supplied
  (data-lake-storage-directory-file-acl-python, SAS token tab) uses
  `azure.storage.filedatalake.DataLakeServiceClient` with a SAS token string as the credential.
- **Alternatives considered**: Direct REST calls via `requests` (rejected: reinvents
  retry/auth/error-handling already provided by the official SDK, higher maintenance cost and
  security risk).

## Decision: Authentication flow

- **Decision**: The library authenticates to Key Vault using `azure.identity.DefaultAzureCredential`
  (so the consuming project's existing Azure identity, e.g. managed identity, Azure CLI login, or
  environment credentials, is reused with no extra secret to manage), retrieves the SAS token
  string from a named secret via `azure.keyvault.secrets.SecretClient.get_secret`, and passes that
  SAS token string directly as the `credential` argument when constructing
  `azure.storage.filedatalake.DataLakeServiceClient`. A caller may alternatively supply a raw SAS
  token string directly at initialization (per the clarified requirement), which bypasses Key
  Vault retrieval entirely for that instance.
- **Rationale**: Matches the reference documentation's SAS-token tab exactly, and keeps Key Vault
  access itself using Azure's recommended credential chain rather than another embedded secret.
- **Alternatives considered**: Storing the Key Vault access credential itself as a secret
  (rejected: security anti-pattern — would require a secret to access secrets).

## Decision: Testing strategy

- **Decision**: `pytest` for unit tests using mocked Azure SDK clients (`unittest.mock`), plus a
  clearly separated, optionally-skipped integration test suite that exercises a real (or
  Azurite-style) ADLS Gen2 endpoint and Key Vault when credentials are available via environment
  variables.
- **Rationale**: Unit tests must run without live Azure resources for fast, reliable CI. The
  constitution's Testable Changes principle requires integration tests when a change depends on
  an actual storage service or authentication flow, so those are included but gated behind
  environment/config availability rather than required for every test run.
- **Alternatives considered**: Only integration tests against live Azure resources (rejected: slow,
  costly, and unusable in most contributors' environments without provisioned Azure resources).

## Decision: Development environment / IDE

- **Decision**: VS Code, per explicit user instruction. No IDE-specific runtime behavior is
  required in the library itself; this affects only recommended workspace settings (e.g., Python
  interpreter selection, linting) documented in quickstart.md, not the library's public API.
- **Rationale**: User-specified constraint.
- **Alternatives considered**: N/A (explicit instruction, not a design choice).

## Decision: Package layout

- **Decision**: Single-project Python library layout (`src/` package + `tests/`), packaged so it
  can be installed into another project (e.g., via `pip install` from a local path, a private
  index, or a git dependency).
- **Rationale**: The spec explicitly frames this as "a library to another project" (FR-001,
  FR-015): no CLI, web service, or UI is requested.
- **Alternatives considered**: Multi-package/monorepo layout (rejected: unnecessary complexity for
  a single-class library; would violate the constitution's Observable and Operationally Simple
  principle, which requires new abstractions/complexity to be justified by a concrete need).
