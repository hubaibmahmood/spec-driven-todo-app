"""Unit tests for validation functions."""
import pytest

from src.cli.validators import validate_description, validate_title


def test_validate_title_with_valid_input_returns_unchanged() -> None:
    """Valid input returns unchanged."""
    # Mock confirm_truncation function for tests that don't need truncation
    from unittest.mock import Mock
    confirm_func = Mock()

    result = validate_title("Valid title", confirm_func)
    assert result == "Valid title"


def test_validate_title_with_empty_input_raises_validation_error() -> None:
    """Empty input raises ValidationError."""
    from src.cli.exceptions import ValidationError
    from unittest.mock import Mock

    confirm_func = Mock()

    with pytest.raises(ValidationError, match="Title cannot be empty"):
        validate_title("", confirm_func)


def test_validate_title_with_whitespace_only_raises_validation_error() -> None:
    """Whitespace-only input raises ValidationError."""
    from src.cli.exceptions import ValidationError
    from unittest.mock import Mock

    confirm_func = Mock()

    with pytest.raises(ValidationError, match="Title cannot be empty"):
        validate_title("   ", confirm_func)


def test_validate_title_with_200_chars_returns_unchanged() -> None:
    """200-character title returns unchanged."""
    from unittest.mock import Mock
    confirm_func = Mock()

    title_200 = "x" * 200
    result = validate_title(title_200, confirm_func)
    assert result == title_200


def test_validate_title_with_201_chars_prompts_and_truncates_if_confirmed() -> None:
    """201-character title prompts and truncates if confirmed."""
    from unittest.mock import Mock

    # This test requires a confirmation callback
    title_201 = "x" * 201
    confirm_func = Mock(return_value=True)  # User confirms truncation

    result = validate_title(title_201, confirm_func)
    assert result == title_201[:200]


def test_validate_title_with_201_chars_raises_if_user_declines() -> None:
    """201-character title raises if user declines."""
    from src.cli.exceptions import ValidationError
    from unittest.mock import Mock

    title_201 = "x" * 201
    confirm_func = Mock(return_value=False)  # User declines truncation

    with pytest.raises(ValidationError, match="Title too long and user declined truncation"):
        validate_title(title_201, confirm_func)


def test_validate_description_with_none_returns_none() -> None:
    """None input returns None."""
    from unittest.mock import Mock
    confirm_func = Mock()

    result = validate_description(None, confirm_func)
    assert result is None


def test_validate_description_with_empty_returns_none() -> None:
    """Empty input returns None."""
    from unittest.mock import Mock
    confirm_func = Mock()

    result = validate_description("", confirm_func)
    assert result is None


def test_validate_description_with_whitespace_only_returns_none() -> None:
    """Whitespace-only input returns None."""
    from unittest.mock import Mock
    confirm_func = Mock()

    result = validate_description("   ", confirm_func)
    assert result is None


def test_validate_description_with_1000_chars_returns_unchanged() -> None:
    """1000-character description returns unchanged."""
    from unittest.mock import Mock
    confirm_func = Mock()

    desc_1000 = "x" * 1000
    result = validate_description(desc_1000, confirm_func)
    assert result == desc_1000


def test_validate_description_with_1001_chars_prompts_and_truncates_if_confirmed() -> None:
    """1001-character description prompts and truncates if confirmed."""
    from unittest.mock import Mock

    # This test requires a confirmation callback
    desc_1001 = "x" * 1001
    confirm_func = Mock(return_value=True)  # User confirms truncation

    result = validate_description(desc_1001, confirm_func)
    assert result == desc_1001[:1000]


def test_validate_description_with_1001_chars_raises_if_user_declines() -> None:
    """1001-character description raises if user declines."""
    from src.cli.exceptions import ValidationError
    from unittest.mock import Mock

    desc_1001 = "x" * 1001
    confirm_func = Mock(return_value=False)  # User declines truncation

    with pytest.raises(ValidationError, match="Description too long and user declined truncation"):
        validate_description(desc_1001, confirm_func)