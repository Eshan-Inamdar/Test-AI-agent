#!/usr/bin/env python3
"""
iPhone Price Alert Tool
Monitors iPhone 17 Pro 256GB prices across retailers and alerts when price hits 15-day low.
"""

import sys
import logging
from pathlib import Path
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
from typing import Optional

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from database import PriceDatabase
from scraper import MultiRetailerScraper
from alerts import AlertManager, ConsoleAlertHandler, EmailAlertHandler, WebhookAlertHandler
from utils import setup_logging, load_config, validate_config


class PriceAlertApplication:
    """Main application class."""
    
    def __init__(self, config_path: str = "config/config.yaml"):
        # Setup logging
        self.logger = setup_logging()
        self.logger.info("=" * 60)
        self.logger.info("iPhone Price Alert Tool Starting...")
        self.logger.info("=" * 60)
        
        # Load and validate config
        try:
            self.config = load_config(config_path)
            validate_config(self.config)
        except Exception as e:
            self.logger.error(f"Configuration error: {e}")
            raise
        
        # Initialize components
        self.db = PriceDatabase(self.config['database']['path'])
        self.scraper = MultiRetailerScraper()
        self.alert_manager = self._setup_alerts()
        
        # Track last alerts to prevent spam
        self.last_alerts = {}
        
        # Scheduler
        self.scheduler = BackgroundScheduler()
    
    def _setup_alerts(self) -> AlertManager:
        """Setup alert handlers based on configuration."""
        manager = AlertManager()
        alert_config = self.config.get('alerts', {})
        handlers_config = alert_config.get('handlers', {})
        
        # Console handler
        if handlers_config.get('console', {}).get('enabled', True):
            manager.add_handler(ConsoleAlertHandler())
        
        # Email handler
        if handlers_config.get('email', {}).get('enabled', False):
            email_config = handlers_config['email']
            try:
                manager.add_handler(EmailAlertHandler(
                    smtp_server=email_config['smtp_server'],
                    smtp_port=email_config['smtp_port'],
                    sender_email=email_config['sender_email'],
                    sender_password=email_config['sender_password'],
                    recipient_email=email_config['recipient_email']
                ))
            except Exception as e:
                self.logger.error(f"Failed to setup email handler: {e}")
        
        # Webhook handler
        if handlers_config.get('webhook', {}).get('enabled', False):
            webhook_url = handlers_config['webhook']['url']
            manager.add_handler(WebhookAlertHandler(webhook_url))
        
        return manager
    
    def check_prices(self):
        """Check prices and send alerts if necessary."""
        self.logger.info(f"Starting price check at {datetime.now()}")
        
        product_name = self.config['product']
        
        # Scrape prices
        prices = self.scraper.scrape_all(product_name)
        
        if not prices:
            self.logger.warning("No prices found during scrape")
            return
        
        # Process each price
        for price_data in prices:
            retailer = price_data['retailer']
            current_price = price_data['price']
            url = price_data['url']
            
            # Store price in database
            self.db.insert_price(product_name, retailer, current_price, url)
            
            # Get 15-day low
            low_price = self.db.get_15day_low(product_name, retailer)
            
            # Log current status
            self.logger.info(f"{retailer}: ${current_price:.2f}" + 
                           (f" | 15-Day Low: ${low_price:.2f}" if low_price else ""))
            
            # Check if alert should be sent
            if low_price is not None and current_price <= low_price:
                self._send_alert_if_needed(product_name, current_price, low_price, retailer, url)
        
        self.logger.info("Price check complete")
    
    def _send_alert_if_needed(self, product_name: str, price: float, low_price: float, 
                              retailer: str, url: str):
        """Send alert if cooldown period has passed."""
        alert_key = f"{product_name}_{retailer}"
        now = datetime.now()
        
        # Check cooldown
        cooldown_minutes = self.config['alerts'].get('cooldown_minutes', 120)
        
        if alert_key in self.last_alerts:
            time_diff = (now - self.last_alerts[alert_key]).total_seconds() / 60
            if time_diff < cooldown_minutes:
                self.logger.debug(f"Alert cooldown active for {alert_key} ({time_diff:.1f}/{cooldown_minutes} min)")
                return
        
        # Send alert
        self.logger.warning(f"🚨 PRICE ALERT: {product_name} at {retailer} - ${price:.2f} (15-Day Low: ${low_price:.2f})")
        
        if self.alert_manager.send_alert(product_name, price, low_price, retailer, url):
            self.last_alerts[alert_key] = now
            self.db.log_alert(product_name, 'price_low', price)
            self.logger.info(f"Alert sent for {alert_key}")
        else:
            self.logger.error(f"Failed to send alert for {alert_key}")
    
    def start(self):
        """Start the application."""
        try:
            # Run initial check
            self.logger.info("Running initial price check...")
            self.check_prices()
            
            # Schedule periodic checks
            check_interval = self.config['check_interval']
            self.scheduler.add_job(
                self.check_prices,
                'interval',
                minutes=check_interval,
                id='price_check',
                replace_existing=True
            )
            
            # Schedule cleanup
            self.scheduler.add_job(
                lambda: self.db.cleanup_old_data(self.config['database']['cleanup_days']),
                'cron',
                hour=2,
                minute=0,
                id='cleanup',
                replace_existing=True
            )
            
            self.scheduler.start()
            self.logger.info(f"Scheduler started. Will check prices every {check_interval} minutes.")
            self.logger.info("Press Ctrl+C to stop the application.")
            
            # Keep running
            try:
                while True:
                    pass
            except KeyboardInterrupt:
                self.logger.info("Received shutdown signal...")
                self.stop()
        
        except Exception as e:
            self.logger.error(f"Error starting application: {e}", exc_info=True)
            raise
    
    def stop(self):
        """Stop the application."""
        self.logger.info("Stopping scheduler...")
        self.scheduler.shutdown()
        self.logger.info("Application stopped.")


def main():
    """Main entry point."""
    config_path = Path(__file__).parent / "config" / "config.yaml"
    
    try:
        app = PriceAlertApplication(str(config_path))
        app.start()
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f"Fatal error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
