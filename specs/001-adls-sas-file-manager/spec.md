# Feature Specification: ADLS SAS File Manager Library

**Feature Branch**: `[001-adls-sas-file-manager]`

**Created**: 2026-09-23

**Status**: Draft

**Input**: User description: "Create a Python class, which can be included as a library to another project, where the class manages directories and files in an ADLS storage account. It should use SAS Token method for authorization. All secrets must be fetched from Azure Key Vault. Key vault settings can be passed as parameters. Use the link https://learn.microsoft.com/en-us/azure/storage/blobs/data-lake-storage-directory-file-acl-python?tabs=sas-token as a reference."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Manage directories and files in ADLS via a reusable library (Priority: P1)

A developer integrating another project imports the library, configures it with storage account
and Key Vault details, and uses it to create, list, rename/move, and delete directories, and to
upload, download, append to, and delete files in an Azure Data Lake Storage (ADLS) Gen2 account,
without needing to write their own Storage SDK or SAS-handling code.

**Why this priority**: This is the core value of the library; without directory and file
management operations, there is no usable product.

**Independent Test**: Can be fully tested by instantiating the class against a test ADLS account,
performing create/list/rename/delete directory operations and upload/download/append/delete file
operations, and verifying the resulting state in the storage account.

**Acceptance Scenarios**:

1. **Given** a valid SAS token and storage account name, **When** the developer asks the library to
   create a directory in a file system, **Then** the directory exists in the target file system.
2. **Given** an existing directory with files, **When** the developer asks the library to list its
   contents, **Then** the library returns the names of the contained files and subdirectories.
3. **Given** an existing directory, **When** the developer asks the library to rename/move it,
   **Then** the directory appears at the new path and no longer exists at the old path.
4. **Given** an existing directory, **When** the developer asks the library to delete it,
   **Then** the directory and its contents no longer exist in the file system.
5. **Given** a local file, **When** the developer asks the library to upload it to a directory,
   **Then** the file exists in that directory with the same content.
6. **Given** a file in a directory, **When** the developer asks the library to download it,
   **Then** the local copy matches the remote file's content byte-for-byte.
7. **Given** an existing file, **When** the developer asks the library to append data to it,
   **Then** the file's content reflects the original content followed by the appended data.
8. **Given** an existing file, **When** the developer asks the library to delete it,
   **Then** the file no longer exists in the directory.

---

### User Story 2 - Authorize storage access using a SAS token retrieved from Azure Key Vault (Priority: P1)

A developer configures the library with Azure Key Vault connection settings (vault URL and secret
name) instead of embedding a SAS token directly in application code or configuration files. The
library retrieves the current SAS token from Key Vault at initialization and uses it to authorize
all ADLS operations.

**Why this priority**: Without secure retrieval of the SAS token, secrets end up hardcoded or
stored insecurely, directly violating the project's security requirements; this is equally
foundational to User Story 1.

**Independent Test**: Can be fully tested by storing a SAS token as a secret in a test Key Vault,
configuring the library with the vault URL and secret name, and verifying the library
successfully authorizes ADLS requests without the caller ever supplying the raw SAS token value.

**Acceptance Scenarios**:

1. **Given** valid Key Vault settings (vault URL and secret name) pointing to a secret containing a
   SAS token, **When** the library is initialized, **Then** it retrieves the SAS token from Key
   Vault and uses it to authorize subsequent ADLS operations.
2. **Given** Key Vault settings that point to a nonexistent secret or vault, **When** the library
   is initialized, **Then** it raises a clear, actionable error identifying that the secret could
   not be retrieved, without exposing sensitive details in the error message.
3. **Given** a caller who supplies a raw SAS token directly instead of Key Vault settings,
   **When** the library is initialized with that direct SAS token override, **Then** it uses the
   supplied token instead of retrieving one from Key Vault, while Key Vault retrieval remains the
   default path when no direct token is provided.

---

### User Story 3 - Discover configuration and connection errors early (Priority: P2)

A developer supplies invalid or incomplete configuration (e.g., missing storage account name, bad
Key Vault settings, invalid SAS token, or a permissions-denied response from the storage service).
The library surfaces a clear, actionable error at the point of failure rather than an ambiguous
low-level SDK exception.

**Why this priority**: Improves developer experience and troubleshooting speed once the core
functionality (User Stories 1-2) works, but the library is still usable without this refinement.

**Independent Test**: Can be fully tested by supplying invalid configuration values (missing
account name, invalid vault URL, expired/invalid SAS token, insufficient SAS permissions) and
verifying each produces a distinguishable, descriptive error rather than an unhandled exception
or silent failure.

**Acceptance Scenarios**:

1. **Given** a missing or empty storage account name, **When** the library is initialized,
   **Then** it raises a clear configuration error before attempting any network call.
2. **Given** a SAS token that has expired or lacks required permissions, **When** an ADLS
   operation is attempted, **Then** the library raises an error that identifies the operation and
   the authorization failure, without leaking the SAS token value in logs or error messages.

### Edge Cases

- How does the library handle attempts to operate on a path that does not exist (e.g., download,
  rename, or delete a nonexistent directory/file)?
- How does the library handle a SAS token that expires partway through a long-running operation
  (e.g., a large file upload/download)?
- How does the library handle file systems (containers) that do not yet exist when a caller tries
  to create a directory inside them?
- How does the library handle very large files during upload/download/append given the
  4000 MiB per-request limit on append operations noted in the reference documentation?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The library MUST expose a single class that can be imported and instantiated by a
  consuming project to manage directories and files in one ADLS Gen2 storage account.
- **FR-002**: The library MUST authorize all storage operations using a SAS token, consistent with
  the SAS token authorization method described in the reference documentation.
- **FR-003**: The library MUST retrieve the SAS token (and any other secrets it needs) from Azure
  Key Vault rather than accepting them as plaintext configuration from the caller.
- **FR-004**: The library MUST accept Azure Key Vault connection settings (at minimum, the vault
  URL and the secret name holding the SAS token) as initialization parameters.
- **FR-005**: The library MUST support creating a directory within a specified file system
  (container), idempotently: if the directory already exists, the library MUST treat this as
  success and proceed without error, rather than creating it again or raising an error.
- **FR-005a**: The library MUST allow a caller to optionally supply a raw SAS token directly at
  initialization as an override; when no direct token is supplied, the library MUST retrieve the
  SAS token from the configured Azure Key Vault secret.
- **FR-009a**: The library MUST upload files with a timestamp included in the file name and MUST
  perform uploads with overwrite enabled by default.
- **FR-006**: The library MUST support listing the contents (files and subdirectories) of a
  specified directory.
- **FR-007**: The library MUST support renaming or moving a directory to a new path within the
  same file system.
- **FR-008**: The library MUST support deleting a directory.
- **FR-009**: The library MUST support uploading a local file into a specified directory.
- **FR-010**: The library MUST support downloading a file from a specified directory to a local
  path.
- **FR-011**: The library MUST support appending data to an existing file.
- **FR-012**: The library MUST support deleting a file.
- **FR-013**: The library MUST NOT log or include the SAS token or Key Vault secret values in any
  error message, exception, or log output.
- **FR-014**: The library MUST raise clear, actionable errors when Key Vault secret retrieval
  fails, when required configuration is missing, or when a storage operation fails due to
  authorization or connectivity problems.
- **FR-015**: The library MUST NOT require the consuming project to construct the underlying
  storage or Key Vault SDK clients directly; the class MUST manage those internally.

### Key Entities

- **Storage Connection Configuration**: Represents the target ADLS account (storage account name)
  and the Key Vault settings needed to retrieve the SAS token (vault URL, secret name).
- **File System (Container)**: The top-level namespace within the storage account that contains
  directories and files.
- **Directory**: A path within a file system that can contain files and subdirectories, and
  supports create, list, rename/move, and delete operations.
- **File**: A path within a directory that supports upload, download, append, and delete
  operations.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A developer can perform any supported directory or file operation (create, list,
  rename/move, delete, upload, download, append) using no more than one method call on the
  library class per operation.
- **SC-002**: 100% of the operations described in the reference documentation (create directory,
  rename/move directory, delete directory, upload file, append data, download file, list directory
  contents, delete file) are available through the library's public interface.
- **SC-003**: The SAS token value never appears in plaintext in the consuming project's source
  code or configuration; it is retrievable only through the configured Key Vault reference.
- **SC-004**: When misconfigured (bad account name, bad Key Vault reference, invalid/expired SAS
  token), the library reports a specific, human-readable error identifying which step failed in
  100% of tested failure scenarios.

## Assumptions

- The target storage account already has hierarchical namespace (HNS) enabled, as required for
  ADLS Gen2 directory and file operations.
- The SAS token stored in Azure Key Vault already has the permissions, resource scope, and
  expiration needed for the operations the library exposes; generating or rotating the SAS token
  is out of scope for this library.
- The consuming project has network access and identity/permissions to read the specified secret
  from the specified Key Vault; provisioning that access is out of scope for this library.
- The library targets a single storage account and a single SAS token per instance; managing
  multiple storage accounts requires creating multiple instances.
- Standard Python exception handling (raising typed exceptions) is an acceptable error-reporting
  mechanism for this library; no additional structured error-code system is required unless
  specified later.
