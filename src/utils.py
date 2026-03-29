import logging
import logging.handlers
from pathlib import Path
from typing import Dict, Any
import yaml


def setup_logging(log_dir: str = "logs", log_file: str = "price_alert.log", level: str = "INFO") -> logging.Logger:
    """Configure logging for the application."""
    Path(log_dir).mkdir(parents=True, exist_ok=True)
    
    log_path = Path(log_dir) / log_file
    
    # Create logger
    logger = logging.getLogger()
    logger.setLevel(level)
    
    # File handler with rotation
    file_handler = logging.handlers.RotatingFileHandler(
        log_path,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5
    )
    file_handler.setLevel(level)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    
    # Formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # Add handlers
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger


def load_config(config_path: str) -> Dict[str, Any]:
    """Load configuration from YAML file."""
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        return config
    except FileNotFoundError:
        raise FileNotFoundError(f"Config file not found: {config_path}")
    except yaml.YAMLError as e:
        raise ValueError(f"Error parsing config file: {e}")


def save_config(config: Dict[str, Any], config_path: str):
    """Save configuration to YAML file."""
    try:
        Path(config_path).parent.mkdir(parents=True, exist_ok=True)
        with open(config_path, 'w') as f:
            yaml.dump(config, f, default_flow_style=False)
    except Exception as e:
        raise Exception(f"Error saving config: {e}")


def validate_config(config: Dict[str, Any]) -> bool:
    """Validate configuration structure."""
    required_keys = ['product', 'retailers', 'check_interval', 'database']
    
    for key in required_keys:
        if key not in config:
            raise ValueError(f"Missing required config key: {key}")
    
    if not isinstance(config['retailers'], list) or len(config['retailers']) == 0:
        raise ValueError("retailers must be a non-empty list")
    
    if not isinstance(config['check_interval'], int) or config['check_interval'] <= 0:
        raise ValueError("check_interval must be a positive integer")
    
    return True
