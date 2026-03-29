#!/usr/bin/env python3
"""
Test Data Generator - Populate database with sample data for testing
Run this to test the data viewer and see how the application works
"""

import sqlite3
from pathlib import Path
from datetime import datetime, timedelta
import random

DB_PATH = "data/prices.db"

# Sample data
RETAILERS = ["amazon", "bestbuy", "apple"]
PRODUCT = "iPhone 17 Pro 256GB"

def generate_test_data():
    """Generate and insert test data into database."""
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("Generating test data...")
    
    # Generate price history for the last 15 days
    start_date = datetime.now() - timedelta(days=15)
    
    # Base prices for each retailer (with some variation)
    base_prices = {
        "amazon": 999.99,
        "bestbuy": 1004.99,
        "apple": 1099.99
    }
    
    price_records = 0
    
    for retailer in RETAILERS:
        base_price = base_prices[retailer]
        
        # Generate 5-7 price points per retailer over 15 days
        for day_offset in range(0, 15, random.randint(2, 4)):
            timestamp = (start_date + timedelta(days=day_offset)).isoformat()
            
            # Add some random variation (±10%)
            price = base_price + random.uniform(-100, 100)
            
            # URLs for each retailer
            urls = {
                "amazon": f"https://www.amazon.com/s?k={PRODUCT.replace(' ', '+')}&page=1",
                "bestbuy": f"https://www.bestbuy.com/site/searchpage.jsp?st={PRODUCT.replace(' ', '+')}",
                "apple": f"https://www.apple.com/shop/goto/product/{PRODUCT.replace(' ', '-').lower()}"
            }
            
            cursor.execute('''
                INSERT INTO price_history 
                (product_name, retailer, price, url, timestamp)
                VALUES (?, ?, ?, ?, ?)
            ''', (PRODUCT, retailer, price, urls[retailer], timestamp))
            
            price_records += 1
    
    # Generate some alert records
    alert_records = 0
    for i in range(5):
        timestamp = (start_date + timedelta(days=random.randint(0, 14))).isoformat()
        retailer = random.choice(RETAILERS)
        price = random.uniform(900, 1100)
        
        cursor.execute('''
            INSERT INTO alerts_sent
            (product_name, alert_type, price, timestamp)
            VALUES (?, ?, ?, ?)
        ''', (PRODUCT, "price_low", price, timestamp))
        
        alert_records += 1
    
    conn.commit()
    conn.close()
    
    print(f"✓ Generated {price_records} price records")
    print(f"✓ Generated {alert_records} alert records")
    print("\nNow run: python view_data.py")


if __name__ == "__main__":
    if not Path(DB_PATH).exists():
        print(f"Error: Database not found at {DB_PATH}")
        print("Run the main application first to create the database.")
        exit(1)
    
    # Confirm before generating
    print("This will add test data to your database.")
    confirm = input("Continue? (y/n): ").strip().lower()
    
    if confirm == 'y':
        generate_test_data()
        print("\n✓ Test data generated successfully!")
    else:
        print("Cancelled.")
