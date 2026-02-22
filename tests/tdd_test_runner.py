"""
Direct test of interactive mode functionality following TDD
"""

import sys
from pathlib import Path
import tempfile
import json

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

def test_history_initialization_with_defaults():
    """Test that history initializes with default limits."""
    print("Testing: test_history_initialization_with_defaults")

    # Arrange & Act
    history = ConversationHistory()

    # Assert
    assert isinstance(history.history, list), "History should be a list"
    assert len(history.history) == 0, "History should start empty"
    assert history.max_tokens == 5000, f"Expected max_tokens 5000, got {history.max_tokens}"
    assert history.max_messages == 6, f"Expected max_messages 6, got {history.max_messages}"
    print("✓ PASSED")

def test_add_user_message_adds_correctly():
    """Test adding a user message to history."""
    print("Testing: test_add_user_message_adds_correctly")

    # Arrange
    history = ConversationHistory()
    message = "Generate a function that sums two numbers"

    # Act
    history.add_user_message(message)

    # Assert
    assert len(history.history) == 1, f"Expected 1 message, got {len(history.history)}"
    assert history.history[0]["role"] == "user", f"Expected role 'user', got {history.history[0]['role']}"
    assert history.history[0]["content"] == message, f"Expected content '{message}', got {history.history[0]['content']}"
    print("✓ PASSED")

def test_add_assistant_message_adds_correctly():
    """Test adding an assistant message to history."""
    print("Testing: test_add_assistant_message_adds_correctly")

    # Arrange
    history = ConversationHistory()
    message = "Here's the function you requested..."

    # Act
    history.add_assistant_message(message)

    # Assert
    assert len(history.history) == 1, f"Expected 1 message, got {len(history.history)}"
    assert history.history[0]["role"] == "assistant", f"Expected role 'assistant', got {history.history[0]['role']}"
    assert history.history[0]["content"] == message, f"Expected content '{message}', got {history.history[0]['content']}"
    print("✓ PASSED")

def test_get_context_returns_full_history():
    """Test getting full conversation context."""
    print("Testing: test_get_context_returns_full_history")

    # Arrange
    history = ConversationHistory()
    history.add_user_message("Hello")
    history.add_assistant_message("Hi there")

    # Act
    context = history.get_context()

    # Assert
    assert len(context) == 2, f"Expected 2 messages in context, got {len(context)}"
    assert context[0]["role"] == "user", f"First message should be 'user', got {context[0]['role']}"
    assert context[1]["role"] == "assistant", f"Second message should be 'assistant', got {context[1]['role']}"
    print("✓ PASSED")

def test_clear_resets_history():
    """Test clearing conversation history."""
    print("Testing: test_clear_resets_history")

    # Arrange
    history = ConversationHistory()
    history.add_user_message("Test message")
    assert len(history.history) == 1, "History should have 1 message before clear"

    # Act
    history.clear()

    # Assert
    assert len(history.history) == 0, f"After clear, history should be empty, got {len(history.history)}"
    print("✓ PASSED")

def test_get_completions_for_partial_command():
    """Test getting completions for partial command."""
    print("Testing: test_get_completions_for_partial_command")

    # Arrange
    completer = CommandCompleter()

    # Act
    completions = completer.get_completions("gen")

    # Assert
    assert "gen" in completions, f"'gen' should be in completions, got {completions}"
    assert all(cmd.startswith("gen") for cmd in completions), f"All completions should start with 'gen'"
    print("✓ PASSED")

def test_progress_initialization():
    """Test progress display initializes with zero values."""
    print("Testing: test_progress_initialization")

    # Arrange & Act
    progress = ProgressDisplay()

    # Assert
    assert progress.current == 0, f"Expected current 0, got {progress.current}"
    assert progress.total == 100, f"Expected total 100, got {progress.total}"
    assert progress.start_time is None, f"Expected start_time None, got {progress.start_time}"
    print("✓ PASSED")

def test_command_handler_with_mock_config():
    """Test command handler with mocked config."""
    print("Testing: test_command_handler_with_mock_config")

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

        # Mock the generate_code method to avoid making actual API calls
        original_method = agent.generate_code
        async def mock_generate_code(prompt, save_to=None):
            return f"Mocked response for: {prompt}"

        agent.generate_code = mock_generate_code

        history = ConversationHistory()
        progress = ProgressDisplay()

        # Act
        import asyncio
        async def run_test():
            await handle_gen_command(agent, history, "create a test function", progress)
            return history

        result_history = asyncio.run(run_test())

        # Restore original method
        agent.generate_code = original_method

        # Assert
        assert len(result_history.history) == 2, f"Expected 2 messages in history (user + assistant), got {len(result_history.history)}"
        assert result_history.history[0]["role"] == "user", "First message should be from user"
        assert result_history.history[1]["role"] == "assistant", "Second message should be from assistant"
        print("✓ PASSED")

def run_all_tests():
    """Run all tests to verify they fail initially (as expected in TDD)."""
    print("Running TDD tests for interactive mode functionality...\n")

    try:
        test_history_initialization_with_defaults()
    except Exception as e:
        print(f"✗ FAILED: {e}\n")

    try:
        test_add_user_message_adds_correctly()
    except Exception as e:
        print(f"✗ FAILED: {e}\n")

    try:
        test_add_assistant_message_adds_correctly()
    except Exception as e:
        print(f"✗ FAILED: {e}\n")

    try:
        test_get_context_returns_full_history()
    except Exception as e:
        print(f"✗ FAILED: {e}\n")

    try:
        test_clear_resets_history()
    except Exception as e:
        print(f"✗ FAILED: {e}\n")

    try:
        test_get_completions_for_partial_command()
    except Exception as e:
        print(f"✗ FAILED: {e}\n")

    try:
        test_progress_initialization()
    except Exception as e:
        print(f"✗ FAILED: {e}\n")

    try:
        test_command_handler_with_mock_config()
    except Exception as e:
        print(f"✗ FAILED: {e}\n")

    print("\nNote: According to TDD, tests should fail initially before implementation.")

if __name__ == "__main__":
    run_all_tests()