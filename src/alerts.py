import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import Optional, Dict
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class AlertHandler(ABC):
    """Base class for alert handlers."""
    
    @abstractmethod
    def send(self, product_name: str, price: float, low_price: float, retailer: str, url: str) -> bool:
        """Send alert."""
        pass


class ConsoleAlertHandler(AlertHandler):
    """Alert handler that prints to console."""
    
    def send(self, product_name: str, price: float, low_price: float, retailer: str, url: str) -> bool:
        """Send alert to console."""
        alert_message = f"""
╔══════════════════════════════════════════════════════════╗
║             🚨 PRICE ALERT - 15 DAY LOW! 🚨             ║
╠══════════════════════════════════════════════════════════╣
║ Product:  {product_name:<44} ║
║ Retailer: {retailer:<44} ║
║ Current Price: ${price:<41} ║
║ 15-Day Low:    ${low_price:<41} ║
║ URL: {url:<51} ║
║ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S'):<44} ║
╚══════════════════════════════════════════════════════════╝
        """
        print(alert_message)
        logger.info("Alert sent to console")
        return True


class EmailAlertHandler(AlertHandler):
    """Alert handler that sends emails."""
    
    def __init__(self, smtp_server: str, smtp_port: int, sender_email: str, sender_password: str, recipient_email: str):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.sender_email = sender_email
        self.sender_password = sender_password
        self.recipient_email = recipient_email
    
    def send(self, product_name: str, price: float, low_price: float, retailer: str, url: str) -> bool:
        """Send alert via email."""
        try:
            subject = f"🚨 Price Alert: {product_name} at 15-Day Low!"
            
            body = f"""
            <html>
                <body style="font-family: Arial, sans-serif;">
                    <h2 style="color: #d9534f;">Price Alert - 15 Day Low!</h2>
                    <table style="border-collapse: collapse; width: 100%;">
                        <tr>
                            <td style="padding: 8px; border: 1px solid #ddd;"><strong>Product:</strong></td>
                            <td style="padding: 8px; border: 1px solid #ddd;">{product_name}</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px; border: 1px solid #ddd;"><strong>Retailer:</strong></td>
                            <td style="padding: 8px; border: 1px solid #ddd;">{retailer}</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px; border: 1px solid #ddd;"><strong>Current Price:</strong></td>
                            <td style="padding: 8px; border: 1px solid #ddd; color: #d9534f; font-weight: bold;">${price:.2f}</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px; border: 1px solid #ddd;"><strong>15-Day Low:</strong></td>
                            <td style="padding: 8px; border: 1px solid #ddd;">${low_price:.2f}</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px; border: 1px solid #ddd;"><strong>Savings:</strong></td>
                            <td style="padding: 8px; border: 1px solid #ddd; color: #5cb85c; font-weight: bold;">${(low_price - price):.2f}</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px; border: 1px solid #ddd;"><strong>Time:</strong></td>
                            <td style="padding: 8px; border: 1px solid #ddd;">{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</td>
                        </tr>
                    </table>
                    <br>
                    <a href="{url}" style="background-color: #5cb85c; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">View Product</a>
                </body>
            </html>
            """
            
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = self.sender_email
            message["To"] = self.recipient_email
            
            message.attach(MIMEText(body, "html"))
            
            with smtplib.SMTP_SSL(self.smtp_server, self.smtp_port) as server:
                server.login(self.sender_email, self.sender_password)
                server.sendmail(self.sender_email, self.recipient_email, message.as_string())
            
            logger.info(f"Email alert sent to {self.recipient_email}")
            return True
        except Exception as e:
            logger.error(f"Error sending email alert: {e}")
            return False


class WebhookAlertHandler(AlertHandler):
    """Alert handler that sends webhooks."""
    
    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url
    
    def send(self, product_name: str, price: float, low_price: float, retailer: str, url: str) -> bool:
        """Send alert via webhook."""
        try:
            import requests
            
            payload = {
                'product': product_name,
                'price': price,
                'low_price': low_price,
                'retailer': retailer,
                'url': url,
                'timestamp': datetime.now().isoformat(),
                'alert_type': 'price_low'
            }
            
            response = requests.post(
                self.webhook_url,
                json=payload,
                timeout=10
            )
            response.raise_for_status()
            
            logger.info(f"Webhook alert sent to {self.webhook_url}")
            return True
        except Exception as e:
            logger.error(f"Error sending webhook alert: {e}")
            return False


class AlertManager:
    """Manages multiple alert handlers."""
    
    def __init__(self):
        self.handlers = []
    
    def add_handler(self, handler: AlertHandler):
        """Add an alert handler."""
        self.handlers.append(handler)
        logger.info(f"Added alert handler: {handler.__class__.__name__}")
    
    def send_alert(self, product_name: str, price: float, low_price: float, retailer: str, url: str) -> bool:
        """Send alert to all registered handlers."""
        if not self.handlers:
            logger.warning("No alert handlers configured")
            return False
        
        success = True
        for handler in self.handlers:
            try:
                if not handler.send(product_name, price, low_price, retailer, url):
                    success = False
            except Exception as e:
                logger.error(f"Error in handler {handler.__class__.__name__}: {e}")
                success = False
        
        return success
