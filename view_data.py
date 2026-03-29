#!/usr/bin/env python3
"""
Data Viewer Script - Display stored price and alert data
"""

import sqlite3
import sys
from pathlib import Path
from datetime import datetime
from tabulate import tabulate

DB_PATH = "data/prices.db"


def get_connection():
    """Get database connection."""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.OperationalError as e:
        print(f"Error connecting to database: {e}")
        sys.exit(1)


def view_latest_prices():
    """View the latest prices for each retailer."""
    print("\n" + "="*100)
    print("LATEST PRICES")
    print("="*100)
    
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        query = """
        SELECT 
            retailer,
            price,
            timestamp,
            url
        FROM price_history
        WHERE (product_name, retailer, timestamp) IN (
            SELECT product_name, retailer, MAX(timestamp)
            FROM price_history
            GROUP BY product_name, retailer
        )
        ORDER BY retailer, timestamp DESC
        """
        
        cursor.execute(query)
        rows = cursor.fetchall()
        
        if not rows:
            print("No price data found.")
            return
        
        for row in rows:
            # Check if price is in INR (large number) or USD
            price = row['price']
            if price > 1000:  # Likely INR
                currency = "₹"
            else:
                currency = "$"
            
            print(f"\nRetailer: {row['retailer'].upper()}")
            print(f"Price: {currency}{price:,.2f}")
            print(f"Date: {row['timestamp']}")
            print(f"Link: {row['url']}")
            print("-" * 100)
    
    finally:
        conn.close()


def view_price_history():
    """View price history for all retailers."""
    print("\n" + "="*100)
    print("PRICE HISTORY (Last 20 entries)")
    print("="*100)
    
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        query = """
        SELECT 
            retailer,
            price,
            timestamp
        FROM price_history
        ORDER BY timestamp DESC
        LIMIT 20
        """
        
        cursor.execute(query)
        rows = cursor.fetchall()
        
        if not rows:
            print("No price history found.")
            return
        
        for row in rows:
            price = row['price']
            if price > 1000:
                currency = "₹"
            else:
                currency = "$"
                
            print(f"{row['retailer']:<20} | {currency}{price:>12,.2f} | {row['timestamp']}")
    
    finally:
        conn.close()


def view_alerts():
    """View recent price alerts."""
    print("\n" + "="*100)
    print("RECENT PRICE ALERTS (Last 15 entries)")
    print("="*100)
    
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        query = """
        SELECT 
            alert_type,
            price,
            timestamp
        FROM alerts_sent
        ORDER BY timestamp DESC
        LIMIT 15
        """
        
        cursor.execute(query)
        rows = cursor.fetchall()
        
        if not rows:
            print("No alerts found.")
            return
        
        for row in rows:
            price = row['price']
            if price > 1000:
                currency = "₹"
            else:
                currency = "$"
                
            print(f"{row['alert_type']:<15} | {currency}{price:>12,.2f} | {row['timestamp']}")
    
    finally:
        conn.close()


def view_15day_lows():
    """View 15-day low prices."""
    print("\n" + "="*100)
    print("15-DAY LOW PRICES BY RETAILER")
    print("="*100)
    
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        query = """
        SELECT 
            retailer,
            MIN(price) as low_price,
            MAX(price) as high_price,
            COUNT(*) as data_points,
            MIN(timestamp) as oldest,
            MAX(timestamp) as newest
        FROM price_history
        WHERE timestamp >= datetime('now', '-15 days')
        GROUP BY retailer
        ORDER BY retailer
        """
        
        cursor.execute(query)
        rows = cursor.fetchall()
        
        if not rows:
            print("No price data from the last 15 days found.")
            return
        
        for row in rows:
            low = row['low_price']
            high = row['high_price']
            if low > 1000:
                currency = "₹"
            else:
                currency = "$"
                
            print(f"\n{row['retailer'].upper()}")
            print(f"  Low:    {currency}{low:>12,.2f}")
            print(f"  High:   {currency}{high:>12,.2f}")
            print(f"  Points: {row['data_points']}")
            print(f"  From:   {row['oldest']}")
            print(f"  To:     {row['newest']}")
    
    finally:
        conn.close()


def view_db_stats():
    """View database statistics."""
    print("\n" + "="*80)
    print("DATABASE STATISTICS")
    print("="*80)
    
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        stats = {}
        
        # Price records count
        cursor.execute("SELECT COUNT(*) FROM price_history")
        stats['Total Prices'] = cursor.fetchone()[0]
        
        # Alert records count
        cursor.execute("SELECT COUNT(*) FROM alerts_sent")
        stats['Total Alerts'] = cursor.fetchone()[0]
        
        # Retailers count
        cursor.execute("SELECT COUNT(DISTINCT retailer) FROM price_history")
        stats['Unique Retailers'] = cursor.fetchone()[0]
        
        # Date range
        cursor.execute("SELECT MIN(timestamp), MAX(timestamp) FROM price_history")
        result = cursor.fetchone()
        stats['Data From'] = result[0] if result[0] else "N/A"
        stats['Data To'] = result[1] if result[1] else "N/A"
        
        for key, value in stats.items():
            print(f"{key:<25}: {value}")
    
    finally:
        conn.close()


def main():
    """Main menu."""
    while True:
        print("\n" + "="*80)
        print("iPhone Price Alert - DATA VIEWER")
        print("="*80)
        print("\nSelect an option:")
        print("1. View latest prices by retailer")
        print("2. View price history (last 20)")
        print("3. View price alerts (last 15)")
        print("4. View 15-day lows by retailer")
        print("5. View database statistics")
        print("6. View all (options 1-5)")
        print("0. Exit")
        
        choice = input("\nEnter your choice (0-6): ").strip()
        
        if choice == '0':
            print("Exiting...")
            break
        elif choice == '1':
            view_latest_prices()
        elif choice == '2':
            view_price_history()
        elif choice == '3':
            view_alerts()
        elif choice == '4':
            view_15day_lows()
        elif choice == '5':
            view_db_stats()
        elif choice == '6':
            view_db_stats()
            view_latest_prices()
            view_15day_lows()
            view_price_history()
            view_alerts()
        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    # Check if database exists
    if not Path(DB_PATH).exists():
        print(f"Error: Database not found at {DB_PATH}")
        print("Make sure the application has run at least once to create the database.")
        sys.exit(1)
    
    main()
