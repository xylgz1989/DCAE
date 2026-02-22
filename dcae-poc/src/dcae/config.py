"""Configuration management for DCAE."""

import os
from pathlib import Path
from typing import Any, Dict, Optional

import yaml
from pydantic import BaseModel, Field


class LLMConfig(BaseModel):
    """LLM API configuration."""

    api_key: str
    base_url: str
    model: str


class ConsensusConfig(BaseModel):
    """Consensus configuration for an agent."""

    enabled: bool = False
    models: list[str] = []
    voting_strategy: str = "majority"  # unanimous, majority, weighted
    threshold: float = 0.5


class AgentConfig(BaseModel):
    """Agent configuration."""

    name: str
    role: str
    model: str
    consensus: ConsensusConfig = Field(default_factory=ConsensusConfig)
    skills: list[str] = Field(default_factory=list)


class SkillConfig(BaseModel):
    """Skill configuration."""

    mandatory_for: list[str] = Field(default_factory=list)
    description: str = ""


class StorageConfig(BaseModel):
    """Storage configuration."""

    type: str = "sqlite"
    path: str = "./dcae-poc.db"


class OutputConfig(BaseModel):
    """Output configuration."""

    artifacts_dir: str = "./artifacts"
    logs_dir: str = "./logs"


class DCAEConfig(BaseModel):
    """Main DCAE configuration."""

    project: Dict[str, Any] = Field(default_factory=dict)
    llm_config: Dict[str, LLMConfig] = Field(default_factory=dict)
    agents: Dict[str, AgentConfig] = Field(default_factory=dict)
    skills: Dict[str, SkillConfig] = Field(default_factory=dict)
    storage: StorageConfig = Field(default_factory=StorageConfig)
    output: OutputConfig = Field(default_factory=OutputConfig)
    consensus: Dict[str, Any] = Field(default_factory=dict)

    @classmethod
    def load(cls, config_path: Optional[Path] = None) -> "DCAEConfig":
        """Load configuration from YAML file.

        Args:
            config_path: Path to config file. Defaults to ./config.yaml

        Returns:
            DCAEConfig instance
        """
        if config_path is None:
            config_path = Path("./config.yaml")

        with open(config_path, "r", encoding="utf-8") as f:
            raw_config = yaml.safe_load(f)

        # Expand environment variables in API keys
        for provider, llm_cfg in raw_config.get("llm_config", {}).items():
            if isinstance(llm_cfg, dict):
                api_key = llm_cfg.get("api_key", "")
                if api_key and "${" in api_key:
                    env_var = api_key.split("${")[1].split("}")[0]
                    llm_cfg["api_key"] = os.getenv(env_var, "")

        return cls(**raw_config)
