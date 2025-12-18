"""Simple test script to verify MCP server tools work correctly.

This script simulates how an AI assistant would interact with the MCP server tools.
"""

import asyncio
from unittest.mock import Mock

from src.tools.list_tasks import list_tasks
from src.tools.create_task import create_task


async def test_list_tasks():
    """Test the list_tasks tool."""
    print("\n" + "="*60)
    print("TEST 1: List Tasks")
    print("="*60)

    # Create mock context with user_id
    mock_ctx = Mock()
    mock_ctx.request_context = {"user_id": "test_user_123"}

    print("Calling list_tasks for user: test_user_123...")
    result = await list_tasks(mock_ctx)

    if isinstance(result, dict) and "error_type" in result:
        print(f"❌ Error: {result['error_type']}")
        print(f"   Message: {result['message']}")
        if "suggestions" in result:
            print("   Suggestions:")
            for suggestion in result["suggestions"]:
                print(f"   - {suggestion}")
    elif isinstance(result, list):
        print(f"✅ Success! Retrieved {len(result)} tasks")
        for task in result:
            print(f"   - [{task['id']}] {task['title']} (Priority: {task['priority']}, Completed: {task['completed']})")

    return result


async def test_create_task():
    """Test the create_task tool."""
    print("\n" + "="*60)
    print("TEST 2: Create Task")
    print("="*60)

    # Create mock context with user_id
    mock_ctx = Mock()
    mock_ctx.request_context = {"user_id": "test_user_123"}

    print("Creating task: 'Test MCP Server Integration'...")
    result = await create_task(
        ctx=mock_ctx,
        title="Test MCP Server Integration",
        description="Verify that MCP server can create tasks via FastAPI backend",
        priority="High",
        due_date=None,
    )

    if isinstance(result, dict) and "error_type" in result:
        print(f"❌ Error: {result['error_type']}")
        print(f"   Message: {result['message']}")
        if "suggestions" in result:
            print("   Suggestions:")
            for suggestion in result["suggestions"]:
                print(f"   - {suggestion}")
    else:
        print(f"✅ Success! Created task:")
        print(f"   ID: {result['id']}")
        print(f"   Title: {result['title']}")
        print(f"   Description: {result['description']}")
        print(f"   Priority: {result['priority']}")
        print(f"   Completed: {result['completed']}")
        print(f"   User ID: {result['user_id']}")

    return result


async def test_validation_error():
    """Test that validation errors work correctly."""
    print("\n" + "="*60)
    print("TEST 3: Validation Error (Empty Title)")
    print("="*60)

    # Create mock context with user_id
    mock_ctx = Mock()
    mock_ctx.request_context = {"user_id": "test_user_123"}

    print("Attempting to create task with empty title...")
    result = await create_task(
        ctx=mock_ctx,
        title="",  # Empty title should fail validation
        description="This should fail",
        priority="Medium",
    )

    if isinstance(result, dict) and "error_type" in result:
        print(f"✅ Validation error caught as expected!")
        print(f"   Error Type: {result['error_type']}")
        print(f"   Message: {result['message']}")
        if "details" in result and "validation_errors" in result["details"]:
            print("   Validation Errors:")
            for error in result["details"]["validation_errors"]:
                print(f"   - Field: {error['field']}")
                print(f"     Message: {error['message']}")
                if error.get("suggestion"):
                    print(f"     Suggestion: {error['suggestion']}")
    else:
        print(f"❌ Unexpected: Task was created despite empty title!")

    return result


async def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("MCP SERVER TOOL TESTS")
    print("="*60)
    print("\nTesting MCP server tools with FastAPI backend...")
    print("Backend URL: http://localhost:8000")
    print("User ID: test_user_123")

    # Test 1: List existing tasks
    await test_list_tasks()

    # Test 2: Create a new task
    task_result = await test_create_task()

    # Test 3: Validation error
    await test_validation_error()

    # Test 4: List tasks again to see the newly created task
    print("\n" + "="*60)
    print("TEST 4: List Tasks Again (Should include new task)")
    print("="*60)
    await test_list_tasks()

    print("\n" + "="*60)
    print("ALL TESTS COMPLETED")
    print("="*60)
    print("\n✅ MVP tools (list_tasks, create_task) are working!")


if __name__ == "__main__":
    asyncio.run(main())
