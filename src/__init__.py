"""
iPhone Price Alert Tool - Core Modules
"""

__version__ = "1.0.0"
__author__ = "Price Alert Team"

from .database import PriceDatabase
from .scraper import MultiRetailerScraper, AmazonScraper, BestBuyScraper, AppleStoreScraper
from .alerts import AlertManager, ConsoleAlertHandler, EmailAlertHandler, WebhookAlertHandler
from .utils import setup_logging, load_config, validate_config

__all__ = [
    'PriceDatabase',
    'MultiRetailerScraper',
    'AmazonScraper',
    'BestBuyScraper',
    'AppleStoreScraper',
    'AlertManager',
    'ConsoleAlertHandler',
    'EmailAlertHandler',
    'WebhookAlertHandler',
    'setup_logging',
    'load_config',
    'validate_config',
]
