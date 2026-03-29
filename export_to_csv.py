#!/usr/bin/env python3
"""
Export scraped prices to CSV
Exports price history and alerts to CSV files
"""

import sqlite3
import csv
from pathlib import Path
from datetime import datetime

DB_PATH = "data/prices.db"
EXPORT_DIR = Path("exports")


def export_prices_to_csv():
    """Export all price history to CSV."""
    EXPORT_DIR.mkdir(exist_ok=True)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Get all price data
    cursor.execute("""
        SELECT product_name, retailer, price, url, timestamp
        FROM price_history
        ORDER BY timestamp DESC
    """)
    
    rows = cursor.fetchall()
    conn.close()
    
    if not rows:
        print("No price data found to export.")
        return None
    
    # Create CSV file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = EXPORT_DIR / f"prices_{timestamp}.csv"
    
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Product', 'Retailer', 'Price (INR)', 'URL', 'Timestamp'])
        
        for row in rows:
            product, retailer, price, url, timestamp = row
            writer.writerow([product, retailer, f"₹{price:,.2f}", url, timestamp])
    
    print(f"✅ Prices exported to: {filename}")
    print(f"   Total records: {len(rows)}")
    return filename


def export_alerts_to_csv():
    """Export all alerts to CSV."""
    EXPORT_DIR.mkdir(exist_ok=True)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Get all alert data
    cursor.execute("""
        SELECT product_name, alert_type, price, timestamp
        FROM alerts_sent
        ORDER BY timestamp DESC
    """)
    
    rows = cursor.fetchall()
    conn.close()
    
    if not rows:
        print("No alert data found to export.")
        return None
    
    # Create CSV file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = EXPORT_DIR / f"alerts_{timestamp}.csv"
    
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Product', 'Alert Type', 'Price (INR)', 'Timestamp'])
        
        for row in rows:
            product, alert_type, price, timestamp = row
            writer.writerow([product, alert_type, f"₹{price:,.2f}", timestamp])
    
    print(f"✅ Alerts exported to: {filename}")
    print(f"   Total records: {len(rows)}")
    return filename


def export_summary_csv():
    """Export summary statistics to CSV."""
    EXPORT_DIR.mkdir(exist_ok=True)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Get summary by retailer
    cursor.execute("""
        SELECT 
            retailer,
            COUNT(*) as total_records,
            MIN(price) as lowest_price,
            MAX(price) as highest_price,
            AVG(price) as average_price,
            MIN(timestamp) as first_recorded,
            MAX(timestamp) as last_recorded
        FROM price_history
        GROUP BY retailer
        ORDER BY retailer
    """)
    
    rows = cursor.fetchall()
    conn.close()
    
    if not rows:
        print("No data found to summarize.")
        return None
    
    # Create CSV file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = EXPORT_DIR / f"summary_{timestamp}.csv"
    
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Retailer', 'Total Records', 'Lowest Price', 'Highest Price', 
                        'Average Price', 'First Recorded', 'Last Recorded'])
        
        for row in rows:
            retailer, total, low, high, avg, first, last = row
            writer.writerow([
                retailer, 
                total, 
                f"₹{low:,.2f}" if low else "N/A",
                f"₹{high:,.2f}" if high else "N/A",
                f"₹{avg:,.2f}" if avg else "N/A",
                first,
                last
            ])
    
    print(f"✅ Summary exported to: {filename}")
    print(f"   Total retailers: {len(rows)}")
    return filename


def main():
    """Main export menu."""
    if not Path(DB_PATH).exists():
        print(f"Error: Database not found at {DB_PATH}")
        print("Run the application first to create the database.")
        return
    
    print("\n" + "="*80)
    print("PRICE DATA EXPORT TO CSV")
    print("="*80)
    print("\nSelect an option:")
    print("1. Export all prices")
    print("2. Export all alerts")
    print("3. Export summary statistics")
    print("4. Export all (options 1-3)")
    print("0. Exit")
    
    choice = input("\nEnter your choice (0-4): ").strip()
    
    if choice == '0':
        print("Exiting...")
    elif choice == '1':
        export_prices_to_csv()
    elif choice == '2':
        export_alerts_to_csv()
    elif choice == '3':
        export_summary_csv()
    elif choice == '4':
        print("\nExporting all data...\n")
        export_prices_to_csv()
        export_alerts_to_csv()
        export_summary_csv()
        print(f"\n✅ All files saved to: exports/")
    else:
        print("Invalid choice.")
    
    print("\n" + "="*80)


if __name__ == "__main__":
    main()
