"""Module for managing LLM provider configurations."""
from dataclasses import dataclass
from enum import Enum
from typing import Optional, Dict, Any


class ProviderType(Enum):
    """Enum representing different LLM provider types."""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    BIGMODEL = "bigmodel"  # For Qwen models from Alibaba Cloud
    BAI_LIAN = "bailian"  # Alibaba Bailian platform
    GOOGLE = "google"
    COHERE = "cohere"
    CUSTOM = "custom"


@dataclass
class ProviderConfig:
    """Configuration for an LLM provider."""

    provider_type: ProviderType
    api_key: str
    name: str  # Unique identifier for this configuration
    base_url: Optional[str] = None
    model: Optional[str] = None
    timeout: int = 30
    max_retries: int = 3
    temperature: float = 0.7
    max_tokens: Optional[int] = None

    def __post_init__(self):
        """Set default values for base_url and model based on provider type."""
        if self.base_url is None:
            self.base_url = self._get_default_base_url()

        if self.model is None:
            self.model = self._get_default_model()

    def _get_default_base_url(self) -> str:
        """Get default base URL based on provider type."""
        defaults = {
            ProviderType.OPENAI: "https://api.openai.com/v1",
            ProviderType.ANTHROPIC: "https://api.anthropic.com/v1",
            ProviderType.BIGMODEL: "https://dashscope.aliyuncs.com/api/v1",
            ProviderType.BAI_LIAN: "https://bailian.aliyuncs.com/v1",
            ProviderType.GOOGLE: "https://generativelanguage.googleapis.com/v1beta",
            ProviderType.COHERE: "https://api.cohere.ai/v1",
            ProviderType.CUSTOM: "http://localhost:8000/v1"
        }
        return defaults.get(self.provider_type, "https://api.openai.com/v1")

    def _get_default_model(self) -> str:
        """Get default model based on provider type."""
        defaults = {
            ProviderType.OPENAI: "gpt-4o",
            ProviderType.ANTHROPIC: "claude-3-5-sonnet-20241022",
            ProviderType.BIGMODEL: "qwen-max",
            ProviderType.BAI_LIAN: "bailian-v1",
            ProviderType.GOOGLE: "gemini-1.5-pro",
            ProviderType.COHERE: "command-r-plus",
            ProviderType.CUSTOM: "custom-model"
        }
        return defaults.get(self.provider_type, "gpt-4o")

    def to_dict(self) -> Dict[str, Any]:
        """Convert ProviderConfig to dictionary representation."""
        return {
            'provider_type': self.provider_type.value,
            'api_key': self.api_key,
            'name': self.name,
            'base_url': self.base_url,
            'model': self.model,
            'timeout': self.timeout,
            'max_retries': self.max_retries,
            'temperature': self.temperature,
            'max_tokens': self.max_tokens
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ProviderConfig':
        """Create ProviderConfig from dictionary representation."""
        provider_type = ProviderType(data['provider_type'])
        return cls(
            provider_type=provider_type,
            api_key=data['api_key'],
            name=data['name'],
            base_url=data.get('base_url'),
            model=data.get('model'),
            timeout=data.get('timeout', 30),
            max_retries=data.get('max_retries', 3),
            temperature=data.get('temperature', 0.7),
            max_tokens=data.get('max_tokens')
        )