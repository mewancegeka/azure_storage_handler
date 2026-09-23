"""Shared pytest fixtures providing mocked Azure SDK clients for unit tests.

Unit tests must never contact real Azure services; use these fixtures instead
of `AdlsSasFileManager`'s real Azure SDK client construction where possible.
"""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest


@pytest.fixture
def mock_file_client() -> MagicMock:
    return MagicMock(name="DataLakeFileClient")


@pytest.fixture
def mock_directory_client(mock_file_client: MagicMock) -> MagicMock:
    directory_client = MagicMock(name="DataLakeDirectoryClient")
    directory_client.get_file_client.return_value = mock_file_client
    return directory_client


@pytest.fixture
def mock_file_system_client(mock_directory_client: MagicMock) -> MagicMock:
    file_system_client = MagicMock(name="FileSystemClient")
    file_system_client.get_directory_client.return_value = mock_directory_client
    return file_system_client


@pytest.fixture
def mock_service_client(mock_file_system_client: MagicMock) -> MagicMock:
    service_client = MagicMock(name="DataLakeServiceClient")
    service_client.get_file_system_client.return_value = mock_file_system_client
    return service_client
