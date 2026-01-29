from collections.abc import Sequence
from http import HTTPMethod
from http import HTTPStatus
from types import TracebackType
from typing import IO
from typing import Final
from typing import Optional
from typing import final

import httpx
from pydantic import BaseModel
from pydantic import TypeAdapter

from youtrack_sdk.base_client import BaseClient
from youtrack_sdk.entities import Agile
from youtrack_sdk.entities import Issue
from youtrack_sdk.entities import IssueAttachment
from youtrack_sdk.entities import IssueComment
from youtrack_sdk.entities import IssueCustomFieldType
from youtrack_sdk.entities import IssueLink
from youtrack_sdk.entities import IssueLinkType
from youtrack_sdk.entities import IssueWorkItem
from youtrack_sdk.entities import Project
from youtrack_sdk.entities import ProjectCustomFieldType
from youtrack_sdk.entities import Sprint
from youtrack_sdk.entities import Tag
from youtrack_sdk.entities import User
from youtrack_sdk.entities import WorkItemType
from youtrack_sdk.exceptions import YouTrackException
from youtrack_sdk.exceptions import YouTrackNotFound
from youtrack_sdk.exceptions import YouTrackUnauthorized
from youtrack_sdk.helpers import model_to_field_names
from youtrack_sdk.helpers import obj_to_json
from youtrack_sdk.types import IssueLinkDirection
from youtrack_sdk.types import TimeoutSpec


@final
class AsyncClient(BaseClient):
    def __init__(
        self,
        *,
        base_url: str,
        token: str,
        timeout: Optional[int | float | TimeoutSpec] = None,
        client: Optional[httpx.AsyncClient] = None,
    ) -> None:
        """
        :param base_url: YouTrack instance URL (e.g. https://example.com/youtrack)
        :param token: Permanent YouTrack token
        :param timeout: (optional) How long to wait for the server to send data before giving up,
            as a float or int, or timeout spec
        :param client: (optional) Custom httpx.AsyncClient instance to use for requests
        """
        super().__init__(base_url=base_url, timeout=timeout)
        httpx_timeout: Final = BaseClient._to_httpx_timeout(timeout)

        if client is not None:
            client.headers.update(BaseClient._get_headers(token))
            client.timeout = httpx_timeout

        self._client: Final = (
            httpx.AsyncClient(
                headers=BaseClient._get_headers(token),
                timeout=httpx_timeout,
            )
            if client is None
            else client
        )

    async def _send_request(
        self,
        *,
        method: HTTPMethod,
        url: str,
        data: Optional[BaseModel] = None,
        files: Optional[dict[str, IO[bytes]]] = None,
    ) -> Optional[bytes]:
        headers: Final = {} if data is None else {"Content-Type": "application/json"}
        response: Final = await self._client.request(
            method=method,
            url=url,
            content=data and obj_to_json(data),
            files=files,
            headers=headers,
        )

        match response.status_code:
            case HTTPStatus.NOT_FOUND:
                raise YouTrackNotFound
            case HTTPStatus.UNAUTHORIZED:
                raise YouTrackUnauthorized
            case _:
                try:
                    response.raise_for_status()
                except httpx.HTTPStatusError as e:
                    msg: Final = f"Unexpected status code for {method} {url}: {response.status_code}."
                    raise YouTrackException(msg) from e

        # Avoid `JSONDecodeError` if status code was 2xx, but the response content is empty.
        # Some API endpoints return empty, non-JSON responses on success.
        if not response.content:
            return None

        return response.content

    async def _get_bytes(self, *, url: str) -> bytes:
        """Get request that raises if response is None."""
        response: Final = await self._send_request(method=HTTPMethod.GET, url=url)
        if response is None:
            msg: Final = f"Unexpected empty response from GET {url}"
            raise YouTrackException(msg)
        return response

    async def _post_bytes(
        self,
        *,
        url: str,
        data: Optional[BaseModel] = None,
        files: Optional[dict[str, IO[bytes]]] = None,
    ) -> bytes:
        """Post request that raises if response is `None`."""
        response: Final = await self._send_request(
            method=HTTPMethod.POST,
            url=url,
            data=data,
            files=files,
        )
        if response is None:
            msg: Final = f"Unexpected empty response from POST {url}"
            raise YouTrackException(msg)
        return response

    async def _get(self, *, url: str) -> Optional[bytes]:
        return await self._send_request(method=HTTPMethod.GET, url=url)

    async def _post(
        self,
        *,
        url: str,
        data: Optional[BaseModel] = None,
        files: Optional[dict[str, IO[bytes]]] = None,
    ) -> Optional[bytes]:
        return await self._send_request(
            method=HTTPMethod.POST,
            url=url,
            data=data,
            files=files,
        )

    async def _delete(self, *, url: str) -> Optional[bytes]:
        return await self._send_request(method=HTTPMethod.DELETE, url=url)

    async def get_issue(self, *, issue_id: str) -> Issue:
        """Read an issue with specific ID.

        https://www.jetbrains.com/help/youtrack/devportal/operations-api-issues.html#get-Issue-method
        """
        return Issue.model_validate_json(
            await self._get_bytes(
                url=self._build_url(
                    path=f"/issues/{issue_id}",
                    fields=model_to_field_names(Issue),
                ),
            ),
        )

    async def get_issues[T](
        self,
        *,
        model: type[T] = Issue,
        query: Optional[str] = None,
        custom_fields: Sequence[str] = (),
        offset: int = 0,
        count: int = -1,
    ) -> Sequence[T]:
        """Get all issues that match the specified query.
        If you don't provide the query parameter, the server returns all issues.

        https://www.jetbrains.com/help/youtrack/devportal/resource-api-issues.html#get_all-Issue-method
        """
        return TypeAdapter(tuple[model, ...]).validate_json(
            await self._get_bytes(
                url=self._build_url(
                    path="/issues/",
                    fields=model_to_field_names(model),
                    query=query,
                    customFields=custom_fields,
                    offset=offset,
                    count=count,
                ),
            ),
        )

    async def create_issue(self, *, issue: Issue) -> Issue:
        """Create new issue.

        https://www.jetbrains.com/help/youtrack/devportal/resource-api-issues.html#create-Issue-method
        """
        return Issue.model_validate_json(
            await self._post_bytes(
                url=self._build_url(
                    path="/issues",
                    fields=model_to_field_names(Issue),
                ),
                data=issue,
            ),
        )

    async def update_issue(
        self,
        *,
        issue_id: str,
        issue: Issue,
        mute_update_notifications: bool = False,
    ) -> Issue:
        """Update an existing issue.

        https://www.jetbrains.com/help/youtrack/devportal/operations-api-issues.html#update-Issue-method
        """
        return Issue.model_validate_json(
            await self._post_bytes(
                url=self._build_url(
                    path=f"/issues/{issue_id}",
                    fields=model_to_field_names(Issue),
                    muteUpdateNotifications=mute_update_notifications,
                ),
                data=issue,
            ),
        )

    async def get_issue_custom_fields(
        self,
        *,
        issue_id: str,
        offset: int = 0,
        count: int = -1,
    ) -> Sequence[IssueCustomFieldType]:
        """Get the list of available custom fields of the issue.

        https://www.jetbrains.com/help/youtrack/devportal/resource-api-issues-issueID-customFields.html#get_all-IssueCustomField-method
        """
        return TypeAdapter(tuple[IssueCustomFieldType, ...]).validate_json(
            await self._get_bytes(
                url=self._build_url(
                    path=f"/issues/{issue_id}/customFields",
                    fields=model_to_field_names(IssueCustomFieldType),
                    offset=offset,
                    count=count,
                ),
            ),
        )

    async def update_issue_custom_field(
        self,
        *,
        issue_id: str,
        field: IssueCustomFieldType,
        mute_update_notifications: bool = False,
    ) -> IssueCustomFieldType:
        """Update specific custom field in the issue.

        https://www.jetbrains.com/help/youtrack/devportal/operations-api-issues-issueID-customFields.html#update-IssueCustomField-method
        """
        return TypeAdapter(IssueCustomFieldType).validate_json(  # type: ignore[return-value]
            await self._post_bytes(
                url=self._build_url(
                    path=f"/issues/{issue_id}/customFields/{field.id}",
                    fields=model_to_field_names(IssueCustomFieldType),
                    muteUpdateNotifications=mute_update_notifications,
                ),
                data=field,
            ),
        )

    async def get_project_custom_fields(
        self,
        *,
        project_id: str,
        offset: int = 0,
        count: int = -1,
    ) -> Sequence[ProjectCustomFieldType]:
        """Get the list of custom fields that are attached to a specific project.

        https://www.jetbrains.com/help/youtrack/devportal/resource-api-admin-projects-projectID-customFields.html#get_all-ProjectCustomField-method
        """
        return TypeAdapter(tuple[ProjectCustomFieldType, ...]).validate_json(
            await self._get_bytes(
                url=self._build_url(
                    path=f"/admin/projects/{project_id}/customFields",
                    fields=f"{model_to_field_names(ProjectCustomFieldType)},field(name,fieldType(id)),bundle(values(id,name))",
                    **{"$skip": offset, "$top": count if count != -1 else None},
                ),
            ),
        )

    async def delete_issue(self, *, issue_id: str) -> None:
        """Delete the issue.

        https://www.jetbrains.com/help/youtrack/devportal/operations-api-issues.html#delete-Issue-method
        """
        await self._delete(url=self._build_url(path=f"/issues/{issue_id}"))

    async def get_issue_comments(
        self,
        *,
        issue_id: str,
        offset: int = 0,
        count: int = -1,
    ) -> Sequence[IssueComment]:
        """Get all accessible comments of the specific issue.

        https://www.jetbrains.com/help/youtrack/devportal/resource-api-issues-issueID-comments.html#get_all-IssueComment-method
        """
        return TypeAdapter(tuple[IssueComment, ...]).validate_json(
            await self._get_bytes(
                url=self._build_url(
                    path=f"/issues/{issue_id}/comments",
                    fields=model_to_field_names(IssueComment),
                    offset=offset,
                    count=count,
                ),
            ),
        )

    async def create_issue_comment(
        self,
        *,
        issue_id: str,
        comment: IssueComment,
    ) -> IssueComment:
        """Add a new comment to an issue with a specific ID.

        https://www.jetbrains.com/help/youtrack/devportal/resource-api-issues-issueID-comments.html#create-IssueComment-method
        """
        return IssueComment.model_validate_json(
            await self._post_bytes(
                url=self._build_url(
                    path=f"/issues/{issue_id}/comments",
                    fields=model_to_field_names(IssueComment),
                ),
                data=comment,
            ),
        )

    async def update_issue_comment(
        self,
        *,
        issue_id: str,
        comment: IssueComment,
        mute_update_notifications: bool = False,
    ) -> IssueComment:
        """Update an existing comment of the specific issue.

        https://www.jetbrains.com/help/youtrack/devportal/operations-api-issues-issueID-comments.html#update-IssueComment-method
        """
        return IssueComment.model_validate_json(
            await self._post_bytes(
                url=self._build_url(
                    path=f"/issues/{issue_id}/comments/{comment.id}",
                    fields=model_to_field_names(IssueComment),
                    muteUpdateNotifications=mute_update_notifications,
                ),
                data=comment,
            ),
        )

    async def hide_issue_comment(self, *, issue_id: str, comment_id: str) -> None:
        """Hide a specific issue comment.

        https://www.jetbrains.com/help/youtrack/devportal/operations-api-issues-issueID-comments.html#update-IssueComment-method
        """
        await self.update_issue_comment(
            issue_id=issue_id,
            comment=(IssueComment(id=comment_id, deleted=True)),
        )

    async def delete_issue_comment(self, *, issue_id: str, comment_id: str) -> None:
        """Delete a specific issue comment.

        https://www.jetbrains.com/help/youtrack/devportal/operations-api-issues-issueID-comments.html#delete-IssueComment-method
        """
        await self._delete(
            url=self._build_url(path=f"/issues/{issue_id}/comments/{comment_id}"),
        )

    async def get_issue_attachments(
        self,
        *,
        issue_id: str,
        offset: int = 0,
        count: int = -1,
    ) -> Sequence[IssueAttachment]:
        """Get a list of all attachments of the specific issue.

        https://www.jetbrains.com/help/youtrack/devportal/resource-api-issues-issueID-attachments.html#get_all-IssueAttachment-method
        """
        return TypeAdapter(tuple[IssueAttachment, ...]).validate_json(
            await self._get_bytes(
                url=self._build_url(
                    path=f"/issues/{issue_id}/attachments",
                    fields=model_to_field_names(IssueAttachment),
                    offset=offset,
                    count=count,
                ),
            ),
        )

    async def create_issue_attachments(
        self,
        *,
        issue_id: str,
        files: dict[str, IO[bytes]],
    ) -> Sequence[IssueAttachment]:
        """Add an attachment to the issue.

        https://www.jetbrains.com/help/youtrack/devportal/resource-api-issues-issueID-attachments.html#create-IssueAttachment-method
        https://www.jetbrains.com/help/youtrack/devportal/api-usecase-attach-files.html
        """
        return TypeAdapter(tuple[IssueAttachment, ...]).validate_json(
            await self._post_bytes(
                url=self._build_url(
                    path=f"/issues/{issue_id}/attachments",
                    fields=model_to_field_names(IssueAttachment),
                ),
                files=files,
            ),
        )

    async def create_comment_attachments(
        self,
        *,
        issue_id: str,
        comment_id: str,
        files: dict[str, IO[bytes]],
    ) -> Sequence[IssueAttachment]:
        return TypeAdapter(tuple[IssueAttachment, ...]).validate_json(
            await self._post_bytes(
                url=self._build_url(
                    path=f"/issues/{issue_id}/comments/{comment_id}/attachments",
                    fields=model_to_field_names(IssueAttachment),
                ),
                files=files,
            ),
        )

    async def get_issue_work_items(self, *, issue_id: str, offset: int = 0, count: int = -1) -> Sequence[IssueWorkItem]:
        """Get the list of all work items of the specific issue.

        https://www.jetbrains.com/help/youtrack/devportal/resource-api-issues-issueID-timeTracking-workItems.html#get_all-IssueWorkItem-method
        """
        return TypeAdapter(tuple[IssueWorkItem, ...]).validate_json(
            await self._get_bytes(
                url=self._build_url(
                    path=f"/issues/{issue_id}/timeTracking/workItems",
                    fields=model_to_field_names(IssueWorkItem),
                    offset=offset,
                    count=count,
                ),
            ),
        )

    async def create_issue_work_item(self, *, issue_id: str, issue_work_item: IssueWorkItem) -> IssueWorkItem:
        """Add a new work item to the issue.

        https://www.jetbrains.com/help/youtrack/devportal/resource-api-issues-issueID-timeTracking-workItems.html#create-IssueWorkItem-method
        """
        return IssueWorkItem.model_validate_json(
            await self._post_bytes(
                url=self._build_url(
                    path=f"/issues/{issue_id}/timeTracking/workItems",
                    fields=model_to_field_names(IssueWorkItem),
                ),
                data=issue_work_item,
            ),
        )

    async def get_projects(self, offset: int = 0, count: int = -1) -> Sequence[Project]:
        """Get a list of all available projects in the system.

        https://www.jetbrains.com/help/youtrack/devportal/resource-api-admin-projects.html#get_all-Project-method
        """
        return TypeAdapter(tuple[Project, ...]).validate_json(
            await self._get_bytes(
                url=self._build_url(
                    path="/admin/projects",
                    fields=model_to_field_names(Project),
                    offset=offset,
                    count=count,
                ),
            ),
        )

    async def get_project_work_item_types(
        self,
        *,
        project_id: str,
        offset: int = 0,
        count: int = -1,
    ) -> Sequence[WorkItemType]:
        """Get the list of all work item types that are used in the project.

        https://www.jetbrains.com/help/youtrack/devportal/resource-api-admin-projects-projectID-timeTrackingSettings-workItemTypes.html#get_all-WorkItemType-method
        """
        return TypeAdapter(tuple[WorkItemType, ...]).validate_json(
            await self._get_bytes(
                url=self._build_url(
                    path=f"/admin/projects/{project_id}/timeTrackingSettings/workItemTypes",
                    fields=model_to_field_names(WorkItemType),
                    offset=offset,
                    count=count,
                ),
            ),
        )

    async def get_tags(self, offset: int = 0, count: int = -1) -> Sequence[Tag]:
        """Get all tags that are visible to the current user.

        https://www.jetbrains.com/help/youtrack/devportal/resource-api-tags.html#get_all-Tag-method
        """
        return TypeAdapter(tuple[Tag, ...]).validate_json(
            await self._get_bytes(
                url=self._build_url(
                    path="/tags",
                    fields=model_to_field_names(Tag),
                    offset=offset,
                    count=count,
                ),
            ),
        )

    async def add_issue_tag(self, *, issue_id: str, tag: Tag) -> None:
        """Tag the issue with an existing tag.

        https://www.jetbrains.com/help/youtrack/devportal/resource-api-issues-issueID-tags.html#create-Tag-method
        """
        await self._post(
            url=self._build_url(path=f"/issues/{issue_id}/tags"),
            data=tag,
        )

    async def get_users(self, offset: int = 0, count: int = -1) -> Sequence[User]:
        """Read the list of users in YouTrack.

        https://www.jetbrains.com/help/youtrack/devportal/resource-api-users.html#get_all-User-method
        """
        return TypeAdapter(tuple[User, ...]).validate_json(
            await self._get_bytes(
                url=self._build_url(
                    path="/users",
                    fields=model_to_field_names(User),
                    offset=offset,
                    count=count,
                ),
            ),
        )

    async def get_issue_links(
        self,
        issue_id: str,
        offset: int = 0,
        count: int = -1,
    ) -> Sequence[IssueLink]:
        """Read the list of links for the issue in YouTrack.

        https://www.jetbrains.com/help/youtrack/devportal/resource-api-issues-issueID-links.html#get_all-IssueLink-method
        """
        return TypeAdapter(tuple[IssueLink, ...]).validate_json(
            await self._get_bytes(
                url=self._build_url(
                    path=f"/issues/{issue_id}/links",
                    fields=model_to_field_names(IssueLink),
                    offset=offset,
                    count=count,
                ),
            ),
        )

    async def get_issue_link_types(
        self,
        offset: int = 0,
        count: int = -1,
    ) -> Sequence[IssueLinkType]:
        """Read the list of all available link types in in YouTrack.

        https://www.jetbrains.com/help/youtrack/devportal/resource-api-issueLinkTypes.html#get_all-IssueLinkType-method
        """
        return TypeAdapter(tuple[IssueLinkType, ...]).validate_json(
            await self._get_bytes(
                url=self._build_url(
                    path="/issueLinkTypes",
                    fields=model_to_field_names(IssueLinkType),
                    offset=offset,
                    count=count,
                ),
            ),
        )

    async def link_issues(
        self,
        *,
        source_issue_id: str,
        target_issue_id: str,
        link_type_id: str,
        link_direction: IssueLinkDirection,
    ) -> Issue:
        """Link an issue to another issue

        https://www.jetbrains.com/help/youtrack/devportal/resource-api-issues-issueID-links-linkID-issues.html#create-Issue-method
        """
        return TypeAdapter(Issue).validate_json(
            await self._post_bytes(
                url=self._build_url(
                    path=f"/issues/{source_issue_id}/links/{link_type_id}{link_direction.value}/issues",
                    fields=model_to_field_names(Issue),
                ),
                data=Issue(id=target_issue_id),
            ),
        )

    async def delete_issue_link(
        self,
        *,
        source_issue_id: str,
        target_issue_id: str,
        link_type_id: str,
    ) -> None:
        """Delete the link between issues.

        https://www.jetbrains.com/help/youtrack/devportal/operations-api-issues-issueID-links-linkID-issues.html#delete-Issue-method
        """
        await self._delete(
            url=self._build_url(path=f"/issues/{source_issue_id}/links/{link_type_id}/issues/{target_issue_id}"),
        )

    async def get_agiles(self, *, offset: int = 0, count: int = -1) -> Sequence[Agile]:
        """Get the list of all available agile boards in the system.

        https://www.jetbrains.com/help/youtrack/devportal/resource-api-agiles.html#get_all-Agile-method
        """
        return TypeAdapter(tuple[Agile, ...]).validate_json(
            await self._get_bytes(
                url=self._build_url(
                    path="/agiles",
                    fields=model_to_field_names(Agile),
                    offset=offset,
                    count=count,
                ),
            ),
        )

    async def get_agile(self, *, agile_id: str) -> Agile:
        """Get settings of the specific agile board.

        https://www.jetbrains.com/help/youtrack/devportal/operations-api-agiles.html#get-Agile-method
        """
        return Agile.model_validate_json(
            await self._get_bytes(
                url=self._build_url(
                    path=f"/agiles/{agile_id}",
                    fields=model_to_field_names(Agile),
                ),
            ),
        )

    async def get_sprints(
        self,
        *,
        agile_id: str,
        offset: int = 0,
        count: int = -1,
    ) -> Sequence[Sprint]:
        """Get the list of all sprints of the agile board.

        https://www.jetbrains.com/help/youtrack/devportal/resource-api-agiles-agileID-sprints.html#get_all-Sprint-method
        """
        return TypeAdapter(tuple[Sprint, ...]).validate_json(
            await self._get_bytes(
                url=self._build_url(
                    path=f"/agiles/{agile_id}/sprints",
                    fields=model_to_field_names(Sprint),
                    offset=offset,
                    count=count,
                ),
            ),
        )

    async def get_sprint(self, *, agile_id: str, sprint_id: str) -> Sprint:
        """Get settings of the specific sprint of the agile board.

        https://www.jetbrains.com/help/youtrack/devportal/operations-api-agiles-agileID-sprints.html#get-Sprint-method
        """
        return Sprint.model_validate_json(
            await self._get_bytes(
                url=self._build_url(
                    path=f"/agiles/{agile_id}/sprints/{sprint_id}",
                    fields=model_to_field_names(Sprint),
                ),
            ),
        )

    async def __aenter__(self) -> "AsyncClient":
        await self._client.__aenter__()
        return self

    async def __aexit__(
        self,
        exception_type: Optional[type[BaseException]] = None,
        exception_value: Optional[BaseException] = None,
        traceback: Optional[TracebackType] = None,
    ) -> None:
        await self._client.__aexit__(exception_type, exception_value, traceback)
