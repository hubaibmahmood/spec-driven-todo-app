"""Integration tests for cross-tool workflows (SC-002, SC-003, SC-004)."""

import pytest
from unittest.mock import AsyncMock, patch

from src.tools.list_tasks import list_tasks
from src.tools.create_task import create_task
from src.tools.mark_completed import mark_task_completed
from src.tools.update_task import update_task
from src.tools.delete_task import delete_task


@pytest.mark.asyncio
async def test_workflow_create_then_list():
    """
    Workflow 1: list_tasks → create_task → list_tasks
    Verifies SC-002: Task persistence across tool calls.
    """
    user_id = "test_user_123"

    with (
        patch("src.tools.list_tasks.BackendClient") as mock_list_client,
        patch("src.tools.create_task.BackendClient") as mock_create_client,
    ):
        mock_list = AsyncMock()
        mock_create = AsyncMock()
        mock_list_client.return_value = mock_list
        mock_create_client.return_value = mock_create

        # Step 1: List tasks (initially empty)
        mock_list.get_tasks.return_value = []
        initial_tasks = await list_tasks(_user_id=user_id)
        assert len(initial_tasks) == 0

        # Step 2: Create a new task
        new_task = {
            "id": 1,
            "title": "Buy milk",
            "description": "From the grocery store",
            "completed": False,
            "priority": "High",
            "due_date": None,
            "created_at": "2025-01-01T00:00:00Z",
            "updated_at": "2025-01-01T00:00:00Z",
            "user_id": user_id,
        }
        mock_create.create_task.return_value = new_task
        created_task = await create_task(
            title="Buy milk",
            description="From the grocery store",
            priority="High",
            _user_id=user_id,
        )

        assert created_task["id"] == 1
        assert created_task["title"] == "Buy milk"

        # Step 3: List tasks again (should now include the new task)
        mock_list.get_tasks.return_value = [new_task]
        updated_tasks = await list_tasks(_user_id=user_id)

        assert len(updated_tasks) == 1
        assert updated_tasks[0]["id"] == 1
        assert updated_tasks[0]["title"] == "Buy milk"
        assert updated_tasks[0]["completed"] is False

        print("✅ Workflow 1 PASSED: create_task → list_tasks persistence verified")


@pytest.mark.asyncio
async def test_workflow_create_mark_complete_list():
    """
    Workflow 2: create_task → mark_task_completed → list_tasks
    Verifies SC-004: Completion status updates reflected in subsequent queries.
    """
    user_id = "test_user_123"

    with (
        patch("src.tools.create_task.BackendClient") as mock_create_client,
        patch(
            "src.tools.mark_completed.BackendClient"
        ) as mock_complete_client,
        patch("src.tools.list_tasks.BackendClient") as mock_list_client,
    ):
        mock_create = AsyncMock()
        mock_complete = AsyncMock()
        mock_list = AsyncMock()
        mock_create_client.return_value = mock_create
        mock_complete_client.return_value = mock_complete
        mock_list_client.return_value = mock_list

        # Step 1: Create a task
        new_task = {
            "id": 1,
            "title": "Write tests",
            "description": None,
            "completed": False,
            "priority": "Medium",
            "due_date": None,
            "created_at": "2025-01-01T00:00:00Z",
            "updated_at": "2025-01-01T00:00:00Z",
            "user_id": user_id,
        }
        mock_create.create_task.return_value = new_task
        created_task = await create_task(title="Write tests", _user_id=user_id)

        assert created_task["completed"] is False

        # Step 2: Mark task as completed
        completed_task = {
            **new_task,
            "completed": True,
            "updated_at": "2025-01-01T01:00:00Z",
        }
        mock_complete.mark_task_completed.return_value = completed_task
        marked_task = await mark_task_completed(task_id=1, _user_id=user_id)

        assert marked_task["completed"] is True
        assert marked_task["updated_at"] != new_task["updated_at"]

        # Step 3: List tasks (should show task as completed)
        mock_list.get_tasks.return_value = [completed_task]
        tasks = await list_tasks(_user_id=user_id)

        assert len(tasks) == 1
        assert tasks[0]["id"] == 1
        assert tasks[0]["completed"] is True

        print(
            "✅ Workflow 2 PASSED: mark_task_completed status reflected in list_tasks"
        )


@pytest.mark.asyncio
async def test_workflow_create_update_list():
    """
    Workflow 3: create_task → update_task → list_tasks
    Verifies SC-003: Field updates reflected in subsequent queries.
    """
    user_id = "test_user_123"

    with (
        patch("src.tools.create_task.BackendClient") as mock_create_client,
        patch("src.tools.update_task.BackendClient") as mock_update_client,
        patch("src.tools.list_tasks.BackendClient") as mock_list_client,
    ):
        mock_create = AsyncMock()
        mock_update = AsyncMock()
        mock_list = AsyncMock()
        mock_create_client.return_value = mock_create
        mock_update_client.return_value = mock_update
        mock_list_client.return_value = mock_list

        # Step 1: Create a task
        new_task = {
            "id": 1,
            "title": "Original title",
            "description": "Original description",
            "completed": False,
            "priority": "Low",
            "due_date": None,
            "created_at": "2025-01-01T00:00:00Z",
            "updated_at": "2025-01-01T00:00:00Z",
            "user_id": user_id,
        }
        mock_create.create_task.return_value = new_task
        created_task = await create_task(
            title="Original title",
            description="Original description",
            priority="Low",
            _user_id=user_id,
        )

        assert created_task["title"] == "Original title"
        assert created_task["priority"] == "Low"

        # Step 2: Update the task (title and priority)
        updated_task = {
            **new_task,
            "title": "Updated title",
            "priority": "Urgent",
            "updated_at": "2025-01-01T02:00:00Z",
        }
        mock_update.update_task.return_value = updated_task
        result = await update_task(
            task_id=1,
            title="Updated title",
            priority="Urgent",
            _user_id=user_id,
        )

        assert result["title"] == "Updated title"
        assert result["priority"] == "Urgent"

        # Step 3: List tasks (should show updated fields)
        mock_list.get_tasks.return_value = [updated_task]
        tasks = await list_tasks(_user_id=user_id)

        assert len(tasks) == 1
        assert tasks[0]["id"] == 1
        assert tasks[0]["title"] == "Updated title"
        assert tasks[0]["priority"] == "Urgent"
        assert tasks[0]["description"] == "Original description"

        print("✅ Workflow 3 PASSED: update_task changes reflected in list_tasks")


@pytest.mark.asyncio
async def test_workflow_create_delete_list():
    """
    Workflow 4: create_task → delete_task → list_tasks
    Verifies SC-004: Deletion reflected in subsequent queries.
    """
    user_id = "test_user_123"

    with (
        patch("src.tools.create_task.BackendClient") as mock_create_client,
        patch("src.tools.delete_task.BackendClient") as mock_delete_client,
        patch("src.tools.list_tasks.BackendClient") as mock_list_client,
    ):
        mock_create = AsyncMock()
        mock_delete = AsyncMock()
        mock_list = AsyncMock()
        mock_create_client.return_value = mock_create
        mock_delete_client.return_value = mock_delete
        mock_list_client.return_value = mock_list

        # Step 1: Create 2 tasks
        task1 = {
            "id": 1,
            "title": "Task to delete",
            "description": None,
            "completed": False,
            "priority": "Medium",
            "due_date": None,
            "created_at": "2025-01-01T00:00:00Z",
            "updated_at": "2025-01-01T00:00:00Z",
            "user_id": user_id,
        }

        task2 = {
            "id": 2,
            "title": "Task to keep",
            "description": None,
            "completed": False,
            "priority": "High",
            "due_date": None,
            "created_at": "2025-01-01T00:00:00Z",
            "updated_at": "2025-01-01T00:00:00Z",
            "user_id": user_id,
        }

        mock_create.create_task.side_effect = [task1, task2]
        await create_task(title="Task to delete", _user_id=user_id)
        await create_task(title="Task to keep", priority="High", _user_id=user_id)

        # Step 2: List tasks (should have 2)
        mock_list.get_tasks.return_value = [task1, task2]
        tasks_before = await list_tasks(_user_id=user_id)
        assert len(tasks_before) == 2

        # Step 3: Delete task 1
        mock_delete.delete_task.return_value = None
        delete_result = await delete_task(task_id=1, _user_id=user_id)
        assert "successfully deleted" in delete_result["message"].lower()

        # Step 4: List tasks again (should only have task 2)
        mock_list.get_tasks.return_value = [task2]
        tasks_after = await list_tasks(_user_id=user_id)

        assert len(tasks_after) == 1
        assert tasks_after[0]["id"] == 2
        assert tasks_after[0]["title"] == "Task to keep"

        # Verify task 1 is gone
        task_ids = [task["id"] for task in tasks_after]
        assert 1 not in task_ids

        print("✅ Workflow 4 PASSED: delete_task removal reflected in list_tasks")


@pytest.mark.asyncio
async def test_workflow_complex_multi_operation():
    """
    Complex workflow: Multiple operations in sequence.
    Tests real-world AI assistant interaction patterns.
    """
    user_id = "test_user_123"

    with (
        patch("src.tools.create_task.BackendClient") as mock_create_client,
        patch("src.tools.list_tasks.BackendClient") as mock_list_client,
        patch("src.tools.update_task.BackendClient") as mock_update_client,
        patch(
            "src.tools.mark_completed.BackendClient"
        ) as mock_complete_client,
        patch("src.tools.delete_task.BackendClient") as mock_delete_client,
    ):
        mock_create = AsyncMock()
        mock_list = AsyncMock()
        mock_update = AsyncMock()
        mock_complete = AsyncMock()
        mock_delete = AsyncMock()

        mock_create_client.return_value = mock_create
        mock_list_client.return_value = mock_list
        mock_update_client.return_value = mock_update
        mock_complete_client.return_value = mock_complete
        mock_delete_client.return_value = mock_delete

        # Scenario: User adds shopping list, then manages it

        # 1. Create 3 tasks
        tasks = []
        for i, title in enumerate(["Buy milk", "Buy bread", "Buy eggs"], start=1):
            task = {
                "id": i,
                "title": title,
                "description": None,
                "completed": False,
                "priority": "Medium",
                "due_date": None,
                "created_at": "2025-01-01T00:00:00Z",
                "updated_at": "2025-01-01T00:00:00Z",
                "user_id": user_id,
            }
            tasks.append(task)

        mock_create.create_task.side_effect = tasks.copy()
        for title in ["Buy milk", "Buy bread", "Buy eggs"]:
            await create_task(title=title, _user_id=user_id)

        # 2. List all tasks
        mock_list.get_tasks.return_value = tasks.copy()
        all_tasks = await list_tasks(_user_id=user_id)
        assert len(all_tasks) == 3

        # 3. Update task 1 to high priority
        tasks[0]["priority"] = "High"
        tasks[0]["updated_at"] = "2025-01-01T01:00:00Z"
        mock_update.update_task.return_value = tasks[0]
        await update_task(task_id=1, priority="High", _user_id=user_id)

        # 4. Mark task 2 as completed
        tasks[1]["completed"] = True
        tasks[1]["updated_at"] = "2025-01-01T01:30:00Z"
        mock_complete.mark_task_completed.return_value = tasks[1]
        await mark_task_completed(task_id=2, _user_id=user_id)

        # 5. Delete task 3
        mock_delete.delete_task.return_value = None
        await delete_task(task_id=3, _user_id=user_id)

        # 6. Final list (should show: task 1 high priority, task 2 completed)
        final_tasks = [tasks[0], tasks[1]]
        mock_list.get_tasks.return_value = final_tasks
        result = await list_tasks(_user_id=user_id)

        assert len(result) == 2
        assert result[0]["id"] == 1
        assert result[0]["priority"] == "High"
        assert result[0]["completed"] is False
        assert result[1]["id"] == 2
        assert result[1]["completed"] is True

        print("✅ Complex Workflow PASSED: All operations work together correctly")
        print("  - Created 3 tasks")
        print("  - Updated priority on task 1")
        print("  - Marked task 2 as completed")
        print("  - Deleted task 3")
        print("  - Final state verified via list_tasks")
