from collections.abc import Sequence
from enum import StrEnum
from typing import Annotated
from typing import Literal
from typing import Optional
from typing import final

from pydantic import AwareDatetime
from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import Field
from pydantic import StrictFloat
from pydantic import StrictInt
from pydantic import StrictStr

from youtrack_sdk.types import YouTrackDate
from youtrack_sdk.types import YouTrackDateTime


@final
class UserTypeName(StrEnum):
    USER = "User"
    ME = "Me"


@final
class User(BaseModel):
    model_config = ConfigDict(populate_by_name=True, frozen=True)

    type: Literal[UserTypeName.USER, UserTypeName.ME] = Field(alias="$type", default=UserTypeName.USER)
    id: Optional[str] = None
    name: Optional[str] = None
    ring_id: Optional[str] = Field(alias="ringId", default=None)
    login: Optional[str] = None
    email: Optional[str] = None


@final
class TextFieldValueTypeName(StrEnum):
    TEXT_FIELD_VALUE = "TextFieldValue"


@final
class TextFieldValue(BaseModel):
    model_config = ConfigDict(populate_by_name=True, frozen=True)

    type: Literal[TextFieldValueTypeName.TEXT_FIELD_VALUE] = Field(
        alias="$type",
        default=TextFieldValueTypeName.TEXT_FIELD_VALUE,
    )
    id: Optional[str] = None
    text: Optional[str] = None
    markdownText: Optional[str] = None


@final
class PeriodValueTypeName(StrEnum):
    PERIOD_VALUE = "PeriodValue"


@final
class PeriodValue(BaseModel):
    model_config = ConfigDict(populate_by_name=True, frozen=True)

    type: Literal[PeriodValueTypeName.PERIOD_VALUE] = Field(alias="$type", default=PeriodValueTypeName.PERIOD_VALUE)
    id: Optional[str] = None
    minutes: Optional[int] = None
    presentation: Optional[str] = None


@final
class DurationValueTypeName(StrEnum):
    DURATION_VALUE = "DurationValue"


@final
class DurationValue(BaseModel):
    model_config = ConfigDict(populate_by_name=True, frozen=True)

    type: Literal[DurationValueTypeName.DURATION_VALUE] = Field(
        alias="$type",
        default=DurationValueTypeName.DURATION_VALUE,
    )
    id: Optional[str] = None
    minutes: Optional[int] = None
    presentation: Optional[str] = None


@final
class BundleElementTypeName(StrEnum):
    BUILD = "BuildBundleElement"
    VERSION = "VersionBundleElement"
    OWNED = "OwnedBundleElement"
    ENUM = "EnumBundleElement"
    STATE = "StateBundleElement"


@final
class BuildBundleElement(BaseModel):
    model_config = ConfigDict(populate_by_name=True, frozen=True)

    type: Literal[BundleElementTypeName.BUILD] = Field(alias="$type", default=BundleElementTypeName.BUILD)
    id: Optional[str] = None
    name: Optional[str] = None


@final
class VersionBundleElement(BaseModel):
    model_config = ConfigDict(populate_by_name=True, frozen=True)

    type: Literal[BundleElementTypeName.VERSION] = Field(alias="$type", default=BundleElementTypeName.VERSION)
    id: Optional[str] = None
    name: Optional[str] = None


@final
class OwnedBundleElement(BaseModel):
    model_config = ConfigDict(populate_by_name=True, frozen=True)

    type: Literal[BundleElementTypeName.OWNED] = Field(alias="$type", default=BundleElementTypeName.OWNED)
    id: Optional[str] = None
    name: Optional[str] = None


@final
class EnumBundleElement(BaseModel):
    model_config = ConfigDict(populate_by_name=True, frozen=True)

    type: Literal[BundleElementTypeName.ENUM] = Field(alias="$type", default=BundleElementTypeName.ENUM)
    id: Optional[str] = None
    name: Optional[str] = None


@final
class StateBundleElement(BaseModel):
    model_config = ConfigDict(populate_by_name=True, frozen=True)

    type: Literal[BundleElementTypeName.STATE] = Field(alias="$type", default=BundleElementTypeName.STATE)
    id: Optional[str] = None
    name: Optional[str] = None


BundleElement = Annotated[
    BuildBundleElement | VersionBundleElement | OwnedBundleElement | EnumBundleElement | StateBundleElement,
    Field(discriminator="type"),
]


@final
class UserGroupTypeName(StrEnum):
    USER_GROUP = "UserGroup"


@final
class UserGroup(BaseModel):
    model_config = ConfigDict(populate_by_name=True, frozen=True)

    type: Literal[UserGroupTypeName.USER_GROUP] = Field(alias="$type", default=UserGroupTypeName.USER_GROUP)
    id: Optional[str] = None
    name: Optional[str] = None
    ring_id: Optional[str] = Field(alias="ringId", default=None)


@final
class FieldTypeTypeName(StrEnum):
    FIELD_TYPE = "FieldType"


@final
class FieldType(BaseModel):
    model_config = ConfigDict(populate_by_name=True, frozen=True)

    type: Literal[FieldTypeTypeName.FIELD_TYPE] = Field(alias="$type", default=FieldTypeTypeName.FIELD_TYPE)
    id: Optional[str] = None


@final
class CustomFieldTypeName(StrEnum):
    CUSTOM_FIELD = "CustomField"


@final
class CustomField(BaseModel):
    model_config = ConfigDict(populate_by_name=True, frozen=True)

    type: Literal[CustomFieldTypeName.CUSTOM_FIELD] = Field(alias="$type", default=CustomFieldTypeName.CUSTOM_FIELD)
    field_type: Optional[FieldType] = Field(alias="fieldType", default=None)


@final
class ProjectCustomFieldTypeName(StrEnum):
    GROUP = "GroupProjectCustomField"
    BUNDLE = "BundleProjectCustomField"
    BUILD = "BuildProjectCustomField"
    ENUM = "EnumProjectCustomField"
    OWNED = "OwnedProjectCustomField"
    STATE = "StateProjectCustomField"
    USER = "UserProjectCustomField"
    VERSION = "VersionProjectCustomField"
    SIMPLE = "SimpleProjectCustomField"
    TEXT = "TextProjectCustomField"
    PERIOD = "PeriodProjectCustomField"


class ProjectCustomField(BaseModel):
    model_config = ConfigDict(populate_by_name=True, frozen=True)

    field: Optional[CustomField] = None


@final
class GroupProjectCustomField(ProjectCustomField):
    model_config = ConfigDict(populate_by_name=True, frozen=True)

    type: Literal[ProjectCustomFieldTypeName.GROUP] = Field(alias="$type", default=ProjectCustomFieldTypeName.GROUP)


@final
class BundleProjectCustomField(BaseModel):
    model_config = ConfigDict(populate_by_name=True, frozen=True)

    type: Literal[ProjectCustomFieldTypeName.BUNDLE] = Field(alias="$type", default=ProjectCustomFieldTypeName.BUNDLE)
    field: Optional[CustomField] = None


@final
class BuildProjectCustomField(BaseModel):
    model_config = ConfigDict(populate_by_name=True, frozen=True)

    type: Literal[ProjectCustomFieldTypeName.BUILD] = Field(alias="$type", default=ProjectCustomFieldTypeName.BUILD)
    field: Optional[CustomField] = None


@final
class EnumProjectCustomField(BaseModel):
    model_config = ConfigDict(populate_by_name=True, frozen=True)
    type: Literal[ProjectCustomFieldTypeName.ENUM] = Field(alias="$type", default=ProjectCustomFieldTypeName.ENUM)
    field: Optional[CustomField] = None


@final
class OwnedProjectCustomField(BaseModel):
    model_config = ConfigDict(populate_by_name=True, frozen=True)

    type: Literal[ProjectCustomFieldTypeName.OWNED] = Field(alias="$type", default=ProjectCustomFieldTypeName.OWNED)
    field: Optional[CustomField] = None


@final
class StateProjectCustomField(BaseModel):
    model_config = ConfigDict(populate_by_name=True, frozen=True)

    type: Literal[ProjectCustomFieldTypeName.STATE] = Field(alias="$type", default=ProjectCustomFieldTypeName.STATE)
    field: Optional[CustomField] = None


@final
class UserProjectCustomField(BaseModel):
    model_config = ConfigDict(populate_by_name=True, frozen=True)

    type: Literal[ProjectCustomFieldTypeName.USER] = Field(alias="$type", default=ProjectCustomFieldTypeName.USER)
    field: Optional[CustomField] = None


@final
class VersionProjectCustomField(BaseModel):
    model_config = ConfigDict(populate_by_name=True, frozen=True)

    type: Literal[ProjectCustomFieldTypeName.VERSION] = Field(alias="$type", default=ProjectCustomFieldTypeName.VERSION)
    field: Optional[CustomField] = None


class SimpleProjectCustomField(BaseModel):
    model_config = ConfigDict(populate_by_name=True, frozen=True)

    type: Literal[ProjectCustomFieldTypeName.SIMPLE] = Field(alias="$type", default=ProjectCustomFieldTypeName.SIMPLE)
    field: Optional[CustomField] = None


@final
class TextProjectCustomField(BaseModel):
    model_config = ConfigDict(populate_by_name=True, frozen=True)

    type: Literal[ProjectCustomFieldTypeName.TEXT] = Field(alias="$type", default=ProjectCustomFieldTypeName.TEXT)
    field: Optional[CustomField] = None


@final
class PeriodProjectCustomField(BaseModel):
    model_config = ConfigDict(populate_by_name=True, frozen=True)

    type: Literal[ProjectCustomFieldTypeName.PERIOD] = Field(alias="$type", default=ProjectCustomFieldTypeName.PERIOD)
    field: Optional[CustomField] = None


ProjectCustomFieldType = Annotated[
    GroupProjectCustomField
    | BundleProjectCustomField
    | BuildProjectCustomField
    | EnumProjectCustomField
    | OwnedProjectCustomField
    | StateProjectCustomField
    | UserProjectCustomField
    | VersionProjectCustomField
    | SimpleProjectCustomField
    | TextProjectCustomField
    | PeriodProjectCustomField,
    Field(discriminator="type"),
]


@final
class IssueCustomFieldTypeName(StrEnum):
    TEXT = "TextIssueCustomField"
    SIMPLE = "SimpleIssueCustomField"
    DATE = "DateIssueCustomField"
    PERIOD = "PeriodIssueCustomField"
    MULTI_BUILD = "MultiBuildIssueCustomField"
    MULTI_ENUM = "MultiEnumIssueCustomField"
    MULTI_GROUP = "MultiGroupIssueCustomField"
    MULTI_OWNED = "MultiOwnedIssueCustomField"
    MULTI_USER = "MultiUserIssueCustomField"
    MULTI_VERSION = "MultiVersionIssueCustomField"
    SINGLE_BUILD = "SingleBuildIssueCustomField"
    SINGLE_ENUM = "SingleEnumIssueCustomField"
    SINGLE_GROUP = "SingleGroupIssueCustomField"
    SINGLE_OWNED = "SingleOwnedIssueCustomField"
    SINGLE_USER = "SingleUserIssueCustomField"
    SINGLE_VERSION = "SingleVersionIssueCustomField"
    STATE = "StateIssueCustomField"


@final
class IssueCustomField(BaseModel):
    model_config = ConfigDict(populate_by_name=True, frozen=True)

    id: Optional[str] = None
    name: Optional[str] = None
    project_custom_field: Optional[ProjectCustomFieldType] = Field(alias="projectCustomField", default=None)


@final
class TextIssueCustomField(BaseModel):
    model_config = ConfigDict(populate_by_name=True, frozen=True)

    type: Literal[IssueCustomFieldTypeName.TEXT] = Field(alias="$type", default=IssueCustomFieldTypeName.TEXT)
    id: Optional[str] = None
    name: Optional[str] = None
    value: Optional[TextFieldValue] = None


@final
class SimpleIssueCustomField(BaseModel):
    model_config = ConfigDict(populate_by_name=True, frozen=True)

    type: Literal[IssueCustomFieldTypeName.SIMPLE] = Field(alias="$type", default=IssueCustomFieldTypeName.SIMPLE)
    id: Optional[str] = None
    name: Optional[str] = None
    project_custom_field: Optional[ProjectCustomFieldType] = Field(alias="projectCustomField", default=None)
    value: Optional[YouTrackDateTime | StrictStr | StrictInt | StrictFloat] = None


@final
class DateIssueCustomField(BaseModel):
    model_config = ConfigDict(populate_by_name=True, frozen=True)

    type: Literal[IssueCustomFieldTypeName.DATE] = Field(alias="$type", default=IssueCustomFieldTypeName.DATE)
    id: Optional[str] = None
    name: Optional[str] = None
    project_custom_field: Optional[ProjectCustomFieldType] = Field(alias="projectCustomField", default=None)
    value: Optional[YouTrackDate] = None


@final
class PeriodIssueCustomField(BaseModel):
    model_config = ConfigDict(populate_by_name=True, frozen=True)

    type: Literal[IssueCustomFieldTypeName.PERIOD] = Field(alias="$type", default=IssueCustomFieldTypeName.PERIOD)
    id: Optional[str] = None
    name: Optional[str] = None
    value: Optional[PeriodValue] = None


@final
class MultiBuildIssueCustomField(BaseModel):
    model_config = ConfigDict(populate_by_name=True, frozen=True)

    type: Literal[IssueCustomFieldTypeName.MULTI_BUILD] = Field(
        alias="$type",
        default=IssueCustomFieldTypeName.MULTI_BUILD,
    )
    id: Optional[str] = None
    name: Optional[str] = None
    value: Sequence[BuildBundleElement]


@final
class MultiEnumIssueCustomField(BaseModel):
    model_config = ConfigDict(populate_by_name=True, frozen=True)

    type: Literal[IssueCustomFieldTypeName.MULTI_ENUM] = Field(
        alias="$type",
        default=IssueCustomFieldTypeName.MULTI_ENUM,
    )
    id: Optional[str] = None
    name: Optional[str] = None
    value: Sequence[EnumBundleElement]


@final
class MultiGroupIssueCustomField(BaseModel):
    model_config = ConfigDict(populate_by_name=True, frozen=True)

    type: Literal[IssueCustomFieldTypeName.MULTI_GROUP] = Field(
        alias="$type",
        default=IssueCustomFieldTypeName.MULTI_GROUP,
    )
    id: Optional[str] = None
    name: Optional[str] = None
    value: Sequence[UserGroup]


@final
class MultiOwnedIssueCustomField(BaseModel):
    model_config = ConfigDict(populate_by_name=True, frozen=True)

    type: Literal[IssueCustomFieldTypeName.MULTI_OWNED] = Field(
        alias="$type",
        default=IssueCustomFieldTypeName.MULTI_OWNED,
    )
    id: Optional[str] = None
    name: Optional[str] = None
    value: Sequence[OwnedBundleElement]


@final
class MultiUserIssueCustomField(BaseModel):
    model_config = ConfigDict(populate_by_name=True, frozen=True)

    type: Literal[IssueCustomFieldTypeName.MULTI_USER] = Field(
        alias="$type",
        default=IssueCustomFieldTypeName.MULTI_USER,
    )
    id: Optional[str] = None
    name: Optional[str] = None
    value: Sequence[User]


@final
class MultiVersionIssueCustomField(BaseModel):
    model_config = ConfigDict(populate_by_name=True, frozen=True)

    type: Literal[IssueCustomFieldTypeName.MULTI_VERSION] = Field(
        alias="$type",
        default=IssueCustomFieldTypeName.MULTI_VERSION,
    )
    id: Optional[str] = None
    name: Optional[str] = None
    value: Sequence[VersionBundleElement]


@final
class SingleBuildIssueCustomField(BaseModel):
    model_config = ConfigDict(populate_by_name=True, frozen=True)

    type: Literal[IssueCustomFieldTypeName.SINGLE_BUILD] = Field(
        alias="$type",
        default=IssueCustomFieldTypeName.SINGLE_BUILD,
    )
    id: Optional[str] = None
    name: Optional[str] = None
    value: Optional[BuildBundleElement] = None


@final
class SingleEnumIssueCustomField(BaseModel):
    model_config = ConfigDict(populate_by_name=True, frozen=True)

    type: Literal[IssueCustomFieldTypeName.SINGLE_ENUM] = Field(
        alias="$type",
        default=IssueCustomFieldTypeName.SINGLE_ENUM,
    )
    id: Optional[str] = None
    name: Optional[str] = None
    value: Optional[EnumBundleElement] = None


@final
class SingleGroupIssueCustomField(BaseModel):
    model_config = ConfigDict(populate_by_name=True, frozen=True)

    type: Literal[IssueCustomFieldTypeName.SINGLE_GROUP] = Field(
        alias="$type",
        default=IssueCustomFieldTypeName.SINGLE_GROUP,
    )
    id: Optional[str] = None
    name: Optional[str] = None
    value: Optional[UserGroup] = None


@final
class SingleOwnedIssueCustomField(BaseModel):
    model_config = ConfigDict(populate_by_name=True, frozen=True)

    type: Literal[IssueCustomFieldTypeName.SINGLE_OWNED] = Field(
        alias="$type",
        default=IssueCustomFieldTypeName.SINGLE_OWNED,
    )
    id: Optional[str] = None
    name: Optional[str] = None
    value: Optional[OwnedBundleElement] = None


@final
class SingleUserIssueCustomField(BaseModel):
    model_config = ConfigDict(populate_by_name=True, frozen=True)

    type: Literal[IssueCustomFieldTypeName.SINGLE_USER] = Field(
        alias="$type",
        default=IssueCustomFieldTypeName.SINGLE_USER,
    )
    id: Optional[str] = None
    name: Optional[str] = None
    value: Optional[User] = None


@final
class SingleVersionIssueCustomField(BaseModel):
    model_config = ConfigDict(populate_by_name=True, frozen=True)

    type: Literal[IssueCustomFieldTypeName.SINGLE_VERSION] = Field(
        alias="$type",
        default=IssueCustomFieldTypeName.SINGLE_VERSION,
    )
    id: Optional[str] = None
    name: Optional[str] = None
    value: Optional[VersionBundleElement] = None


@final
class StateIssueCustomField(BaseModel):
    model_config = ConfigDict(populate_by_name=True, frozen=True)

    type: Literal[IssueCustomFieldTypeName.STATE] = Field(alias="$type", default=IssueCustomFieldTypeName.STATE)
    id: Optional[str] = None
    name: Optional[str] = None
    value: Optional[StateBundleElement] = None


IssueCustomFieldType = Annotated[
    SingleEnumIssueCustomField
    | MultiEnumIssueCustomField
    | SingleBuildIssueCustomField
    | MultiBuildIssueCustomField
    | StateIssueCustomField
    | SingleVersionIssueCustomField
    | MultiVersionIssueCustomField
    | SingleOwnedIssueCustomField
    | MultiOwnedIssueCustomField
    | SingleUserIssueCustomField
    | MultiUserIssueCustomField
    | SingleGroupIssueCustomField
    | MultiGroupIssueCustomField
    | SimpleIssueCustomField
    | DateIssueCustomField
    | PeriodIssueCustomField
    | TextIssueCustomField,
    Field(discriminator="type"),
]


@final
class ProjectTypeName(StrEnum):
    PROJECT = "Project"


@final
class Project(BaseModel):
    model_config = ConfigDict(populate_by_name=True, frozen=True)

    type: Literal[ProjectTypeName.PROJECT] = Field(alias="$type", default=ProjectTypeName.PROJECT)
    id: Optional[str] = None
    name: Optional[str] = None
    short_name: Optional[str] = Field(alias="shortName", default=None)


@final
class TagTypeName(StrEnum):
    TAG = "Tag"


@final
class Tag(BaseModel):
    model_config = ConfigDict(populate_by_name=True, frozen=True)

    type: Literal[TagTypeName.TAG] = Field(alias="$type", default=TagTypeName.TAG)
    id: Optional[str] = None
    name: Optional[str] = None


@final
class IssueTypeName(StrEnum):
    ISSUE = "Issue"


@final
class Issue(BaseModel):
    model_config = ConfigDict(populate_by_name=True, frozen=True)

    type: Literal[IssueTypeName.ISSUE] = Field(alias="$type", default=IssueTypeName.ISSUE)
    id: Optional[str] = None
    id_readable: Optional[str] = Field(alias="idReadable", default=None)
    created: Optional[AwareDatetime] = None
    updated: Optional[AwareDatetime] = None
    resolved: Optional[AwareDatetime] = None
    project: Optional[Project] = None
    reporter: Optional[User] = None
    updater: Optional[User] = None
    summary: Optional[str] = None
    description: Optional[str] = None
    wikified_description: Optional[str] = Field(alias="wikifiedDescription", default=None)
    comments_count: Optional[int] = Field(alias="commentsCount", default=None)
    tags: Optional[Sequence[Tag]] = None
    custom_fields: Optional[Sequence[IssueCustomFieldType]] = Field(alias="customFields", default=None)

    @property
    def url(self) -> str:
        return f"/issue/{self.id_readable}"


@final
class IssueAttachmentTypeName(StrEnum):
    ISSUE_ATTACHMENT = "IssueAttachment"


@final
class IssueAttachment(BaseModel):
    model_config = ConfigDict(populate_by_name=True, frozen=True)

    type: Literal[IssueAttachmentTypeName.ISSUE_ATTACHMENT] = Field(
        alias="$type",
        default=IssueAttachmentTypeName.ISSUE_ATTACHMENT,
    )
    id: Optional[str] = None
    name: Optional[str] = None
    author: Optional[User] = None
    created: Optional[AwareDatetime] = None
    updated: Optional[AwareDatetime] = None
    mime_type: Optional[str] = Field(alias="mimeType", default=None)
    url: Optional[str] = None


@final
class IssueCommentTypeName(StrEnum):
    ISSUE_COMMENT = "IssueComment"


@final
class IssueComment(BaseModel):
    model_config = ConfigDict(populate_by_name=True, frozen=True)

    type: Literal[IssueCommentTypeName.ISSUE_COMMENT] = Field(alias="$type", default=IssueCommentTypeName.ISSUE_COMMENT)
    id: Optional[str] = None
    text: Optional[str] = None
    text_preview: Optional[str] = Field(alias="textPreview", default=None)
    created: Optional[AwareDatetime] = None
    updated: Optional[AwareDatetime] = None
    author: Optional[User] = None
    attachments: Optional[Sequence[IssueAttachment]] = None
    deleted: Optional[bool] = None


@final
class IssueLinkTypeTypeName(StrEnum):
    ISSUE_LINK_TYPE = "IssueLinkType"


@final
class IssueLinkType(BaseModel):
    model_config = ConfigDict(populate_by_name=True, frozen=True)

    type: Literal[IssueLinkTypeTypeName.ISSUE_LINK_TYPE] = Field(
        alias="$type", default=IssueLinkTypeTypeName.ISSUE_LINK_TYPE
    )
    id: Optional[str] = None
    name: Optional[str] = None
    localized_name: Optional[str] = Field(alias="localizedName", default=None)
    source_to_target: Optional[str] = Field(alias="sourceToTarget", default=None)
    localized_source_to_target: Optional[str] = Field(alias="localizedSourceToTarget", default=None)
    target_to_source: Optional[str] = Field(alias="targetToSource", default=None)
    localized_target_to_source: Optional[str] = Field(alias="localizedTargetToSource", default=None)
    directed: Optional[bool] = None
    aggregation: Optional[bool] = None
    read_only: Optional[bool] = Field(alias="readOnly", default=None)


@final
class IssueLink(BaseModel):
    model_config = ConfigDict(populate_by_name=True, frozen=True)

    id: Optional[str] = None
    direction: Optional[Literal["OUTWARD", "INWARD", "BOTH"]] = None
    link_type: Optional[IssueLinkType] = Field(alias="linkType", default=None)
    issues: Optional[Sequence[Issue]] = None
    trimmed_issues: Optional[Sequence[Issue]] = Field(alias="trimmedIssues", default=None)


@final
class WorkItemTypeTypeName(StrEnum):
    WORK_ITEM_TYPE = "WorkItemType"


@final
class WorkItemType(BaseModel):
    model_config = ConfigDict(populate_by_name=True, frozen=True)

    type: Literal[WorkItemTypeTypeName.WORK_ITEM_TYPE] = Field(
        alias="$type",
        default=WorkItemTypeTypeName.WORK_ITEM_TYPE,
    )
    id: Optional[str] = None
    name: Optional[str] = None


@final
class IssueWorkItemTypeName(StrEnum):
    ISSUE_WORK_ITEM = "IssueWorkItem"


@final
class IssueWorkItem(BaseModel):
    model_config = ConfigDict(populate_by_name=True, frozen=True)

    type: Literal[IssueWorkItemTypeName.ISSUE_WORK_ITEM] = Field(
        alias="$type", default=IssueWorkItemTypeName.ISSUE_WORK_ITEM
    )
    id: Optional[str] = None
    author: Optional[User] = None
    creator: Optional[User] = None
    text: Optional[str] = None
    text_preview: Optional[str] = Field(alias="textPreview", default=None)
    work_item_type: Optional[WorkItemType] = Field(alias="type", default=None)
    created: Optional[AwareDatetime] = None
    updated: Optional[AwareDatetime] = None
    duration: Optional[DurationValue] = None
    date: Optional[AwareDatetime] = None


@final
class AgileTypeName(StrEnum):
    AGILE = "Agile"


@final
class AgileRef(BaseModel):
    model_config = ConfigDict(populate_by_name=True, frozen=True)

    type: Literal[AgileTypeName.AGILE] = Field(alias="$type", default=AgileTypeName.AGILE)
    id: Optional[str] = None
    name: Optional[str] = None


@final
class SprintTypeName(StrEnum):
    SPRINT = "Sprint"


@final
class SprintRef(BaseModel):
    model_config = ConfigDict(populate_by_name=True, frozen=True)

    type: Literal[SprintTypeName.SPRINT] = Field(alias="$type", default=SprintTypeName.SPRINT)
    id: Optional[str] = None
    name: Optional[str] = None


@final
class Agile(BaseModel):
    model_config = ConfigDict(populate_by_name=True, frozen=True)

    type: Literal[AgileTypeName.AGILE] = Field(alias="$type", default=AgileTypeName.AGILE)
    id: Optional[str] = None
    name: Optional[str] = None
    owner: Optional[User] = None
    visible_for: Optional[UserGroup] = Field(alias="visibleFor", default=None)
    projects: Optional[Sequence[Project]] = None
    sprints: Optional[Sequence[SprintRef]] = None
    current_sprint: Optional[SprintRef] = Field(alias="currentSprint", default=None)


@final
class Sprint(BaseModel):
    model_config = ConfigDict(populate_by_name=True, frozen=True)

    type: Literal[SprintTypeName.SPRINT] = Field(alias="$type", default=SprintTypeName.SPRINT)
    id: Optional[str] = None
    name: Optional[str] = None
    agile: Optional[AgileRef] = None
    goal: Optional[str] = None
    start: Optional[AwareDatetime] = None
    finish: Optional[AwareDatetime] = None
    archived: Optional[bool] = None
    is_default: Optional[bool] = Field(alias="isDefault", default=None)
    issues: Optional[Sequence[Issue]] = None
    unresolved_issues_count: Optional[int] = Field(alias="unresolvedIssuesCount", default=None)
    previous_sprint: Optional[SprintRef] = Field(alias="previousSprint", default=None)
