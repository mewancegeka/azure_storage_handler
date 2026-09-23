# Quickstart: ADLS SAS File Manager Library

This guide validates that the library works end-to-end. It assumes Python 3.13, VS Code, and an
ADLS Gen2 storage account plus an Azure Key Vault you control.

## Prerequisites

- Python 3.13 installed and selected as the interpreter in VS Code.
- An Azure storage account with hierarchical namespace (HNS) enabled.
- A SAS token for that account, stored as a secret in an Azure Key Vault.
- Azure credentials available locally for `DefaultAzureCredential` to authenticate to Key Vault
  (e.g., `az login`, or environment variables — see `research.md`).

## Setup

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install azure-storage-file-datalake azure-keyvault-secrets azure-identity pytest
```

## Run unit tests (no live Azure resources required)

```powershell
pytest tests/unit
```

Expected outcome: all unit tests pass using mocked Azure SDK clients (see `data-model.md` and
`contracts/adls_sas_file_manager.md` for the behaviors under test).

## Run the integration scenario (requires live Key Vault + ADLS account)

Set environment variables (names illustrative; finalize during implementation):

```powershell
$env:ADLS_ACCOUNT_NAME = "<your-storage-account-name>"
$env:ADLS_KEY_VAULT_URL = "https://<your-vault-name>.vault.azure.net/"
$env:ADLS_KEY_VAULT_SECRET_NAME = "<secret-name-holding-sas-token>"
$env:ADLS_FILE_SYSTEM_NAME = "<test-container-name>"

pytest tests/integration -m integration
```

Expected outcome:

1. `create_directory("<file_system>", "quickstart/demo")` succeeds and is idempotent if run twice.
2. `save_json("<file_system>", "quickstart/demo", {"hello": "world"})` creates a timestamped
   `.json` file whose content matches the payload when downloaded and parsed.
3. `upload_file(...)` followed by `download_file(...)` round-trips a local file's bytes exactly.
4. `append_to_file(...)` results in a file whose content is the original content followed by the
   appended bytes.
5. `list_directory("<file_system>", "quickstart/demo")` includes the uploaded file names.
6. `rename_directory("<file_system>", "quickstart/demo", "quickstart/demo-renamed")` moves the
   directory; the old path no longer resolves and the new path contains the same files.
7. `delete_directory("<file_system>", "quickstart/demo-renamed")` removes the directory; a
   subsequent `list_directory` call on that path raises `PathNotFoundError`.

## Validating security requirements

- Confirm no test or example ever prints/logs `sas_token`, the resolved SAS token, or the Key
  Vault secret value (constitution: Secure by Default; FR-013).
- Confirm `AdlsSasFileManager(account_name="")` raises `ConfigurationError` before any network
  call (User Story 3, acceptance scenario 1).
