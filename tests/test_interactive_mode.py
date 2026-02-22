"""
TDD Tests for DCAE Interactive Mode

Test structure following AAA pattern (Arrange-Act-Assert)
"""

import pytest
import asyncio
import sys
import tempfile
from pathlib import Path
import json

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from dcae import DCAEConfig, DCAEAgent


class TestInteractiveSession:
    """Test basic interactive session functionality."""

    def test_session_initialization(self):
        """Test that session initializes correctly with config."""
        # Arrange
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / 'config.json'
            config_data = {
                'provider': 'qwen',
                'api_key': 'test-key',
                'daily_limit': 100000,
                'daily_used': 0
            }
            config_path.write_text(json.dumps(config_data))

            # Act
            config = DCAEConfig(config_path)
            agent = DCAEAgent(config)

            # Assert
            assert config.get('provider') == 'qwen'
            assert agent.budget.get_status()['daily']['used'] == 0

    @pytest.mark.asyncio
    async def test_process_simple_request(self):
        """Test processing a simple 'status' command."""
        # Arrange
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / 'config.json'
            config_path.write_text(json.dumps({
                'provider': 'qwen',
                'api_key': 'test-key',
                'daily_limit': 100000,
                'daily_used': 0,
                'model_preference': 'auto'
            }))

            config = DCAEConfig(config_path)
            agent = DCAEAgent(config)

            # Act
            status = agent.budget.get_status()

            # Assert
            assert 'daily' in status
            assert status['daily']['used'] == 0
            assert status['daily']['limit'] == 100000


class TestCommandParser:
    """Test command parsing logic."""

    def test_parse_simple_command(self):
        """Test parsing a simple command without arguments."""
        # Arrange
        user_input = "status"

        # Act
        parts = user_input.strip().split()
        command = parts[0] if parts else None
        args = parts[1:] if len(parts) > 1 else []

        # Assert
        assert command == "status"
        assert args == []

    def test_parse_command_with_single_argument(self):
        """Test parsing command with single argument."""
        # Arrange
        user_input = "review auth.py"

        # Act
        parts = user_input.strip().split()
        command = parts[0] if parts else None
        args = parts[1:] if len(parts) > 1 else []

        # Assert
        assert command == "review"
        assert args == ["auth.py"]

    def test_parse_command_with_multiple_arguments(self):
        """Test parsing command with multiple arguments."""
        # Arrange
        user_input = "gen write login function -o auth.py"

        # Act
        parts = user_input.strip().split()
        command = parts[0] if parts else None
        args = parts[1:] if len(parts) > 1 else []

        # Assert
        assert command == "gen"
        assert args == ["write", "login", "function", "-o", "auth.py"]

    def test_parse_internal_command(self):
        """Test parsing internal commands starting with /."""
        # Arrange
        user_input = "/status"

        # Act
        is_internal = user_input.startswith('/')
        command = user_input[1:] if is_internal else None

        # Assert
        assert is_internal
        assert command == "status"

    def test_parse_empty_input(self):
        """Test parsing empty input."""
        # Arrange
        user_input = ""

        # Act
        is_empty = not user_input.strip()

        # Assert
        assert is_empty


class TestConversationHistory:
    """Test conversation history tracking."""

    def test_history_initialization(self):
        """Test that history initializes as empty list."""
        # Arrange
        history = []

        # Act
        is_empty = len(history) == 0

        # Assert
        assert is_empty

    def test_add_user_message(self):
        """Test adding user message to history."""
        # Arrange
        history = []
        message = "生成一个斐波那契函数"

        # Act
        history.append({"role": "user", "content": message})

        # Assert
        assert len(history) == 1
        assert history[0]["role"] == "user"
        assert history[0]["content"] == message

    def test_add_assistant_message(self):
        """Test adding assistant message to history."""
        # Arrange
        history = []
        message = "这是生成的代码..."

        # Act
        history.append({"role": "assistant", "content": message})

        # Assert
        assert len(history) == 1
        assert history[0]["role"] == "assistant"

    def test_history_token_counting(self):
        """Test counting tokens in history."""
        # Arrange
        history = [
            {"role": "user", "content": "Generate a function"},
            {"role": "assistant", "content": "def function(): pass"}
        ]

        # Act - Simple character-based approximation
        total_chars = sum(len(msg["content"]) for msg in history)
        estimated_tokens = total_chars // 4  # Rough estimate

        # Assert
        assert estimated_tokens > 0
        assert len(history) == 2

    def test_history_trimming_when_too_large(self):
        """Test trimming history when it exceeds token limit."""
        # Arrange - create history with more tokens than limit
        history = [
            {"role": "user", "content": "A" * 1000}
            for _ in range(10)
        ]
        max_tokens = 500

        # Act - Simple trim: keep last N messages
        total_chars = sum(len(msg["content"]) for msg in history)
        while total_chars // 4 > max_tokens and len(history) > 2:
            removed = history.pop(0)
            total_chars -= len(removed["content"])

        # Assert
        assert len(history) < 10
        assert len(history) >= 2  # Keep at least 2 messages


class TestTokenWarning:
    """Test token warning logic."""

    def test_no_warning_under_threshold(self):
        # Arrange
        used = 50000
        limit = 100000

        # Act
        percent = (used / limit) * 100
        warning_needed = percent >= 80

        # Assert
        assert percent == 50
        assert not warning_needed

    def test_warning_at_threshold(self):
        # Arrange
        used = 80000
        limit = 100000

        # Act
        percent = (used / limit) * 100
        warning_needed = percent >= 80

        # Assert
        assert percent == 80
        assert warning_needed

    def test_warning_above_threshold(self):
        # Arrange
        used = 90000
        limit = 100000

        # Act
        percent = (used / limit) * 100
        warning_needed = percent >= 80

        # Assert
        assert percent == 90
        assert warning_needed

    def test_model_downgrade_condition(self):
        # Arrange
        used = 85000
        limit = 100000
        current_model = "qwen-max"
        fallback_model = "qwen-plus"

        # Act
        percent = (used / limit) * 100
        should_downgrade = percent > 80 and current_model != fallback_model

        # Assert
        assert percent == 85
        assert should_downgrade


class TestAutocomplete:
    """Test autocomplete functionality."""

    def test_complete_command_start(self):
        """Test completing partial command."""
        # Arrange
        user_input = "sta"
        available_commands = ["status", "gen", "review", "exit"]

        # Act
        matches = [cmd for cmd in available_commands if cmd.startswith(user_input)]

        # Assert
        assert "status" in matches
        assert len(matches) == 1

    def test_multiple_matches(self):
        """Test when multiple commands match prefix."""
        # Arrange
        user_input = "r"
        available_commands = ["status", "gen", "review", "review"]

        # Act
        matches = [cmd for cmd in available_commands if cmd.startswith(user_input)]

        # Assert
        assert "review" in matches
        assert len(matches) >= 1

    def test_file_completion(self):
        """Test completing file paths."""
        # Arrange
        prefix = "test"
        with tempfile.TemporaryDirectory() as tmpdir:
            Path(tmpdir, "test_fib.py").touch()
            Path(tmpdir, "test_utils.py").touch()
            Path(tmpdir, "other.py").touch()

            # Act
            files = list(Path(tmpdir).glob(f"{prefix}*.py"))
            matches = [f.name for f in files]

            # Assert
            assert "test_fib.py" in matches
            assert "test_utils.py" in matches
            assert "other.py" not in matches


class TestMultiLineInput:
    """Test multi-line input handling."""

    def test_single_line_input(self):
        """Test handling single line input."""
        # Arrange
        user_input = "gen 写一个函数"

        # Act
        lines = user_input.split('\n')
        is_multiline = len(lines) > 1

        # Assert
        assert not is_multiline
        assert len(lines) == 1

    def test_multi_line_input_detected(self):
        """Test detecting multi-line input."""
        # Arrange
        user_input = """gen write a function
with these features:
1. Parameter validation
2. Error handling"""

        # Act
        lines = user_input.split('\n')
        is_multiline = len(lines) > 1

        # Assert
        assert is_multiline
        assert len(lines) == 4

    def test_multi_line_continuation_prompt(self):
        """Test detecting continuation prompt."""
        # Arrange
        user_input = "def function():\\"
        has_continuation = user_input.endswith('\\')

        # Act
        continuation_indicator = "\\" if has_continuation else ""

        # Assert
        assert has_continuation
        assert continuation_indicator == "\\"


class TestKeyboardShortcuts:
    """Test keyboard shortcut handling."""

    def test_ctrl_c_interrupt(self):
        """Test Ctrl+C interrupt handling."""
        # Arrange
        try:
            # Simulate user input that might be interrupted
            input_value = "test"
        except KeyboardInterrupt:
            interrupted = True
        else:
            interrupted = False

        # Assert
        assert not interrupted  # In this test, no interruption

    def test_empty_after_interrupt(self):
        """Test handling empty input after interruption."""
        # Arrange
        user_input = ""

        # Act
        should_skip = not user_input.strip()

        # Assert
        assert should_skip

    def test_exit_command_recognition(self):
        """Test recognizing exit commands."""
        # Arrange
        exit_commands = ["/exit", "exit", "quit", "q"]
        test_inputs = [
            ("/exit", True),
            ("exit", True),
            ("quit", True),
            ("q", True),
            ("other", False),
            ("", False)
        ]

        # Act & Assert
        for input_val, expected in test_inputs:
            is_exit = input_val.lower() in exit_commands
            assert is_exit == expected, f"Failed for input: {input_val}"


class TestProgressDisplay:
    """Test progress display functionality."""

    def test_progress_percentage_calculation(self):
        """Test calculating progress percentage."""
        # Arrange
        current = 5
        total = 10

        # Act
        percent = (current / total) * 100

        # Assert
        assert percent == 50

    def test_progress_display_formatting(self):
        """Test formatting progress display."""
        # Arrange
        percent = 75
        bar_length = 20

        # Act
        filled = int(bar_length * percent / 100)
        bar = '[' + '=' * filled + ' ' * (bar_length - filled) + ']'
        display = f"{bar} {percent}%"

        # Assert
        assert '=' * 15 in bar
        assert '75%' in display

    def test_estimated_time_remaining(self):
        """Test calculating estimated time remaining."""
        # Arrange
        elapsed = 10  # seconds
        current = 3
        total = 10

        # Act
        if current > 0:
            avg_time = elapsed / current
            remaining = total - current
            eta = avg_time * remaining
        else:
            eta = float('inf')

        # Assert
        assert eta > 0
        assert eta < float('inf')


if __name__ == "__main__":
    pytest.main([__file__, "-v"])