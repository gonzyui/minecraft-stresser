"""
Logging configuration for Minecraft Stresser
"""
import logging
from typing import Dict, Any


def setup_logging(config: Dict[str, Any]):
    """Setup logging from application config"""
    log_config = config.get('logging', {})
    if not log_config.get('enabled', True):
        return

    level = getattr(logging, log_config.get('level', 'INFO').upper())

    logging.getLogger().handlers.clear()

    file_handler = logging.FileHandler(log_config.get('file', 'stresser.log'))
    file_handler.setLevel(level)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    ))

    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(logging.Formatter('%(levelname)s - %(message)s'))

    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)