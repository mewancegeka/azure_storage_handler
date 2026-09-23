# Contract: AdlsSasFileManager Public Interface

This is the public Python interface the library exposes to a consuming project (per FR-001 and
FR-015: one class, no need for the caller to construct SDK clients directly).

## Construction

```python
class AdlsSasFileManager:
    def __init__(
        self,
        account_name: str,
        *,
        key_vault_url: str | None = None,
        key_vault_secret_name: str | None = None,
        sas_token: str | None = None,
    ) -> None:
        """
        Initialize the manager for a single ADLS Gen2 storage account.

        Exactly one SAS token source MUST be resolvable:
        - `sas_token` is provided directly, OR
        - both `key_vault_url` and `key_vault_secret_name` are provided, and the named secret
          in that Key Vault holds a valid SAS token string.

        Raises:
            ConfigurationError: if `account_name` is empty, or if no valid SAS token source
                is resolvable from the arguments given.
            SecretRetrievalError: if Key Vault retrieval is attempted and fails.
        """
```

## Directory operations

```python
def create_directory(self, file_system_name: str, directory_path: str) -> None:
    """Create `directory_path` in `file_system_name`. No-op (success) if it already exists.

    Raises:
        AuthorizationError, StorageOperationError
    """

def list_directory(self, file_system_name: str, directory_path: str) -> list[str]:
    """Return the names of immediate files and subdirectories under `directory_path`.

    Raises:
        PathNotFoundError, AuthorizationError, StorageOperationError
    """

def rename_directory(self, file_system_name: str, directory_path: str, new_directory_path: str) -> None:
    """Rename/move a directory to `new_directory_path` within the same file system.

    Raises:
        PathNotFoundError, AuthorizationError, StorageOperationError
    """

def delete_directory(self, file_system_name: str, directory_path: str) -> None:
    """Delete a directory and its contents.

    Raises:
        PathNotFoundError, AuthorizationError, StorageOperationError
    """
```

## File operations

```python
def upload_file(
    self,
    file_system_name: str,
    directory_path: str,
    local_file_path: str,
    file_name: str | None = None,
) -> str:
    """Upload a local file into `directory_path`. The stored file name includes a timestamp
    and overwrite is enabled by default. Returns the actual stored file name.

    Raises:
        AuthorizationError, StorageOperationError
    """

def download_file(
    self,
    file_system_name: str,
    directory_path: str,
    file_name: str,
    local_destination_path: str,
) -> None:
    """Download a file from `directory_path` to `local_destination_path`.

    Raises:
        PathNotFoundError, AuthorizationError, StorageOperationError
    """

def append_to_file(
    self,
    file_system_name: str,
    directory_path: str,
    file_name: str,
    data: bytes,
) -> None:
    """Append `data` to the end of an existing file and flush it.

    Raises:
        PathNotFoundError, AuthorizationError, StorageOperationError
    """

def delete_file(self, file_system_name: str, directory_path: str, file_name: str) -> None:
    """Delete a file.

    Raises:
        PathNotFoundError, AuthorizationError, StorageOperationError
    """
```

## JSON payload operation

```python
def save_json(
    self,
    file_system_name: str,
    directory_path: str,
    payload: object,
    file_name: str | None = None,
) -> str:
    """Serialize `payload` to JSON and save it as a timestamped `.json` file under
    `directory_path` (creating the directory if it does not exist). Returns the stored file name.

    Raises:
        ConfigurationError: if `payload` is not JSON-serializable.
        AuthorizationError, StorageOperationError
    """
```

## Exceptions (see also data-model.md § Error Model)

```python
class AdlsSasFileManagerError(Exception): ...
class ConfigurationError(AdlsSasFileManagerError): ...
class SecretRetrievalError(AdlsSasFileManagerError): ...
class AuthorizationError(AdlsSasFileManagerError): ...
class PathNotFoundError(AdlsSasFileManagerError): ...
class StorageOperationError(AdlsSasFileManagerError): ...
```

All exception messages MUST NOT include the SAS token value, the Key Vault secret value, or any
other secret value (FR-013).
