#!/usr/bin/env python3
"""
MCP Server for iPhone Price Alert
Exposes price tracking functionality through Model Context Protocol
"""

import sqlite3
import json
import subprocess
import sys
from pathlib import Path
from datetime import datetime
from typing import Any

DB_PATH = "data/prices.db"

def get_db_connection():
    """Get database connection."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def get_latest_prices() -> dict:
    """Get latest prices from all retailers."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT retailer, price, timestamp, url
            FROM price_history
            WHERE (product_name, retailer, timestamp) IN (
                SELECT product_name, retailer, MAX(timestamp)
                FROM price_history
                GROUP BY product_name, retailer
            )
            ORDER BY retailer
        """)
        
        rows = cursor.fetchall()
        prices = []
        for row in rows:
            prices.append({
                "retailer": row['retailer'],
                "price": f"₹{row['price']:,.2f}",
                "timestamp": row['timestamp'],
                "url": row['url']
            })
        return {"status": "success", "data": prices}
    except Exception as e:
        return {"status": "error", "message": str(e)}
    finally:
        conn.close()

def get_db_stats() -> dict:
    """Get database statistics."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT COUNT(*) FROM price_history")
        price_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM alerts_sent")
        alert_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(DISTINCT retailer) FROM price_history")
        retailer_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT MIN(timestamp), MAX(timestamp) FROM price_history")
        result = cursor.fetchone()
        date_from = result[0] if result[0] else "N/A"
        date_to = result[1] if result[1] else "N/A"
        
        return {
            "status": "success",
            "data": {
                "total_prices": price_count,
                "total_alerts": alert_count,
                "unique_retailers": retailer_count,
                "data_from": date_from,
                "data_to": date_to
            }
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}
    finally:
        conn.close()

def get_price_history(limit: int = 20) -> dict:
    """Get recent price history."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT retailer, price, timestamp
            FROM price_history
            ORDER BY timestamp DESC
            LIMIT ?
        """, (limit,))
        
        rows = cursor.fetchall()
        history = []
        for row in rows:
            history.append({
                "retailer": row['retailer'],
                "price": f"₹{row['price']:,.2f}",
                "timestamp": row['timestamp']
            })
        return {"status": "success", "data": history}
    except Exception as e:
        return {"status": "error", "message": str(e)}
    finally:
        conn.close()

def get_alerts(limit: int = 10) -> dict:
    """Get recent alerts."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT alert_type, price, timestamp
            FROM alerts_sent
            ORDER BY timestamp DESC
            LIMIT ?
        """, (limit,))
        
        rows = cursor.fetchall()
        alerts = []
        for row in rows:
            alerts.append({
                "type": row['alert_type'],
                "price": f"₹{row['price']:,.2f}",
                "timestamp": row['timestamp']
            })
        return {"status": "success", "data": alerts}
    except Exception as e:
        return {"status": "error", "message": str(e)}
    finally:
        conn.close()

def get_15day_lows() -> dict:
    """Get 15-day price lows by retailer."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT 
                retailer,
                MIN(price) as low_price,
                MAX(price) as high_price,
                COUNT(*) as data_points
            FROM price_history
            WHERE timestamp >= datetime('now', '-15 days')
            GROUP BY retailer
            ORDER BY retailer
        """)
        
        rows = cursor.fetchall()
        data = []
        for row in rows:
            data.append({
                "retailer": row['retailer'],
                "low": f"₹{row['low_price']:,.2f}",
                "high": f"₹{row['high_price']:,.2f}",
                "data_points": row['data_points']
            })
        return {"status": "success", "data": data}
    except Exception as e:
        return {"status": "error", "message": str(e)}
    finally:
        conn.close()

def export_csv() -> dict:
    """Trigger CSV export."""
    try:
        result = subprocess.run(
            [sys.executable, "export_to_csv.py"],
            capture_output=True,
            text=True,
            timeout=30
        )
        return {
            "status": "success" if result.returncode == 0 else "error",
            "message": result.stdout or result.stderr
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

def process_tool_call(tool_name: str, arguments: dict) -> dict:
    """Process MCP tool calls."""
    tools = {
        "get_latest_prices": lambda: get_latest_prices(),
        "get_database_stats": lambda: get_db_stats(),
        "get_price_history": lambda: get_price_history(arguments.get("limit", 20)),
        "get_recent_alerts": lambda: get_alerts(arguments.get("limit", 10)),
        "get_15day_lows": lambda: get_15day_lows(),
        "export_to_csv": lambda: export_csv(),
    }
    
    if tool_name in tools:
        return tools[tool_name]()
    else:
        return {"status": "error", "message": f"Unknown tool: {tool_name}"}

def handle_request(request: dict) -> dict:
    """Handle incoming MCP requests."""
    method = request.get("method")
    params = request.get("params", {})
    
    if method == "tools/list":
        return {
            "tools": [
                {
                    "name": "get_latest_prices",
                    "description": "Get latest iPhone prices from all tracked retailers"
                },
                {
                    "name": "get_database_stats",
                    "description": "Get database statistics (total prices, alerts, retailers)"
                },
                {
                    "name": "get_price_history",
                    "description": "Get recent price history",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "limit": {"type": "integer", "default": 20}
                        }
                    }
                },
                {
                    "name": "get_recent_alerts",
                    "description": "Get recent price alerts",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "limit": {"type": "integer", "default": 10}
                        }
                    }
                },
                {
                    "name": "get_15day_lows",
                    "description": "Get 15-day low prices by retailer"
                },
                {
                    "name": "export_to_csv",
                    "description": "Export price data to CSV files"
                }
            ]
        }
    elif method == "tools/call":
        tool_name = params.get("name")
        arguments = params.get("arguments", {})
        return process_tool_call(tool_name, arguments)
    else:
        return {"error": f"Unknown method: {method}"}

if __name__ == "__main__":
    import sys
    
    # Check if database exists
    if not Path(DB_PATH).exists():
        print(f"Error: Database not found at {DB_PATH}", file=sys.stderr)
        sys.exit(1)
    
    print("iPhone Price Alert - MCP Server Started", file=sys.stderr)
    print("Listening for MCP requests...", file=sys.stderr)
    
    # Read requests from stdin
    for line in sys.stdin:
        try:
            request = json.loads(line.strip())
            response = handle_request(request)
            print(json.dumps(response))
            sys.stdout.flush()
        except json.JSONDecodeError:
            print(json.dumps({"error": "Invalid JSON"}))
            sys.stdout.flush()
        except Exception as e:
            print(json.dumps({"error": str(e)}))
            sys.stdout.flush()
