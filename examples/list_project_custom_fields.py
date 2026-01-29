#!/usr/bin/env python3
"""Example script to list all custom fields for a YouTrack project.

This script demonstrates how to:
- Connect to YouTrack with an API token
- Fetch all custom fields for a project
- Display field details including bundle values (enum variants, states, etc.)
- Fetch an example issue and display its custom field values
"""

import argparse
import asyncio
import sys

from youtrack_sdk import AsyncClient
from youtrack_sdk.entities import BuildProjectCustomField
from youtrack_sdk.entities import BundleProjectCustomField
from youtrack_sdk.entities import DateIssueCustomField
from youtrack_sdk.entities import EnumProjectCustomField
from youtrack_sdk.entities import GroupProjectCustomField
from youtrack_sdk.entities import MultiBuildIssueCustomField
from youtrack_sdk.entities import MultiEnumIssueCustomField
from youtrack_sdk.entities import MultiGroupIssueCustomField
from youtrack_sdk.entities import MultiOwnedIssueCustomField
from youtrack_sdk.entities import MultiUserIssueCustomField
from youtrack_sdk.entities import MultiVersionIssueCustomField
from youtrack_sdk.entities import OwnedProjectCustomField
from youtrack_sdk.entities import PeriodIssueCustomField
from youtrack_sdk.entities import PeriodProjectCustomField
from youtrack_sdk.entities import SimpleIssueCustomField
from youtrack_sdk.entities import SimpleProjectCustomField
from youtrack_sdk.entities import SingleBuildIssueCustomField
from youtrack_sdk.entities import SingleEnumIssueCustomField
from youtrack_sdk.entities import SingleGroupIssueCustomField
from youtrack_sdk.entities import SingleOwnedIssueCustomField
from youtrack_sdk.entities import SingleUserIssueCustomField
from youtrack_sdk.entities import SingleVersionIssueCustomField
from youtrack_sdk.entities import StateIssueCustomField
from youtrack_sdk.entities import StateProjectCustomField
from youtrack_sdk.entities import TextIssueCustomField
from youtrack_sdk.entities import TextProjectCustomField
from youtrack_sdk.entities import UserProjectCustomField
from youtrack_sdk.entities import VersionProjectCustomField
from youtrack_sdk.exceptions import YouTrackNotFound


async def display_custom_fields(server_url: str, token: str, project_id: str) -> None:
    """Fetch and display all custom fields for a project."""
    # Create client
    async with AsyncClient(base_url=server_url, token=token) as client:
        # Fetch custom fields
        print(f"Fetching custom fields for project: {project_id}")
        print("=" * 80)
        print()

        try:
            custom_fields = await client.get_project_custom_fields(project_id=project_id)
        except YouTrackNotFound:
            print(f"Error: Project '{project_id}' not found.\n", file=sys.stderr)
            print("Available projects:", file=sys.stderr)
            try:
                projects = await client.get_projects()
                for project in projects:
                    project_name = project.name or "Unknown"
                    print(f"  - {project.short_name}: {project_name}", file=sys.stderr)
            except Exception as e:
                print(f"  Could not retrieve projects: {e}", file=sys.stderr)
            sys.exit(1)

        if not custom_fields:
            print("No custom fields found for this project.")
            return

        print(f"Found {len(custom_fields)} custom field(s):\n")

        # Display each field
        for idx, field in enumerate(custom_fields, 1):
            field_name = field.field.name if field.field and field.field.name else "Unknown"
            print(f"{idx}. {field_name}")
            print(f"   ID: {field.id}")
            print(f"   Type: {field.type}")

            # Check if field is multi-value by examining field_type.id
            if field.field and field.field.field_type and field.field.field_type.id:
                field_type_id = field.field.field_type.id
                is_multi = "[*]" in field_type_id
                print(f"   Field Type: {field_type_id}")
                print(f"   Multi-value: {is_multi}")

            print(f"   Can be empty: {field.can_be_empty}")
            print(f"   Is public: {field.is_public}")

            # Display bundle values for bundle-type fields
            match field:
                case EnumProjectCustomField(bundle=bundle) if bundle is not None and bundle.values is not None:
                    print(f"   Enum Values ({len(bundle.values)}):")
                    for value in bundle.values:
                        print(f"      - {value.name} (ID: {value.id})")
                case EnumProjectCustomField():
                    print("   Enum Values: None")

                case StateProjectCustomField(bundle=bundle) if bundle is not None and bundle.values is not None:
                    print(f"   State Values ({len(bundle.values)}):")
                    for value in bundle.values:
                        print(f"      - {value.name} (ID: {value.id})")
                case StateProjectCustomField():
                    print("   State Values: None")

                case UserProjectCustomField(bundle=bundle) if bundle is not None and bundle.values is not None:
                    print(f"   Available Users ({len(bundle.values)}):")
                    for user in bundle.values:
                        print(f"      - {user.name} (ID: {user.id})")
                case UserProjectCustomField():
                    print("   Available Users: None")

                case VersionProjectCustomField(bundle=bundle) if bundle is not None and bundle.values is not None:
                    print(f"   Available Versions ({len(bundle.values)}):")
                    for item in bundle.values:
                        print(f"      - {item.name} (ID: {item.id})")
                case VersionProjectCustomField():
                    print("   Available Versions: None")

                case BuildProjectCustomField(bundle=bundle) if bundle is not None and bundle.values is not None:
                    print(f"   Available Builds ({len(bundle.values)}):")
                    for item in bundle.values:
                        print(f"      - {item.name} (ID: {item.id})")
                case BuildProjectCustomField():
                    print("   Available Builds: None")

                case OwnedProjectCustomField(bundle=bundle) if bundle is not None and bundle.values is not None:
                    print(f"   Available Values ({len(bundle.values)}):")
                    for item in bundle.values:
                        print(f"      - {item.name} (ID: {item.id})")
                case OwnedProjectCustomField():
                    print("   Available Values: None")

                case (
                    SimpleProjectCustomField()
                    | TextProjectCustomField()
                    | PeriodProjectCustomField()
                    | GroupProjectCustomField()
                    | BundleProjectCustomField()
                ):
                    # These field types don't have bundle values
                    # They accept free-form values or have different structures
                    pass

            print()

        # Fetch and display an example issue with its custom field values
        print("\n" + "=" * 80)
        print("EXAMPLE ISSUE WITH CUSTOM FIELD VALUES")
        print("=" * 80)
        print()

        try:
            # Fetch one issue from the project
            issues = await client.get_issues(query=f"project: {project_id}", count=1)
            if not issues:
                print(f"No issues found in project {project_id}")
                return

            issue = issues[0]
            print(f"Issue: {issue.id_readable}")
            if issue.summary:
                print(f"Summary: {issue.summary}")
            print()

            # Display custom field values
            if issue.custom_fields:
                print("Custom Fields:")
                for custom_field in issue.custom_fields:
                    field_name = custom_field.name if custom_field.name is not None else "Unknown field"
                    field_id = custom_field.id if custom_field.id is not None else "unknown"
                    print(f"  {field_name} (ID: {field_id}):")

                    match custom_field:
                        case PeriodIssueCustomField(value=value) if value is not None:
                            print(f"    Value: {value.presentation}")
                        case (
                            SingleEnumIssueCustomField(value=value)
                            | StateIssueCustomField(value=value)
                            | SingleBuildIssueCustomField(value=value)
                            | SingleVersionIssueCustomField(value=value)
                            | SingleOwnedIssueCustomField(value=value)
                        ) if value is not None:
                            value_id = value.id if value.id is not None else "unknown"
                            print(f"    Value: {value.name} (ID: {value_id})")
                        case SingleUserIssueCustomField(value=value) | SingleGroupIssueCustomField(value=value) if (
                            value is not None
                        ):
                            value_id = value.id if value.id is not None else "unknown"
                            print(f"    Value: {value.name} (ID: {value_id})")
                        case (
                            MultiEnumIssueCustomField(value=values)
                            | MultiBuildIssueCustomField(value=values)
                            | MultiVersionIssueCustomField(value=values)
                            | MultiOwnedIssueCustomField(value=values)
                            | MultiUserIssueCustomField(value=values)
                            | MultiGroupIssueCustomField(value=values)
                        ):
                            print(f"    Values ({len(values)}):")
                            for v in values:
                                value_id = v.id if v.id is not None else "unknown"
                                print(f"      - {v.name} (ID: {value_id})")
                        case SimpleIssueCustomField(value=value) | DateIssueCustomField(value=value) if (
                            value is not None
                        ):
                            print(f"    Value: {value}")
                        case TextIssueCustomField(value=value) if value is not None:
                            print(f"    Value: {value.text}")
                        case (
                            PeriodIssueCustomField()
                            | SingleEnumIssueCustomField()
                            | MultiEnumIssueCustomField()
                            | SingleBuildIssueCustomField()
                            | MultiBuildIssueCustomField()
                            | StateIssueCustomField()
                            | SingleVersionIssueCustomField()
                            | MultiVersionIssueCustomField()
                            | SingleOwnedIssueCustomField()
                            | MultiOwnedIssueCustomField()
                            | SingleUserIssueCustomField()
                            | MultiUserIssueCustomField()
                            | SingleGroupIssueCustomField()
                            | MultiGroupIssueCustomField()
                            | SimpleIssueCustomField()
                            | DateIssueCustomField()
                            | TextIssueCustomField()
                        ):
                            print("    Value: (empty)")
            else:
                print("No custom fields on this issue")

        except Exception as e:
            print(f"Could not fetch example issue: {e}", file=sys.stderr)


async def main() -> None:
    """Parse arguments and run the script."""
    parser = argparse.ArgumentParser(
        description="List all custom fields for a YouTrack project",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s https://youtrack.example.com perm:abc123 DEMO
  %(prog)s https://youtrack.example.com perm:abc123 PROJECT-1
        """,
    )

    parser.add_argument(
        "server_url",
        help="YouTrack server URL (e.g., https://youtrack.example.com)",
    )
    parser.add_argument(
        "token",
        help="YouTrack API token (permanent token starting with 'perm:')",
    )
    parser.add_argument(
        "project_id",
        help="Project ID or short name (e.g., DEMO or PROJECT-1)",
    )

    args = parser.parse_args()

    await display_custom_fields(
        server_url=args.server_url,
        token=args.token,
        project_id=args.project_id,
    )


if __name__ == "__main__":
    asyncio.run(main())
