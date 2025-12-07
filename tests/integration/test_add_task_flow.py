"""Integration tests for interactive add task flow."""
from io import StringIO
from unittest.mock import patch
import pytest


def test_add_task_with_title_only_succeeds(monkeypatch, capsys) -> None:
    """Add task with title only succeeds in interactive mode."""
    # Simulate user input: add command with title, then quit
    inputs = iter(['add Test task title', 'quit'])

    def mock_input(prompt):
        return next(inputs)

    with patch('builtins.input', side_effect=mock_input):
        from src.cli.main import main
        exit_code = main()

    # Capture the output
    captured = capsys.readouterr()
    output = captured.out

    # Check that the success message is in the output
    assert "Task created successfully" in output
    assert "ID:" in output


def test_add_task_with_empty_title_shows_error(monkeypatch, capsys) -> None:
    """Add task with empty title shows error in interactive mode."""
    # Simulate user input: add command with empty title, then quit
    inputs = iter(['add', 'quit'])  # 'add' without title

    def mock_input(prompt):
        return next(inputs)

    with patch('builtins.input', side_effect=mock_input):
        from src.cli.main import main
        exit_code = main()

    # Capture the output
    captured = capsys.readouterr()
    output = captured.out

    # Check that the error message is in the output
    assert "Error" in output or "error" in output


def test_multiple_tasks_receive_sequential_ids(monkeypatch, capsys) -> None:
    """Multiple tasks receive sequential IDs in interactive mode."""
    # Simulate user input: add first task, add second task, then quit
    inputs = iter(['add First task', 'add Second task', 'quit'])

    def mock_input(prompt):
        return next(inputs)

    with patch('builtins.input', side_effect=mock_input):
        from src.cli.main import main
        exit_code = main()

    # Capture the output
    captured = capsys.readouterr()
    output = captured.out

    # Check that both tasks get sequential IDs (ID: 1 and ID: 2)
    assert "ID: 1" in output
    assert "ID: 2" in output


def test_add_task_with_title_and_description_succeeds(monkeypatch, capsys) -> None:
    """Add task with title and description succeeds in interactive mode."""
    # Simulate user input: add command with title and description, then quit
    inputs = iter(['add Test task title -d Test description', 'quit'])

    def mock_input(prompt):
        return next(inputs)

    with patch('builtins.input', side_effect=mock_input):
        from src.cli.main import main
        exit_code = main()

    # Capture the output
    captured = capsys.readouterr()
    output = captured.out

    # Check that the success message is in the output and description is shown
    assert "Task created successfully" in output
    assert "ID:" in output
    assert "Description: Test description" in output


def test_add_task_with_title_only_succeeds_no_description_shown(monkeypatch, capsys) -> None:
    """Add task with title only succeeds and no description shown in interactive mode."""
    # Simulate user input: add command with title only, then quit
    inputs = iter(['add Test task title', 'quit'])

    def mock_input(prompt):
        return next(inputs)

    with patch('builtins.input', side_effect=mock_input):
        from src.cli.main import main
        exit_code = main()

    # Capture the output
    captured = capsys.readouterr()
    output = captured.out

    # Check that the success message is in the output but no description line
    assert "Task created successfully" in output
    assert "ID:" in output
    assert "Description:" not in output