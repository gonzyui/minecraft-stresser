"""
Configuration management for Minecraft Stresser
"""
import yaml
import logging
from typing import Dict, Any


class ConfigManager:
    """Manages application configuration"""

    def __init__(self, config_file: str = "config.yaml"):
        self.config_file = config_file
        self.config = self.load_config()

    def load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file"""
        try:
            with open(self.config_file, 'r') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            logging.warning(f"Config file {self.config_file} not found, using defaults")
            return self.get_default_config()
        except yaml.YAMLError as e:
            logging.error(f"Error parsing config file: {e}")
            return self.get_default_config()

    def get_default_config(self) -> Dict[str, Any]:
        """Return default configuration"""
        return {
            'attack': {
                'protocol': 'tcp',
                'method': 'connect',
                'duration': 30,
                'threads': 100,
                'packet_size': 1024
            },
            'target': {
                'ip': '127.0.0.1',
                'port': 25565
            },
            'logging': {
                'enabled': True,
                'file': 'stresser.log',
                'level': 'INFO'
            },
            'limits': {
                'max_threads': 1000,
                'max_duration': 300,
                'max_packet_size': 65500,
                'min_threads': 1,
                'min_duration': 1,
                'min_packet_size': 1
            }
        }

    def validate_config(self) -> bool:
        """Validate configuration parameters"""
        limits = self.config.get('limits', {})
        attack = self.config.get('attack', {})
        target = self.config.get('target', {})

        if not self.validate_ip(target.get('ip', '')):
            print("❌ Invalid IP address!")
            return False

        if not (limits.get('min_threads', 1) <= attack.get('threads', 100) <= limits.get('max_threads', 1000)):
            print(f"❌ Threads must be between {limits.get('min_threads', 1)} and {limits.get('max_threads', 1000)}!")
            return False

        if not (limits.get('min_duration', 1) <= attack.get('duration', 30) <= limits.get('max_duration', 300)):
            print(f"❌ Duration must be between {limits.get('min_duration', 1)} and {limits.get('max_duration', 300)}!")
            return False

        if attack.get('protocol') == 'udp':
            if not (limits.get('min_packet_size', 1) <= attack.get('packet_size', 1024) <= limits.get('max_packet_size', 65500)):
                print(f"❌ Packet size must be between {limits.get('min_packet_size', 1)} and {limits.get('max_packet_size', 65500)}!")
                return False

        return True

    @staticmethod
    def validate_ip(ip: str) -> bool:
        """Validate IP address format"""
        import ipaddress
        try:
            ipaddress.ip_address(ip)
            return True
        except ValueError:
            return False

    def get(self, key: str, default: Dict[str, Any] | None = None) -> Dict[str, Any]:
        """Get configuration value"""
        return self.config.get(key, default) or {}

    def get_nested(self, *keys) -> Any | None:
        """Get nested configuration value"""
        value = self.config
        for key in keys:
            if isinstance(value, dict):
                value = value.get(key)
            else:
                return None
        return value