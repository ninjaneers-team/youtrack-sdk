from collections.abc import AsyncGenerator
from collections.abc import Callable
from datetime import UTC
from datetime import datetime
from functools import wraps
from http import HTTPMethod
from pathlib import Path
from typing import Any
from typing import Final
from unittest.mock import ANY
from unittest.mock import AsyncMock
from unittest.mock import patch

import httpx
import pytest
import pytest_asyncio
import respx

import youtrack_sdk.async_client
from tests.test_definitions import TEST_AGILE
from tests.test_definitions import TEST_CUSTOM_ISSUE
from tests.test_definitions import TEST_CUSTOM_ISSUE_2
from tests.test_definitions import TEST_ISSUE
from tests.test_definitions import TEST_ISSUE_2
from tests.test_definitions import TEST_SPRINT
from tests.test_definitions import CustomIssue
from youtrack_sdk.async_client import AsyncClient
from youtrack_sdk.base_client import BaseClient
from youtrack_sdk.entities import Agile
from youtrack_sdk.entities import AgileRef
from youtrack_sdk.entities import DurationValue
from youtrack_sdk.entities import Issue
from youtrack_sdk.entities import IssueAttachment
from youtrack_sdk.entities import IssueComment
from youtrack_sdk.entities import IssueLink
from youtrack_sdk.entities import IssueLinkType
from youtrack_sdk.entities import IssueWorkItem
from youtrack_sdk.entities import Project
from youtrack_sdk.entities import Sprint
from youtrack_sdk.entities import SprintRef
from youtrack_sdk.entities import Tag
from youtrack_sdk.entities import User
from youtrack_sdk.entities import WorkItemType
from youtrack_sdk.exceptions import YouTrackException
from youtrack_sdk.exceptions import YouTrackNotFound
from youtrack_sdk.exceptions import YouTrackUnauthorized
from youtrack_sdk.types import TimeoutSpec


def mock_response(
    url: str,
    response_name: str,
    method: HTTPMethod = HTTPMethod.GET,
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    def wrapper(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        async def inner(*args: Any, **kwargs: Any) -> Any:  # noqa: ANN401
            with respx.mock:
                respx.route(method=method, url=url).mock(
                    return_value=httpx.Response(
                        200,
                        text=(Path(__file__).parent / "responses" / f"{response_name}.json").read_text(),
                    )
                )
                return await func(*args, **kwargs)

        return inner

    return wrapper


@pytest_asyncio.fixture
async def client() -> AsyncGenerator[AsyncClient]:
    """Fixture providing an AsyncClient instance with cleanup."""
    async with AsyncClient(base_url="https://server", token="test") as client:  # noqa: S106
        yield client


@pytest.mark.asyncio
@patch.object(
    youtrack_sdk.async_client.httpx.AsyncClient,
    "request",
    side_effect=httpx.ConnectTimeout("timeout"),
)
async def test_client_timeout(mock_request: Any) -> None:  # noqa: ANN401
    client: Final = AsyncClient(base_url="https://server", token="test", timeout=123)  # noqa: S106
    with pytest.raises(httpx.ConnectTimeout):
        await client.get_issue(issue_id="1")
    mock_request.assert_called_once_with(
        method=HTTPMethod.GET,
        url=ANY,
        content=None,
        files=None,
        headers={},
    )


@pytest.mark.asyncio
async def test_get_absolute_url(client: AsyncClient) -> None:
    assert client.get_absolute_url(path="/issue/1") == "https://server/issue/1"


@pytest.mark.asyncio
@mock_response(url="https://server/api/issues/1", response_name="issue")
async def test_get_issue(client: AsyncClient) -> None:
    assert await client.get_issue(issue_id="1") == TEST_ISSUE


def test_issue_url() -> None:
    assert TEST_ISSUE.url == "/issue/HD-25"


@pytest.mark.asyncio
@mock_response(url="https://server/api/issues/", response_name="issues")
async def test_get_issues(client: AsyncClient) -> None:
    assert await client.get_issues(query="in:TD for:me") == (TEST_ISSUE, TEST_ISSUE_2)


@pytest.mark.asyncio
@mock_response(url="https://server/api/issues/", response_name="issues_custom_model")
async def test_get_issues_custom_model(client: AsyncClient) -> None:
    assert await client.get_issues(model=CustomIssue, custom_fields=["State", "Type"]) == (
        TEST_CUSTOM_ISSUE,
        TEST_CUSTOM_ISSUE_2,
    )


@pytest.mark.asyncio
@mock_response(url="https://server/api/issues/1/comments", response_name="issue_comments")
async def test_get_issue_comments(client: AsyncClient) -> None:
    assert await client.get_issue_comments(issue_id="1") == (
        IssueComment.model_construct(
            type="IssueComment",
            id="4-296",
            text="*Hello*, world!",
            text_preview="<strong>Hello</strong>, world!",
            created=datetime(2021, 12, 14, 11, 17, 48, tzinfo=UTC),
            updated=None,
            author=User.model_construct(
                type="User",
                id="1-3",
                ring_id="b0fea1e1-ed18-43f6-a99d-40044fb1dfb0",
                login="support",
                email="support@example.com",
            ),
            attachments=[],
            deleted=False,
        ),
        IssueComment.model_construct(
            type="IssueComment",
            id="4-443",
            text="Sample _comment_",
            text_preview="Sample <em>comment</em>",
            created=datetime(2021, 12, 15, 12, 51, 40, tzinfo=UTC),
            updated=datetime(2021, 12, 15, 13, 8, 20, tzinfo=UTC),
            author=User.model_construct(
                type="User",
                id="1-17",
                ring_id="c5d08431-dd52-4cdd-9911-7ec3a18ad117",
                login="max.demo",
                email="max@example.com",
            ),
            attachments=[],
            deleted=True,
        ),
        IssueComment.model_construct(
            type="IssueComment",
            id="4-678",
            text="Comment with attachments",
            text_preview="One attachment",
            created=datetime(2021, 12, 21, 16, 41, 33, tzinfo=UTC),
            updated=None,
            author=User.model_construct(
                type="User",
                id="1-9",
                ring_id="f19c93e1-833b-407b-a4de-7f9a3370aaf3",
                login="sam",
                email="sam@example.com",
            ),
            attachments=[
                IssueAttachment.model_construct(
                    id="8-312",
                    type="IssueAttachment",
                    created=datetime(2021, 12, 21, 16, 41, 33, tzinfo=UTC),
                    updated=datetime(2021, 12, 21, 16, 41, 35, tzinfo=UTC),
                    author=None,
                    url="/attachments/url",
                    mime_type="text/plain",
                    name="test.txt",
                ),
            ],
            deleted=False,
        ),
    )


@pytest.mark.asyncio
@mock_response(url="https://server/api/issues/1/timeTracking/workItems", response_name="issue_work_items")
async def test_get_issue_work_items(client: AsyncClient) -> None:
    assert await client.get_issue_work_items(issue_id="1") == (
        IssueWorkItem.model_construct(
            type="IssueWorkItem",
            id="12-14",
            author=User.model_construct(
                type="User",
                id="1-64",
                name="Paul Lawson",
                ring_id="d53ece48-4c60-4b88-b93f-68392b975087",
                login="paul.lawson",
                email="",
            ),
            creator=User.model_construct(
                type="User",
                id="1-52",
                name="Mary Jane",
                ring_id="26677773-c425-4f47-b62c-dbfb2ad21e8f",
                login="mary.jane",
                email="mary.jane@example.com",
            ),
            text="Working hard",
            text_preview='<div class="wiki text common-markdown"><p>Working hard</p>\n</div>',
            work_item_type=WorkItemType(
                id="1-0",
                name="Development",
            ),
            created=datetime(2024, 3, 13, 11, 55, 27, tzinfo=UTC),
            updated=None,
            duration=DurationValue(
                id="100",
                minutes=100,
                presentation="1h 40m",
            ),
            date=datetime(2024, 3, 3, 0, 0, tzinfo=UTC),
        ),
    )


@pytest.mark.asyncio
@mock_response(url="https://server/api/admin/projects", response_name="projects")
async def test_get_projects(client: AsyncClient) -> None:
    assert await client.get_projects() == (
        Project.model_construct(
            type="Project",
            id="0-0",
            name="Demo project",
            short_name="DEMO",
        ),
        Project.model_construct(
            type="Project",
            id="0-5",
            name="Help Desk",
            short_name="HD",
        ),
    )


@pytest.mark.asyncio
@mock_response(
    url="https://server/api/admin/projects/DEMO/timeTrackingSettings/workItemTypes",
    response_name="work_item_types",
)
async def test_get_project_work_item_types(client: AsyncClient) -> None:
    assert await client.get_project_work_item_types(project_id="DEMO") == (
        WorkItemType.model_construct(
            type="WorkItemType",
            id="1-0",
            name="Development",
        ),
        WorkItemType.model_construct(
            type="WorkItemType",
            id="1-1",
            name="Testing",
        ),
        WorkItemType.model_construct(
            type="WorkItemType",
            id="1-2",
            name="Documentation",
        ),
    )


@pytest.mark.asyncio
@mock_response(url="https://server/api/tags", response_name="tags")
async def test_get_tags(client: AsyncClient) -> None:
    assert await client.get_tags() == (
        Tag.model_construct(
            type="Tag",
            id="6-0",
            name="productivity",
        ),
        Tag.model_construct(
            type="Tag",
            id="6-1",
            name="tip",
        ),
        Tag.model_construct(
            type="Tag",
            id="6-5",
            name="Star",
        ),
    )


@pytest.mark.asyncio
@mock_response(url="https://server/api/users", response_name="users")
async def test_get_users(client: AsyncClient) -> None:
    assert await client.get_users() == (
        User.model_construct(
            type="User",
            id="1-17",
            ring_id="c5d08431-dd52-4cdd-9911-7ec3a18ad117",
            login="max.demo",
            email="max@example.com",
        ),
        User.model_construct(
            type="User",
            id="1-3",
            ring_id="b0fea1e1-ed18-43f6-a99d-40044fb1dfb0",
            login="support",
            email="support@example.com",
        ),
        User.model_construct(
            type="User",
            id="1-9",
            ring_id="f19c93e1-833b-407b-a4de-7f9a3370aaf3",
            login="sam",
            email="sam@example.com",
        ),
        User.model_construct(
            type="User",
            id="1-10",
            ring_id="20e4e701-7e87-45f8-8492-c448600b7991",
            name="Worker Buddy",
            login="worker",
            email="worker@example.com",
        ),
    )


@pytest.mark.asyncio
@mock_response(url="https://server/api/issueLinkTypes", response_name="issue_link_types")
async def test_get_issue_link_types(client: AsyncClient) -> None:
    assert await client.get_issue_link_types() == (
        IssueLinkType.model_construct(
            type="IssueLinkType",
            id="106-0",
            name="Relates",
            localized_name=None,
            source_to_target="relates to",
            localized_source_to_target=None,
            target_to_source="",
            localized_target_to_source=None,
            directed=False,
            aggregation=False,
            read_only=False,
        ),
        IssueLinkType.model_construct(
            type="IssueLinkType",
            id="106-1",
            name="Depend",
            localized_name=None,
            source_to_target="is required for",
            localized_source_to_target=None,
            target_to_source="depends on",
            localized_target_to_source=None,
            directed=True,
            aggregation=False,
            read_only=False,
        ),
        IssueLinkType.model_construct(
            type="IssueLinkType",
            id="106-2",
            name="Duplicate",
            localized_name=None,
            source_to_target="is duplicated by",
            localized_source_to_target=None,
            target_to_source="duplicates",
            localized_target_to_source=None,
            directed=True,
            aggregation=True,
            read_only=True,
        ),
        IssueLinkType.model_construct(
            type="IssueLinkType",
            id="106-3",
            name="Subtask",
            localized_name=None,
            source_to_target="parent for",
            localized_source_to_target=None,
            target_to_source="subtask of",
            localized_target_to_source=None,
            directed=True,
            aggregation=True,
            read_only=True,
        ),
    )


@pytest.mark.asyncio
@mock_response(url="https://server/api/issues/1/links", response_name="issue_links")
async def test_get_issue_links(client: AsyncClient) -> None:
    assert await client.get_issue_links(issue_id="1") == (
        IssueLink.model_construct(
            id="106-0",
            direction="BOTH",
            link_type=IssueLinkType.model_construct(
                type="IssueLinkType",
                id="106-0",
                name="Relates",
                localized_name=None,
                source_to_target="relates to",
                localized_source_to_target=None,
                target_to_source="",
                localized_target_to_source=None,
                directed=False,
                aggregation=False,
                read_only=False,
            ),
            issues=[],
            trimmed_issues=[],
        ),
        IssueLink.model_construct(
            id="106-1s",
            direction="OUTWARD",
            link_type=IssueLinkType.model_construct(
                type="IssueLinkType",
                id="106-1",
                name="Depend",
                localized_name=None,
                source_to_target="is required for",
                localized_source_to_target=None,
                target_to_source="depends on",
                localized_target_to_source=None,
                directed=True,
                aggregation=False,
                read_only=False,
            ),
            issues=[],
            trimmed_issues=[],
        ),
        IssueLink.model_construct(
            id="106-1t",
            direction="INWARD",
            link_type=IssueLinkType.model_construct(
                type="IssueLinkType",
                id="106-1",
                name="Depend",
                localized_name=None,
                source_to_target="is required for",
                localized_source_to_target=None,
                target_to_source="depends on",
                localized_target_to_source=None,
                directed=True,
                aggregation=False,
                read_only=False,
            ),
            issues=[],
            trimmed_issues=[],
        ),
        IssueLink.model_construct(
            id="106-2s",
            direction="OUTWARD",
            link_type=IssueLinkType.model_construct(
                type="IssueLinkType",
                id="106-2",
                name="Duplicate",
                localized_name=None,
                source_to_target="is duplicated by",
                localized_source_to_target=None,
                target_to_source="duplicates",
                localized_target_to_source=None,
                directed=True,
                aggregation=True,
                read_only=True,
            ),
            issues=[
                Issue.model_construct(
                    type="Issue",
                    id="2-46619",
                    id_readable="PT-1839",
                    created=datetime(2022, 9, 26, 13, 50, 12, 810000, tzinfo=UTC),
                    updated=datetime(2022, 10, 5, 6, 28, 57, 291000, tzinfo=UTC),
                    resolved=datetime(2022, 9, 26, 13, 51, 29, 671000, tzinfo=UTC),
                    project=Project.model_construct(
                        type="Project",
                        id="0-4",
                        name="Test: project",
                        short_name="PT",
                    ),
                    reporter=User.model_construct(
                        type="User",
                        id="1-52",
                        name="Mary Jane",
                        ring_id="26677773-c425-4f47-b62c-dbfb2ad21e8f",
                        login="mary.jane",
                        email=None,
                    ),
                    updater=User.model_construct(
                        type="User",
                        id="1-64",
                        name="Paul Lawson",
                        ring_id="d53ece48-4c60-4b88-b93f-68392b975087",
                        login="paul.lawson",
                        email="",
                    ),
                    summary="Fintra Auftrag: 99 - Last Name, First Name",
                    description="",
                    wikified_description="",
                    comments_count=5,
                    tags=[],
                    custom_fields=[],
                ),
            ],
            trimmed_issues=[
                Issue.model_construct(
                    type="Issue",
                    id="2-46619",
                    id_readable="PT-1840",
                    created=datetime(2022, 9, 26, 13, 50, 12, 810000, tzinfo=UTC),
                    updated=datetime(2022, 10, 5, 6, 28, 57, 291000, tzinfo=UTC),
                    resolved=datetime(2022, 9, 26, 13, 51, 29, 671000, tzinfo=UTC),
                    project=Project.model_construct(
                        type="Project",
                        id="0-4",
                        name="Test: project",
                        short_name="PT",
                    ),
                    reporter=User.model_construct(
                        type="User",
                        id="1-52",
                        name="Mary Jane",
                        ring_id="26677773-c425-4f47-b62c-dbfb2ad21e8f",
                        login="mary.jane",
                        email=None,
                    ),
                    updater=User.model_construct(
                        type="User",
                        id="1-64",
                        name="Paul Lawson",
                        ring_id="d53ece48-4c60-4b88-b93f-68392b975087",
                        login="paul.lawson",
                        email="",
                    ),
                    summary="Fintra Auftrag: 99 - Last Name, First Name",
                    description="",
                    wikified_description="",
                    comments_count=0,
                    tags=[],
                    custom_fields=[],
                ),
            ],
        ),
        IssueLink.model_construct(
            id="106-2t",
            direction="INWARD",
            link_type=IssueLinkType.model_construct(
                type="IssueLinkType",
                id="106-2",
                name="Duplicate",
                localized_name=None,
                source_to_target="is duplicated by",
                localized_source_to_target=None,
                target_to_source="duplicates",
                localized_target_to_source=None,
                directed=True,
                aggregation=True,
                read_only=True,
            ),
            issues=[],
            trimmed_issues=[],
        ),
        IssueLink.model_construct(
            id="106-3s",
            direction="OUTWARD",
            link_type=IssueLinkType.model_construct(
                type="IssueLinkType",
                id="106-3",
                name="Subtask",
                localized_name=None,
                source_to_target="parent for",
                localized_source_to_target=None,
                target_to_source="subtask of",
                localized_target_to_source=None,
                directed=True,
                aggregation=True,
                read_only=True,
            ),
            issues=[],
            trimmed_issues=[],
        ),
        IssueLink.model_construct(
            id="106-3t",
            direction="INWARD",
            link_type=IssueLinkType.model_construct(
                type="IssueLinkType",
                id="106-3",
                name="Subtask",
                localized_name=None,
                source_to_target="parent for",
                localized_source_to_target=None,
                target_to_source="subtask of",
                localized_target_to_source=None,
                directed=True,
                aggregation=True,
                read_only=True,
            ),
            issues=[],
            trimmed_issues=[],
        ),
    )


@pytest.mark.asyncio
@mock_response(url="https://server/api/issues/1", response_name="issue", method=HTTPMethod.POST)
async def test_update_issue(client: AsyncClient) -> None:
    assert await client.update_issue(issue_id="1", issue=TEST_ISSUE) == TEST_ISSUE


@pytest.mark.asyncio
@mock_response(url="https://server/api/agiles", response_name="agiles", method=HTTPMethod.GET)
async def test_get_agiles(client: AsyncClient) -> None:
    assert await client.get_agiles() == (
        Agile.model_construct(
            type="Agile",
            id="120-0",
            name="Demo Board",
            owner=User.model_construct(
                type="User",
                id="1-17",
                name="Max Demo",
                ring_id="c5d08431-dd52-4cdd-9911-7ec3a18ad117",
                login="max.demo",
                email="max@example.com",
            ),
            visible_for=None,
            projects=[
                Project.model_construct(
                    type="Project",
                    id="0-0",
                    name="Demo project",
                    short_name="DEMO",
                ),
            ],
            sprints=[
                SprintRef.model_construct(
                    type="Sprint",
                    id="121-12",
                    name="First sprint",
                ),
            ],
            current_sprint=SprintRef.model_construct(
                type="Sprint",
                id="121-12",
                name="First sprint",
            ),
        ),
        TEST_AGILE,
    )


@pytest.mark.asyncio
@mock_response(url="https://server/api/agiles/120-8", response_name="agile", method=HTTPMethod.GET)
async def test_get_agile(client: AsyncClient) -> None:
    assert await client.get_agile(agile_id="120-8") == TEST_AGILE


@pytest.mark.asyncio
@mock_response(url="https://server/api/agiles/120-8/sprints", response_name="sprints", method=HTTPMethod.GET)
async def test_get_sprints(client: AsyncClient) -> None:
    assert await client.get_sprints(agile_id="120-8") == (
        TEST_SPRINT,
        Sprint.model_construct(
            type="Sprint",
            id="121-11",
            name="Week 2",
            goal="Finish everything",
            start=datetime(2023, 2, 5, 0, 0, tzinfo=UTC),
            finish=datetime(2023, 2, 18, 23, 59, 59, 999000, tzinfo=UTC),
            archived=False,
            is_default=False,
            unresolved_issues_count=0,
            agile=AgileRef.model_construct(
                type="Agile",
                id="120-8",
                name="Kanban",
            ),
            issues=[TEST_ISSUE],
            previous_sprint=None,
        ),
    )


@pytest.mark.asyncio
@mock_response(url="https://server/api/agiles/120-8/sprints/121-8", response_name="sprint", method=HTTPMethod.GET)
async def test_get_sprint(client: AsyncClient) -> None:
    assert await client.get_sprint(agile_id="120-8", sprint_id="121-8") == TEST_SPRINT


@pytest.mark.asyncio
async def test_context_manager() -> None:
    """Test that AsyncClient can be used as an async context manager."""
    async with AsyncClient(base_url="https://server", token="test") as client:  # noqa: S106
        assert isinstance(client, AsyncClient)


@pytest.mark.asyncio
async def test_async_context_manager_cleanup() -> None:
    """Test that the async context manager properly closes the client."""
    client: Final = AsyncClient(base_url="https://server", token="test")  # noqa: S106
    async with client:
        assert not client._client.is_closed  # type: ignore[reportPrivateUsage]
    assert client._client.is_closed  # type: ignore[reportPrivateUsage]


@pytest.mark.asyncio
async def test_external_httpx_async_client() -> None:
    """Test that AsyncClient can use an external httpx.AsyncClient instance."""
    mock_client: Final = AsyncMock(spec=httpx.AsyncClient)
    mock_client.headers = {}
    mock_client.timeout = None  # Initialize timeout attribute

    client: Final = AsyncClient(base_url="https://server", token="test", client=mock_client)  # noqa: S106

    # Verify the external client was used
    assert client._client is mock_client  # type: ignore[reportPrivateUsage]
    # Verify headers were set
    assert "Authorization" in mock_client.headers
    assert mock_client.headers["Authorization"] == "Bearer test"


@pytest.mark.asyncio
@respx.mock
async def test_not_found_error(client: AsyncClient) -> None:
    """Test that a 404 NOT_FOUND response raises YouTrackNotFound."""
    respx.get("https://server/api/issues/INVALID-123").mock(return_value=httpx.Response(404))

    with pytest.raises(YouTrackNotFound):
        await client.get_issue(issue_id="INVALID-123")


@pytest.mark.asyncio
@respx.mock
async def test_unauthorized_error(client: AsyncClient) -> None:
    """Test that a 401 UNAUTHORIZED response raises YouTrackUnauthorized."""
    respx.get("https://server/api/issues/DEMO-1").mock(return_value=httpx.Response(401))

    with pytest.raises(YouTrackUnauthorized):
        await client.get_issue(issue_id="DEMO-1")


@pytest.mark.asyncio
@respx.mock
async def test_get_bytes_empty_response_error(client: AsyncClient) -> None:
    """Test that _get_bytes raises YouTrackException when response is empty."""
    # Mock a GET request that returns 204 No Content (empty response)
    respx.get("https://server/api/issues/DEMO-1").mock(return_value=httpx.Response(204))

    with pytest.raises(YouTrackException, match="Unexpected empty response from GET"):
        await client.get_issue(issue_id="DEMO-1")


@pytest.mark.asyncio
@respx.mock
async def test_post_bytes_empty_response_error(client: AsyncClient) -> None:
    """Test that _post_bytes raises YouTrackException when response is empty."""
    # Mock a POST request that returns 204 No Content (empty response)
    respx.post("https://server/api/issues").mock(return_value=httpx.Response(204))

    with pytest.raises(YouTrackException, match="Unexpected empty response from POST"):
        await client.create_issue(issue=TEST_ISSUE)


@pytest.mark.asyncio
@respx.mock
async def test_unexpected_status_code_error(client: AsyncClient) -> None:
    """Test that unexpected status codes raise YouTrackException."""
    # Mock a request that returns an unexpected error status code (e.g., 500)
    respx.get("https://server/api/issues/DEMO-1").mock(return_value=httpx.Response(500))

    with pytest.raises(YouTrackException, match="Unexpected status code for GET"):
        await client.get_issue(issue_id="DEMO-1")


@pytest.mark.asyncio
@respx.mock
async def test_delete_issue(client: AsyncClient) -> None:
    """Test deleting an issue."""
    respx.delete("https://server/api/issues/DEMO-1").mock(return_value=httpx.Response(200))

    # delete_issue returns None on success
    result: Final = await client.delete_issue(issue_id="DEMO-1")
    assert result is None


@pytest.mark.asyncio
@respx.mock
async def test_add_comment_to_issue(client: AsyncClient) -> None:
    """Test adding a comment to an issue."""
    comment: Final = IssueComment(text="Test comment")
    mock_response: Final = '{"id": "1-1", "type": "IssueComment", "text": "Test comment", "deleted": false}'
    respx.post("https://server/api/issues/DEMO-1/comments").mock(
        return_value=httpx.Response(200, content=mock_response)
    )

    result: Final = await client.create_issue_comment(issue_id="DEMO-1", comment=comment)
    assert result.text == "Test comment"
    assert result.id == "1-1"


@pytest.mark.asyncio
@respx.mock
async def test_delete_issue_comment(client: AsyncClient) -> None:
    """Test deleting an issue comment."""
    respx.delete("https://server/api/issues/DEMO-1/comments/1-1").mock(return_value=httpx.Response(200))

    result: Final = await client.delete_issue_comment(issue_id="DEMO-1", comment_id="1-1")
    assert result is None


@pytest.mark.asyncio
async def test_client_with_timeout_spec() -> None:
    """Test that TimeoutSpec is properly converted to httpx.Timeout."""
    timeout_spec: Final = TimeoutSpec(connect_timeout=5.0, read_timeout=30.0)

    # Test the _to_httpx_timeout conversion directly
    result: Final = BaseClient._to_httpx_timeout(timeout_spec)  # type: ignore[reportPrivateUsage]

    # Verify it returns an httpx.Timeout object
    assert isinstance(result, httpx.Timeout)
    assert result.connect == 5.0
    assert result.read == 30.0
