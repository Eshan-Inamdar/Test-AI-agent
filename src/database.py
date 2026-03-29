import sqlite3
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class PriceDatabase:
    """Manages price history storage and retrieval."""
    
    def __init__(self, db_path: str = "data/prices.db"):
        self.db_path = db_path
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self.init_db()
    
    def init_db(self):
        """Initialize database with required tables."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS price_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_name TEXT NOT NULL,
                retailer TEXT NOT NULL,
                price REAL NOT NULL,
                url TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(product_name, retailer, timestamp)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS alerts_sent (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_name TEXT NOT NULL,
                alert_type TEXT NOT NULL,
                price REAL NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_product_timestamp 
            ON price_history(product_name, timestamp)
        ''')
        
        conn.commit()
        conn.close()
        logger.info(f"Database initialized at {self.db_path}")
    
    def insert_price(self, product_name: str, retailer: str, price: float, url: str = None) -> bool:
        """Insert or update price record."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO price_history 
                (product_name, retailer, price, url, timestamp)
                VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
            ''', (product_name, retailer, price, url))
            
            conn.commit()
            conn.close()
            logger.debug(f"Inserted price: {retailer} - ${price} for {product_name}")
            return True
        except Exception as e:
            logger.error(f"Error inserting price: {e}")
            return False
    
    def get_15day_low(self, product_name: str, retailer: str) -> Optional[float]:
        """Get lowest price in last 15 days."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cutoff_date = datetime.now() - timedelta(days=15)
            
            cursor.execute('''
                SELECT MIN(price) FROM price_history
                WHERE product_name = ? AND retailer = ?
                AND timestamp >= ?
            ''', (product_name, retailer, cutoff_date.isoformat()))
            
            result = cursor.fetchone()
            conn.close()
            
            return result[0] if result and result[0] is not None else None
        except Exception as e:
            logger.error(f"Error retrieving 15-day low: {e}")
            return None
    
    def get_latest_price(self, product_name: str, retailer: str) -> Optional[Dict]:
        """Get most recent price record."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT price, url, timestamp FROM price_history
                WHERE product_name = ? AND retailer = ?
                ORDER BY timestamp DESC LIMIT 1
            ''', (product_name, retailer))
            
            result = cursor.fetchone()
            conn.close()
            
            if result:
                return {
                    'price': result[0],
                    'url': result[1],
                    'timestamp': result[2]
                }
            return None
        except Exception as e:
            logger.error(f"Error retrieving latest price: {e}")
            return None
    
    def get_price_history(self, product_name: str, retailer: str, days: int = 15) -> List[Dict]:
        """Get price history for specified period."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cutoff_date = datetime.now() - timedelta(days=days)
            
            cursor.execute('''
                SELECT price, timestamp FROM price_history
                WHERE product_name = ? AND retailer = ?
                AND timestamp >= ?
                ORDER BY timestamp DESC
            ''', (product_name, retailer, cutoff_date.isoformat()))
            
            results = cursor.fetchall()
            conn.close()
            
            return [{'price': r[0], 'timestamp': r[1]} for r in results]
        except Exception as e:
            logger.error(f"Error retrieving price history: {e}")
            return []
    
    def log_alert(self, product_name: str, alert_type: str, price: float) -> bool:
        """Log that an alert was sent."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO alerts_sent (product_name, alert_type, price, timestamp)
                VALUES (?, ?, ?, CURRENT_TIMESTAMP)
            ''', (product_name, alert_type, price))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Error logging alert: {e}")
            return False
    
    def cleanup_old_data(self, days: int = 30):
        """Remove price data older than specified days."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cutoff_date = datetime.now() - timedelta(days=days)
            
            cursor.execute('''
                DELETE FROM price_history WHERE timestamp < ?
            ''', (cutoff_date.isoformat(),))
            
            deleted = cursor.rowcount
            conn.commit()
            conn.close()
            
            logger.info(f"Cleaned up {deleted} old price records")
        except Exception as e:
            logger.error(f"Error cleaning up old data: {e}")
