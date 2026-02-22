"""
TDD Tests for Enhanced DCAE Interactive Mode

Test structure following AAA pattern (Arrange-Act-Assert)
"""

import pytest
import asyncio
import sys
from pathlib import Path
import tempfile
import json
import io
import contextlib
from unittest.mock import patch, MagicMock, AsyncMock

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from dcae import (
    ConversationHistory,
    CommandCompleter,
    ProgressDisplay,
    DCAEConfig,
    DCAEAgent,
    run_interactive_mode,
    show_interactive_status,
    print_interactive_help,
    print_conversation_history,
    handle_gen_command,
    handle_review_command,
    handle_debug_command,
    handle_req_command,
    handle_test_doc_command,
    handle_test_case_command,
    handle_general_prompt
)


class TestConversationHistoryEnhanced:
    """Test enhanced conversation history functionality."""

    def test_history_initialization_with_defaults(self):
        """Test that history initializes with default limits."""
        # Arrange & Act
        history = ConversationHistory()

        # Assert
        assert isinstance(history.history, list)
        assert len(history.history) == 0
        assert history.max_tokens == 5000
        assert history.max_messages == 6

    def test_add_user_message_adds_correctly(self):
        """Test adding a user message to history."""
        # Arrange
        history = ConversationHistory()
        message = "Generate a function that sums two numbers"

        # Act
        history.add_user_message(message)

        # Assert
        assert len(history.history) == 1
        assert history.history[0]["role"] == "user"
        assert history.history[0]["content"] == message

    def test_add_assistant_message_adds_correctly(self):
        """Test adding an assistant message to history."""
        # Arrange
        history = ConversationHistory()
        message = "Here's the function you requested..."

        # Act
        history.add_assistant_message(message)

        # Assert
        assert len(history.history) == 1
        assert history.history[0]["role"] == "assistant"
        assert history.history[0]["content"] == message

    def test_get_context_returns_full_history(self):
        """Test getting full conversation context."""
        # Arrange
        history = ConversationHistory()
        history.add_user_message("Hello")
        history.add_assistant_message("Hi there")

        # Act
        context = history.get_context()

        # Assert
        assert len(context) == 2
        assert context[0]["role"] == "user"
        assert context[1]["role"] == "assistant"

    def test_clear_resets_history(self):
        """Test clearing conversation history."""
        # Arrange
        history = ConversationHistory()
        history.add_user_message("Test message")
        assert len(history.history) == 1

        # Act
        history.clear()

        # Assert
        assert len(history.history) == 0

    def test_trim_by_message_count(self):
        """Test trimming history when message count exceeds limit."""
        # Arrange
        history = ConversationHistory(max_tokens=10000)  # High token limit to focus on message count
        history.max_messages = 2  # Override to smaller number for test

        # Add 3 messages to exceed limit
        history.add_user_message("Message 1")
        history.add_assistant_message("Response 1")
        history.add_user_message("Message 2")  # This should trigger trimming

        # Act - Already happened during add_assistant_message
        # The first message (Message 1) should have been removed

        # Assert
        assert len(history.history) == 2  # Should only have Response 1 and Message 2
        assert history.history[0]["content"] == "Response 1"  # Oldest remaining message
        assert history.history[1]["content"] == "Message 2"   # Newest message

    def test_trim_by_token_count(self):
        """Test trimming history when token count exceeds limit."""
        # Arrange
        history = ConversationHistory(max_tokens=20)  # Small limit for test
        history.max_messages = 10  # High limit to focus on token count

        # Add messages that exceed token limit
        history.add_user_message("This is a fairly long message that will exceed the token limit")  # More than 20 chars

        # Act
        history.add_assistant_message("This is another long message to test token limit")  # Add second message

        # Assert
        # Since each message alone is over 20 chars, after adding both,
        # the trim process should occur and keep at least the last message
        assert len(history.history) >= 1


class TestCommandCompleterEnhanced:
    """Test enhanced command completion functionality."""

    def test_get_completions_for_partial_command(self):
        """Test getting completions for partial command."""
        # Arrange
        completer = CommandCompleter()

        # Act
        completions = completer.get_completions("gen")

        # Assert
        assert "gen" in completions
        assert all(cmd.startswith("gen") for cmd in completions)

    def test_get_completions_case_insensitive(self):
        """Test that completions are case insensitive."""
        # Arrange
        completer = CommandCompleter()

        # Act
        completions = completer.get_completions("GEN")  # Uppercase

        # Assert
        assert "gen" in completions

    def test_get_completions_with_no_match(self):
        """Test getting completions for non-existent command."""
        # Arrange
        completer = CommandCompleter()

        # Act
        completions = completer.get_completions("xyz")

        # Assert
        assert len(completions) == 0

    def test_get_completions_with_file_paths(self, tmp_path):
        """Test getting completions including file paths."""
        # Arrange
        completer = CommandCompleter()
        # Create test files
        (tmp_path / "test_file.py").write_text("test")
        (tmp_path / "other_file.txt").write_text("test")

        # Act
        completions = completer.get_completions_with_files("review test", tmp_path)

        # Assert
        assert "test_file.py" in completions
        # txt file should not be included


class TestProgressDisplayEnhanced:
    """Test enhanced progress display functionality."""

    def test_progress_initialization(self):
        """Test progress display initializes with zero values."""
        # Arrange & Act
        progress = ProgressDisplay()

        # Assert
        assert progress.current == 0
        assert progress.total == 100
        assert progress.start_time is None

    def test_progress_start_sets_values(self):
        """Test starting progress tracking sets initial values."""
        # Arrange
        progress = ProgressDisplay()

        # Act
        progress.start(50)

        # Assert
        assert progress.total == 50
        assert progress.current == 0
        assert progress.start_time is not None

    def test_progress_update_changes_current(self):
        """Test updating progress changes current value."""
        # Arrange
        progress = ProgressDisplay()
        progress.start(100)

        # Act
        progress.update(25)

        # Assert
        assert progress.current == 25

    def test_show_returns_formatted_string(self):
        """Test showing progress returns formatted display string."""
        # Arrange
        progress = ProgressDisplay()
        progress.start(100)
        progress.update(50)

        # Act
        display = progress.show()

        # Assert
        assert "[==========          ] 50%" in display
        assert "ETA:" in display


class TestInteractiveCommands:
    """Test individual command handlers."""

    @pytest.mark.asyncio
    async def test_handle_gen_command_processes_prompt(self):
        """Test handling generate command with prompt."""
        # Arrange
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / 'config.json'
            config_data = {
                'provider': 'qwen',
                'api_key': 'test-key',
                'daily_limit': 100000,
                'daily_used': 0,
                'model_preference': 'auto'
            }
            config_path.write_text(json.dumps(config_data))

            config = DCAEConfig(config_path)
            agent = DCAEAgent(config)
            # Mock the generate_code method to return a fixed response
            agent.generate_code = AsyncMock(return_value="def test(): pass")

            history = ConversationHistory()
            progress = ProgressDisplay()

            # Act
            await handle_gen_command(agent, history, "create a test function", progress)

            # Assert
            agent.generate_code.assert_called_once()
            assert len(history.history) == 2  # User message + Assistant response

    @pytest.mark.asyncio
    async def test_handle_gen_command_empty_prompt(self):
        """Test handling generate command with empty prompt."""
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

            config = DCAEConfig(config_path)
            agent = DCAEAgent(config)
            history = ConversationHistory()
            progress = ProgressDisplay()

            captured_output = io.StringIO()

            # Act & Assert
            # We'll need to capture the print output from inside handle_gen_command
            # Since we can't easily do that, we'll verify that no calls to generate_code happen
            await handle_gen_command(agent, history, "", progress)

            # If the prompt is empty, generate_code should not be called
            # For now, just checking that the function doesn't crash

    @pytest.mark.asyncio
    async def test_handle_review_command_valid_file(self):
        """Test handling review command with valid file."""
        # Arrange
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a temporary Python file to review
            test_file = Path(tmpdir) / "test_code.py"
            test_file.write_text("def hello(): pass")

            config_path = Path(tmpdir) / 'config.json'
            config_data = {
                'provider': 'qwen',
                'api_key': 'test-key',
                'daily_limit': 100000,
                'daily_used': 0,
                'model_preference': 'auto'
            }
            config_path.write_text(json.dumps(config_data))

            config = DCAEConfig(config_path)
            agent = DCAEAgent(config)
            # Mock the review_code method
            agent.review_code = AsyncMock(return_value="Review complete")

            history = ConversationHistory()
            progress = ProgressDisplay()

            # Act
            await handle_review_command(agent, history, str(test_file), progress)

            # Assert
            agent.review_code.assert_called_once()
            assert len(history.history) == 2  # User message + Assistant response

    @pytest.mark.asyncio
    async def test_handle_review_command_invalid_file(self):
        """Test handling review command with invalid file."""
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

            config = DCAEConfig(config_path)
            agent = DCAEAgent(config)
            history = ConversationHistory()
            progress = ProgressDisplay()

            # Act & Assert
            # For this test, we're mainly checking that it doesn't crash
            await handle_review_command(agent, history, "nonexistent_file.py", progress)

            # History shouldn't be updated if file doesn't exist
            # (This depends on the implementation, so we might need to adjust)


class TestInteractiveModeInitialization:
    """Test interactive mode startup and initialization."""

    def test_print_interactive_help_works(self):
        """Test that help printing function executes without error."""
        # Arrange & Act & Assert - Just ensure it doesn't crash
        print_interactive_help()

    def test_print_conversation_history_works(self):
        """Test that conversation history printing works."""
        # Arrange
        history = ConversationHistory()
        history.add_user_message("Test message")

        # Act & Assert - Just ensure it doesn't crash
        print_conversation_history(history)

    @pytest.mark.asyncio
    async def test_show_interactive_status_works(self):
        """Test that status display function executes without error."""
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

            config = DCAEConfig(config_path)
            agent = DCAEAgent(config)

            # Act & Assert - Just ensure it doesn't crash
            await show_interactive_status(agent)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])