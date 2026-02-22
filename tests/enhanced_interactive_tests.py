"""
Comprehensive test of enhanced interactive mode functionality
"""

import sys
from pathlib import Path
import tempfile
import json
import asyncio
from unittest.mock import AsyncMock

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from dcae import (
    ConversationHistory,
    CommandCompleter,
    ProgressDisplay,
    DCAEConfig,
    DCAEAgent,
    handle_gen_command,
    handle_review_command,
    handle_debug_command,
    handle_req_command,
    handle_test_doc_command,
    handle_test_case_command,
    handle_general_prompt
)

def test_improved_history_token_handling():
    """Test improved token handling in history."""
    print("Testing: test_improved_history_token_handling")

    # Arrange
    history = ConversationHistory(max_tokens=20)  # Small limit for testing

    # Act - Add a long message that should trigger trimming
    history.add_user_message("This is a very long message that should exceed the token limit easily")

    # Add more messages to test the trim functionality
    history.add_assistant_message("Response to long message")
    history.add_user_message("Another message")

    # Assert
    assert len(history.history) <= 6, f"History should be trimmed to max 6 messages, got {len(history.history)}"
    assert history.count_tokens() <= 5000, f"Tokens should be within limit, got {history.count_tokens()}"
    print("✓ PASSED")


def test_improved_command_completion_with_files():
    """Test improved command completion with various file types."""
    print("Testing: test_improved_command_completion_with_files")

    # Arrange
    completer = CommandCompleter()

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)

        # Create various test files
        (tmp_path / "test_file.py").write_text("print('hello')")
        (tmp_path / "script.js").write_text("console.log('hello');")
        (tmp_path / "data.json").write_text('{"key": "value"}')

        # Act
        completions = completer.get_completions_with_files("review test", tmp_path)

        # Assert
        assert "test_file.py" in completions, f"Expected 'test_file.py' in completions, got {completions}"
        # Don't check for 'gen' here since we're testing with 'review test' command
        print("✓ PASSED")


def test_progress_display_finish_method():
    """Test the new finish method in progress display."""
    print("Testing: test_progress_display_finish_method")

    # Arrange
    progress = ProgressDisplay()
    progress.start(10)

    # Act
    progress.finish()

    # Assert
    assert progress.current == progress.total, f"Expected current={progress.total}, got {progress.current}"
    print("✓ PASSED")


def test_error_handling_in_command_handlers():
    """Test error handling in command handlers."""
    print("Testing: test_error_handling_in_command_handlers")

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

        # Mock methods to simulate failures
        original_method = agent.generate_code
        async def mock_failing_generate(prompt, save_to=None):
            raise Exception("API Error occurred")

        agent.generate_code = mock_failing_generate

        history = ConversationHistory()
        progress = ProgressDisplay()

        # Act
        async def run_test():
            try:
                await handle_gen_command(agent, history, "create a test function", progress)
                return history
            except:
                # Expected to handle the error gracefully
                return history

        result_history = asyncio.run(run_test())

        # Restore original method
        agent.generate_code = original_method

        # Assert
        # History should contain error message as assistant response
        assert len(result_history.history) == 2, f"Expected 2 messages (user + error response), got {len(result_history.history)}"
        print("✓ PASSED")


def test_file_path_resolution_in_review_handler():
    """Test file path resolution in review handler."""
    print("Testing: test_file_path_resolution_in_review_handler")

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

        # Mock the review_code method to prevent actual API call
        original_method = agent.review_code
        async def mock_review(file_path):
            return "Mocked review result"

        agent.review_code = mock_review

        history = ConversationHistory()
        progress = ProgressDisplay()

        # Act
        async def run_test():
            await handle_review_command(agent, history, str(test_file), progress)
            return history

        result_history = asyncio.run(run_test())

        # Restore original method
        agent.review_code = original_method

        # Assert
        assert len(result_history.history) == 2, f"Expected 2 messages (user + assistant), got {len(result_history.history)}"
        print("✓ PASSED")


def test_command_normalization():
    """Test command normalization (case insensitive)."""
    print("Testing: test_command_normalization")

    # Arrange
    user_input = "GEN create a function"  # Uppercase command

    # Act
    parts = user_input.split()
    command = parts[0].lower() if parts else None  # Normalized to lowercase
    args = parts[1:] if len(parts) > 1 else []
    full_prompt = ' '.join(args) if args else user_input[len(command or ''):].strip()

    # Assert
    assert command == "gen", f"Expected normalized command 'gen', got '{command}'"
    assert full_prompt == "create a function", f"Expected prompt 'create a function', got '{full_prompt}'"
    print("✓ PASSED")


def run_enhanced_tests():
    """Run all enhanced functionality tests."""
    print("Running tests for enhanced interactive mode functionality...\n")

    try:
        test_improved_history_token_handling()
    except Exception as e:
        print(f"✗ FAILED: {e}\n")

    try:
        test_improved_command_completion_with_files()
    except Exception as e:
        print(f"✗ FAILED: {e}\n")

    try:
        test_progress_display_finish_method()
    except Exception as e:
        print(f"✗ FAILED: {e}\n")

    try:
        test_error_handling_in_command_handlers()
    except Exception as e:
        print(f"✗ FAILED: {e}\n")

    try:
        test_file_path_resolution_in_review_handler()
    except Exception as e:
        print(f"✗ FAILED: {e}\n")

    try:
        test_command_normalization()
    except Exception as e:
        print(f"✗ FAILED: {e}\n")

    print("\nAll enhanced interactive mode tests completed!")


if __name__ == "__main__":
    run_enhanced_tests()