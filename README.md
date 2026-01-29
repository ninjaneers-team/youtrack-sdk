# YouTrack REST API Client

A client library for accessing YouTrack REST API.

This is a fork of [moneymeets/youtrack-sdk](https://github.com/moneymeets/youtrack-sdk) with several enhancements.

## Key Changes from Original

This fork includes the following improvements over the original repository:

- **AsyncClient Implementation**: Full async/await support with `AsyncClient` for non-blocking I/O operations
- **Project Custom Fields API**: New `get_project_custom_fields()` method to retrieve custom field definitions for projects
- **Migrated to UV**: Switched from Poetry to UV for dependency management
- **Enhanced Testing**: Migrated test suite from unittest to Pytest with async test support
- **Modern Python**: Updated to require Python 3.13+ with improved type hints and linting
- **Improved Code Quality**: Enhanced linting with Ruff and type checking with Pyright

## Usage

### Synchronous Client

```python
from datetime import date
from youtrack_sdk import Client
from youtrack_sdk.entities import (
    DateIssueCustomField,
    EnumBundleElement,
    Issue,
    Tag,
    Project,
    SingleEnumIssueCustomField,
    SingleUserIssueCustomField,
    StateBundleElement,
    StateIssueCustomField,
    User,
)

with Client(base_url="https://dummy.myjetbrains.com/youtrack", token="dummy") as client:
    result = client.create_issue(
        issue=Issue(
            project=Project(id="0-0"),
            summary="Created from YouTrack SDK",
            description="Description **text**.",
            tags=[
                Tag(id="6-0"),
            ],
            custom_fields=[
                StateIssueCustomField(
                    name="State",
                    value=StateBundleElement(
                        name="In Progress",
                    ),
                ),
                SingleUserIssueCustomField(
                    name="Assignee",
                    value=User(
                        ring_id="00000000-a31c-4174-bb27-abd3387df67a",
                    ),
                ),
                SingleEnumIssueCustomField(
                    name="Type",
                    value=EnumBundleElement(
                        name="Bug",
                    ),
                ),
                DateIssueCustomField(
                    name="Due Date",
                    value=date(2005, 12, 31),
                ),
            ],
        ),
    )
```

### Async Client

```python
import asyncio
from youtrack_sdk import AsyncClient
from youtrack_sdk.entities import Project

async def main():
    async with AsyncClient(base_url="https://dummy.myjetbrains.com/youtrack", token="dummy") as client:
        projects = await client.get_projects()
        for project in projects:
            print(f"Project: {project.name}")

asyncio.run(main())
```

### Fetching Project Custom Fields

```python
from youtrack_sdk import Client

with Client(base_url="https://dummy.myjetbrains.com/youtrack", token="dummy") as client:
    custom_fields = client.get_project_custom_fields(project_id="0-0")

    for field in custom_fields:
        print(f"Field: {field.field.name}, Type: {type(field).__name__}")
```

See [examples/list_project_custom_fields.py](examples/list_project_custom_fields.py) for a complete example.

## Note

- You should prefer to use internal entity IDs everywhere. Some methods accept readable issue IDs (e.g. HD-99) but it's not supported everywhere.
