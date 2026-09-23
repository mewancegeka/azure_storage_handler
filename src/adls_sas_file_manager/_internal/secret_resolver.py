"""Resolve the SAS token used to authorize ADLS Gen2 operations.

Resolution order (see research.md § Decision: Authentication flow):
1. A directly supplied `sas_token` on the `StorageConnectionConfig` always takes
   precedence and Key Vault is never consulted in that case (FR-005a).
2. Otherwise, the SAS token is retrieved from the configured Azure Key Vault
   secret using `DefaultAzureCredential` for Key Vault authentication.

Any failure to retrieve the secret is wrapped in `SecretRetrievalError` with a
generic message that never includes the secret name, vault URL, or any
resolved/attempted secret value (FR-013).
"""

from __future__ import annotations

from azure.core.exceptions import AzureError
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

from ..config import StorageConnectionConfig
from ..errors import SecretRetrievalError


def resolve_sas_token(config: StorageConnectionConfig) -> str:
    """Return the SAS token to use, per the resolution order documented above."""
    if config.sas_token:
        return config.sas_token

    try:
        credential = DefaultAzureCredential()
        secret_client = SecretClient(vault_url=config.key_vault_url, credential=credential)
        secret = secret_client.get_secret(config.key_vault_secret_name)
    except AzureError as exc:
        raise SecretRetrievalError(
            "Failed to retrieve the SAS token from the configured Azure Key Vault secret."
        ) from exc

    if not secret.value:
        raise SecretRetrievalError(
            "The configured Azure Key Vault secret does not contain a usable value."
        )

    return secret.value
