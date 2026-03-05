#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test script for the review rules functionality."""

import asyncio
from pathlib import Path
import tempfile

def create_sample_code_file():
    """Create a sample code file for testing."""
    content = '''
def calculate_sum(a, b):
    """Calculate the sum of two numbers."""
    return a + b


def login(username, password):
    """User login function."""
    # Hardcoded credentials - this might trigger security rules
    if username == "admin" and password == "password123":
        return True
    return False


class UserManager:
    """Manages user accounts."""

    def __init__(self):
        self.users = []

    def add_user(self, username):
        """Add a new user."""
        self.users.append(username)
        return len(self.users)
'''
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(content)
        return Path(f.name)


async def test_review_rules():
    """Test the review rules functionality."""
    from dcae import DCAEConfig, DCAEAgent

    # Create a sample code file
    sample_file = create_sample_code_file()
    print(f"Created sample file: {sample_file}")

    # Create config (we'll use a minimal config for this test)
    config_path = Path.home() / '.dcae' / 'config_test.json'
    config = DCAEConfig(config_path)

    # Just make sure the config exists so the agent can be created
    if not config_path.exists():
        config.set('provider', 'qwen')
        config.set('api_key', 'dummy-key-for-test')
        config.set('daily_limit', 100000)
        config.set('monthly_limit', 2000000)

    # Create agent
    agent = DCAEAgent(config)

    # Manually load the review engine for testing
    if agent.load_review_rules_engine():
        print("✅ Review Rules Engine loaded successfully")

        # Apply review rules to the sample file
        result = await agent.apply_review_rules(sample_file)
        print("\nReview Rules Results:")
        print("="*50)
        print(result)
        print("="*50)
    else:
        print("❌ Failed to load Review Rules Engine")

    # Clean up
    if sample_file.exists():
        sample_file.unlink()
        print(f"\nCleaned up sample file: {sample_file}")


if __name__ == "__main__":
    asyncio.run(test_review_rules())