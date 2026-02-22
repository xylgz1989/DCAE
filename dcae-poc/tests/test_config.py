"""Test configuration management."""

import pytest
from pathlib import Path
from dcae.config import DCAEConfig, AgentConfig, ConsensusConfig


def test_load_config():
    """Test loading configuration from YAML file."""
    config = DCAEConfig.load(Path("./config.yaml"))

    assert config.project["name"] == "DCAE POC"
    assert "pm" in config.agents
    assert "architect" in config.agents
    assert "developer" in config.agents


def test_agent_config_consensus():
    """Test agent consensus configuration."""
    config = DCAEConfig.load(Path("./config.yaml"))

    pm_config = config.agents["pm"]
    assert pm_config.consensus.enabled is False

    architect_config = config.agents["architect"]
    assert architect_config.consensus.enabled is True
    assert architect_config.consensus.voting_strategy == "unanimous"
    assert architect_config.consensus.threshold == 1.0


def test_llm_config():
    """Test LLM configuration."""
    config = DCAEConfig.load(Path("./config.yaml"))

    assert "claude" in config.llm_config
    assert "openai" in config.llm_config
