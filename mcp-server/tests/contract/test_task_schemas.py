"""Contract tests for task schemas.

These tests validate that our Pydantic schemas correctly accept/reject data
according to the contract with the backend API.
"""

from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from src.schemas.task import (
    CreateTaskParams,
    DeleteTaskParams,
    MarkTaskCompletedParams,
    PriorityLevel,
    TaskResponse,
    UpdateTaskParams,
)


class TestTaskResponse:
    """Contract tests for TaskResponse schema."""

    def test_accepts_all_required_fields(self):
        """TaskResponse should accept valid data with all required fields."""
        data = {
            "id": 1,
            "title": "Test Task",
            "description": "A test task description",
            "completed": False,
            "priority": "Medium",
            "due_date": "2025-12-20T10:00:00Z",
            "created_at": "2025-12-18T10:00:00Z",
            "updated_at": "2025-12-18T10:00:00Z",
            "user_id": "user_123",
        }

        task = TaskResponse(**data)

        assert task.id == 1
        assert task.title == "Test Task"
        assert task.description == "A test task description"
        assert task.completed is False
        assert task.priority == PriorityLevel.MEDIUM
        assert task.user_id == "user_123"

    def test_accepts_optional_fields_as_none(self):
        """TaskResponse should accept None for optional fields."""
        data = {
            "id": 1,
            "title": "Test Task",
            "description": None,  # Optional
            "completed": False,
            "priority": "Medium",
            "due_date": None,  # Optional
            "created_at": "2025-12-18T10:00:00Z",
            "updated_at": "2025-12-18T10:00:00Z",
            "user_id": "user_123",
        }

        task = TaskResponse(**data)

        assert task.description is None
        assert task.due_date is None

    def test_title_max_length_validation(self):
        """TaskResponse should validate title max length (200 chars)."""
        data = {
            "id": 1,
            "title": "a" * 201,  # Exceeds max_length
            "completed": False,
            "priority": "Medium",
            "created_at": "2025-12-18T10:00:00Z",
            "updated_at": "2025-12-18T10:00:00Z",
            "user_id": "user_123",
        }

        with pytest.raises(ValidationError) as exc_info:
            TaskResponse(**data)

        errors = exc_info.value.errors()
        assert any(error["loc"] == ("title",) for error in errors)

    def test_validates_priority_enum_values(self):
        """TaskResponse should only accept valid PriorityLevel enum values."""
        data = {
            "id": 1,
            "title": "Test Task",
            "completed": False,
            "priority": "Invalid",  # Not a valid enum value
            "created_at": "2025-12-18T10:00:00Z",
            "updated_at": "2025-12-18T10:00:00Z",
            "user_id": "user_123",
        }

        with pytest.raises(ValidationError) as exc_info:
            TaskResponse(**data)

        errors = exc_info.value.errors()
        assert any(error["loc"] == ("priority",) for error in errors)

    def test_accepts_all_priority_levels(self):
        """TaskResponse should accept all valid PriorityLevel enum values."""
        base_data = {
            "id": 1,
            "title": "Test Task",
            "completed": False,
            "created_at": "2025-12-18T10:00:00Z",
            "updated_at": "2025-12-18T10:00:00Z",
            "user_id": "user_123",
        }

        for priority in ["Low", "Medium", "High", "Urgent"]:
            data = {**base_data, "priority": priority}
            task = TaskResponse(**data)
            assert task.priority.value == priority


class TestPriorityLevel:
    """Contract tests for PriorityLevel enum."""

    def test_has_all_required_levels(self):
        """PriorityLevel should have Low, Medium, High, Urgent."""
        assert PriorityLevel.LOW.value == "Low"
        assert PriorityLevel.MEDIUM.value == "Medium"
        assert PriorityLevel.HIGH.value == "High"
        assert PriorityLevel.URGENT.value == "Urgent"

    def test_enum_count(self):
        """PriorityLevel should have exactly 4 levels."""
        assert len(PriorityLevel) == 4


class TestCreateTaskParams:
    """Contract tests for CreateTaskParams schema."""

    def test_title_is_required(self):
        """CreateTaskParams should require title field."""
        data = {
            "description": "A description",
            "priority": "Medium",
        }

        with pytest.raises(ValidationError) as exc_info:
            CreateTaskParams(**data)

        errors = exc_info.value.errors()
        assert any(error["loc"] == ("title",) for error in errors)

    def test_title_min_length_validation(self):
        """CreateTaskParams should reject empty title."""
        data = {
            "title": "",  # Empty string
        }

        with pytest.raises(ValidationError) as exc_info:
            CreateTaskParams(**data)

        errors = exc_info.value.errors()
        assert any(error["loc"] == ("title",) for error in errors)

    def test_title_max_length_validation(self):
        """CreateTaskParams should validate title max length (200 chars)."""
        data = {
            "title": "a" * 201,  # Exceeds max_length
        }

        with pytest.raises(ValidationError) as exc_info:
            CreateTaskParams(**data)

        errors = exc_info.value.errors()
        assert any(error["loc"] == ("title",) for error in errors)

    def test_accepts_title_only_with_defaults(self):
        """CreateTaskParams should accept title only and apply defaults."""
        data = {
            "title": "Buy milk",
        }

        params = CreateTaskParams(**data)

        assert params.title == "Buy milk"
        assert params.description is None
        assert params.priority == PriorityLevel.MEDIUM  # Default
        assert params.due_date is None

    def test_accepts_all_optional_fields(self):
        """CreateTaskParams should accept all fields including optional ones."""
        data = {
            "title": "Buy milk",
            "description": "Get 2% milk from grocery store",
            "priority": "High",
            "due_date": "2025-12-20T10:00:00Z",
        }

        params = CreateTaskParams(**data)

        assert params.title == "Buy milk"
        assert params.description == "Get 2% milk from grocery store"
        assert params.priority == PriorityLevel.HIGH
        assert params.due_date is not None

    def test_rejects_invalid_priority(self):
        """CreateTaskParams should reject invalid priority values."""
        data = {
            "title": "Test Task",
            "priority": "SuperUrgent",  # Invalid priority
        }

        with pytest.raises(ValidationError) as exc_info:
            CreateTaskParams(**data)

        errors = exc_info.value.errors()
        assert any(error["loc"] == ("priority",) for error in errors)

    def test_rejects_invalid_due_date_format(self):
        """CreateTaskParams should reject invalid date formats."""
        data = {
            "title": "Test Task",
            "due_date": "not-a-date",
        }

        with pytest.raises(ValidationError) as exc_info:
            CreateTaskParams(**data)

        errors = exc_info.value.errors()
        assert any(error["loc"] == ("due_date",) for error in errors)

    def test_accepts_valid_iso_date(self):
        """CreateTaskParams should accept valid ISO 8601 date format."""
        data = {
            "title": "Test Task",
            "due_date": "2025-12-20T10:00:00Z",
        }

        params = CreateTaskParams(**data)

        assert params.due_date is not None
        assert isinstance(params.due_date, datetime)
