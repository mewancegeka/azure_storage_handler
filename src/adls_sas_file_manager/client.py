"""Public client for managing directories and files in an ADLS Gen2 storage account.

See contracts/adls_sas_file_manager.md for the full interface contract.
"""

from __future__ import annotations

from azure.storage.filedatalake import DataLakeServiceClient

from ._internal.secret_resolver import resolve_sas_token
from .config import StorageConnectionConfig


class AdlsSasFileManager:
    """Manage directories and files in one ADLS Gen2 storage account using a SAS token."""

    def __init__(
        self,
        account_name: str,
        *,
        key_vault_url: str | None = None,
        key_vault_secret_name: str | None = None,
        sas_token: str | None = None,
    ) -> None:
        config = StorageConnectionConfig(
            account_name=account_name,
            key_vault_url=key_vault_url,
            key_vault_secret_name=key_vault_secret_name,
            sas_token=sas_token,
        )
        resolved_sas_token = resolve_sas_token(config)
        self._service_client = DataLakeServiceClient(
            account_url=config.account_url, credential=resolved_sas_token
        )
