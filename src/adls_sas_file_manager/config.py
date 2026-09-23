"""Connection configuration for the ADLS SAS File Manager library."""

from __future__ import annotations

from dataclasses import dataclass

from .errors import ConfigurationError


@dataclass(frozen=True)
class StorageConnectionConfig:
    """Configuration needed to connect to one ADLS Gen2 storage account.

    Either `sas_token` must be provided directly, or both `key_vault_url` and
    `key_vault_secret_name` must be provided so the SAS token can be retrieved
    from Azure Key Vault (see data-model.md § StorageConnectionConfig).
    """

    account_name: str
    key_vault_url: str | None = None
    key_vault_secret_name: str | None = None
    sas_token: str | None = None

    def __post_init__(self) -> None:
        if not self.account_name:
            raise ConfigurationError("account_name is required and must be non-empty.")

        has_direct_token = bool(self.sas_token)
        has_key_vault_settings = bool(self.key_vault_url) and bool(self.key_vault_secret_name)

        if not has_direct_token and not has_key_vault_settings:
            raise ConfigurationError(
                "Either sas_token must be provided, or both key_vault_url and "
                "key_vault_secret_name must be provided."
            )

    @property
    def account_url(self) -> str:
        """The ADLS Gen2 account endpoint URL for this account."""
        return f"https://{self.account_name}.dfs.core.windows.net"
