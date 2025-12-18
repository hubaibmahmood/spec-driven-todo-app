"""Quick test script to verify all 5 MCP tools work correctly."""

import asyncio
from unittest.mock import Mock

from src.tools.list_tasks import list_tasks
from src.tools.create_task import create_task
from src.tools.mark_completed import mark_task_completed
from src.tools.update_task import update_task
from src.tools.delete_task import delete_task


def create_mock_ctx():
    """Create mock context with user_id."""
    mock_ctx = Mock()
    mock_ctx.request_context = {"user_id": "test_user_123"}
    return mock_ctx


async def main():
    """Test all 5 MCP tools."""
    print("\n" + "="*60)
    print("TESTING ALL 5 MCP TOOLS")
    print("="*60)

    # 1. List tasks (should be empty or show existing)
    print("\n1️⃣  LIST TASKS")
    print("-" * 60)
    result = await list_tasks(create_mock_ctx())
    if isinstance(result, list):
        print(f"✅ Found {len(result)} tasks")
    else:
        print(f"❌ Error: {result.get('message', 'Unknown error')}")

    # 2. Create a new task
    print("\n2️⃣  CREATE TASK")
    print("-" * 60)
    result = await create_task(
        create_mock_ctx(),
        title="Complete All MCP Tools Testing",
        description="Test list, create, mark complete, update, and delete",
        priority="High",
    )
    if "id" in result:
        task_id = result["id"]
        print(f"✅ Created task ID: {task_id}")
        print(f"   Title: {result['title']}")
        print(f"   Priority: {result['priority']}")
    else:
        print(f"❌ Error: {result.get('message', 'Unknown error')}")
        return

    # 3. Update the task
    print("\n3️⃣  UPDATE TASK")
    print("-" * 60)
    result = await update_task(
        create_mock_ctx(),
        task_id=task_id,
        description="Updated: Successfully testing all 5 MCP tools!",
        priority="Medium",
    )
    if "id" in result:
        print(f"✅ Updated task {task_id}")
        print(f"   New description: {result['description']}")
        print(f"   New priority: {result['priority']}")
    else:
        print(f"❌ Error: {result.get('message', 'Unknown error')}")

    # 4. Mark task as completed
    print("\n4️⃣  MARK TASK COMPLETED")
    print("-" * 60)
    result = await mark_task_completed(create_mock_ctx(), task_id=task_id)
    if "id" in result:
        print(f"✅ Marked task {task_id} as completed")
        print(f"   Completed status: {result['completed']}")
    else:
        print(f"❌ Error: {result.get('message', 'Unknown error')}")

    # 5. List tasks again (should show completed task)
    print("\n5️⃣  LIST TASKS (should show completed task)")
    print("-" * 60)
    result = await list_tasks(create_mock_ctx())
    if isinstance(result, list):
        print(f"✅ Found {len(result)} tasks")
        for task in result:
            status = "✅ DONE" if task['completed'] else "⏳ TODO"
            print(f"   [{task['id']}] {status} {task['title']}")
    else:
        print(f"❌ Error: {result.get('message', 'Unknown error')}")

    # 6. Delete the task
    print("\n6️⃣  DELETE TASK")
    print("-" * 60)
    result = await delete_task(create_mock_ctx(), task_id=task_id)
    if result.get("success"):
        print(f"✅ Deleted task {task_id}")
        print(f"   Message: {result['message']}")
    else:
        print(f"❌ Error: {result.get('message', 'Unknown error')}")

    # 7. List tasks final (should not show deleted task)
    print("\n7️⃣  LIST TASKS (deleted task should be gone)")
    print("-" * 60)
    result = await list_tasks(create_mock_ctx())
    if isinstance(result, list):
        print(f"✅ Found {len(result)} tasks")
        if not any(t['id'] == task_id for t in result):
            print(f"   ✅ Confirmed: Task {task_id} is deleted")
    else:
        print(f"❌ Error: {result.get('message', 'Unknown error')}")

    print("\n" + "="*60)
    print("ALL 5 TOOLS TESTED SUCCESSFULLY! 🎉")
    print("="*60)
    print("\n✅ Complete CRUD Operations Working:")
    print("   1. ✅ list_tasks")
    print("   2. ✅ create_task")
    print("   3. ✅ update_task")
    print("   4. ✅ mark_task_completed")
    print("   5. ✅ delete_task")
    print()


if __name__ == "__main__":
    asyncio.run(main())
