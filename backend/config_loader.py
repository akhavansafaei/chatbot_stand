"""Configuration loader for the chatbot system."""

import yaml
from pathlib import Path
from typing import Dict, Any


class ConfigLoader:
    """Load and manage configuration from YAML file."""

    def __init__(self, config_path: str = "config.yaml"):
        """Initialize the config loader.

        Args:
            config_path: Path to the configuration file
        """
        self.config_path = Path(config_path)
        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file.

        Returns:
            Dictionary containing configuration
        """
        if not self.config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")

        with open(self.config_path, 'r') as f:
            config = yaml.safe_load(f)

        return config

    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value by key.

        Args:
            key: Configuration key (supports dot notation, e.g., 'server.host')
            default: Default value if key not found

        Returns:
            Configuration value
        """
        keys = key.split('.')
        value = self.config

        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default

        return value

    def get_asr_config(self) -> Dict[str, Any]:
        """Get ASR configuration."""
        return self.config.get('asr', {})

    def get_tts_config(self) -> Dict[str, Any]:
        """Get TTS configuration."""
        return self.config.get('tts', {})

    def get_llm_config(self) -> Dict[str, Any]:
        """Get LLM configuration."""
        return self.config.get('llm', {})

    def get_server_config(self) -> Dict[str, Any]:
        """Get server configuration."""
        return self.config.get('server', {})

    def get_avatar_config(self) -> Dict[str, Any]:
        """Get avatar configuration."""
        return self.config.get('avatar', {})
