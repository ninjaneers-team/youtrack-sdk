from collections.abc import AsyncGenerator

import httpx
import pytest
import pytest_asyncio
import respx

from youtrack_sdk.async_client import AsyncClient
from youtrack_sdk.entities import Issue


@pytest_asyncio.fixture
async def client() -> AsyncGenerator[AsyncClient]:
    """Fixture providing an AsyncClient instance with cleanup."""
    async with AsyncClient(base_url="https://server", token="test") as client:  # noqa: S106
        yield client


@pytest.mark.asyncio
async def test_context_manager() -> None:
    """Test that AsyncClient can be used as an async context manager."""
    async with AsyncClient(base_url="https://server", token="test") as client:  # noqa: S106
        assert isinstance(client, AsyncClient)


@pytest.mark.asyncio
@respx.mock
async def test_get_issue(client: AsyncClient) -> None:
    """Test basic issue retrieval."""
    mock_response = {
        "$type": "Issue",
        "id": "1-1",
        "idReadable": "TEST-1",
        "summary": "Test issue",
    }
    respx.get("https://server/api/issues/1").mock(
        return_value=httpx.Response(200, json=mock_response),
    )

    issue = await client.get_issue(issue_id="1")
    assert isinstance(issue, Issue)
    assert issue.id == "1-1"
    assert issue.id_readable == "TEST-1"
    assert issue.summary == "Test issue"


@pytest.mark.asyncio
async def test_get_absolute_url(client: AsyncClient) -> None:
    """Test URL construction."""
    assert client.get_absolute_url(path="/issue/1") == "https://server/issue/1"


@pytest.mark.asyncio
async def test_async_context_manager_cleanup() -> None:
    """Test that the async context manager properly closes the client."""
    client = AsyncClient(base_url="https://server", token="test")  # noqa: S106
    async with client:
        assert not client._client.is_closed  # type: ignore[reportPrivateUsage]
    assert client._client.is_closed  # type: ignore[reportPrivateUsage]
