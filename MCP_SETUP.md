# MCP Server Setup Guide

## Overview
This MCP (Model Context Protocol) server exposes your iPhone Price Alert project's functionality to AI models like Claude through GitHub Copilot.

## What It Provides
The MCP server gives Claude access to:
- ✅ Latest prices from all retailers
- ✅ Database statistics
- ✅ Price history (configurable limit)
- ✅ Recent alerts
- ✅ 15-day low prices
- ✅ CSV export functionality

## Setup Instructions

### Option 1: Using with GitHub Copilot (VS Code Extension)

1. **Save the MCP config to VS Code settings:**
   
   Press `Ctrl+Shift+P` and open `Preferences: Open User Settings (JSON)`
   
   Add this to your `settings.json`:
   ```json
   "github.copilot.advanced": {
     "custom_servers": [
       {
         "name": "iPhone Price Alert",
         "type": "stdio",
         "command": "python",
         "args": ["mcp_server.py"],
         "cwd": "c:\\Users\\ehina\\OneDrive\\Desktop\\Data Science\\Test AI agent\\iPhone-Price-Alert"
       }
     ]
   }
   ```

2. **Restart VS Code**

3. **Now Copilot can access your price data!**
   
   Try asking in Copilot Chat:
   - "Show me the latest iPhone prices"
   - "What are the 15-day lows?"
   - "Export price data to CSV"
   - "Get database statistics"

### Option 2: Standalone Server

```bash
cd "c:\Users\ehina\OneDrive\Desktop\Data Science\Test AI agent\iPhone-Price-Alert"
python mcp_server.py
```

The server reads JSON requests from stdin and outputs JSON responses to stdout.

## Available Tools

### 1. `get_latest_prices`
Gets the most recent price for each retailer.
```
Response: {status, data: [{retailer, price, timestamp, url}]}
```

### 2. `get_database_stats`
Gets overall database statistics.
```
Response: {status, data: {total_prices, total_alerts, unique_retailers, data_from, data_to}}
```

### 3. `get_price_history`
Gets recent price history (default: last 20).
```
Parameters: limit (integer, optional)
Response: {status, data: [{retailer, price, timestamp}]}
```

### 4. `get_recent_alerts`
Gets recent price alerts (default: last 10).
```
Parameters: limit (integer, optional)
Response: {status, data: [{type, price, timestamp}]}
```

### 5. `get_15day_lows`
Gets 15-day low/high prices by retailer.
```
Response: {status, data: [{retailer, low, high, data_points}]}
```

### 6. `export_to_csv`
Triggers CSV export of all data.
```
Response: {status, message}
```

## Example API Calls

### Using Claude/Copilot Chat:
```
"What price did Amazon India have for the iPhone 17 Pro 256GB?"
"Export all price data to CSV"
"Show me the statistics for my price tracking database"
"Have prices dropped in the last 15 days?"
```

### Direct stdin/stdout example:
```bash
echo '{"method": "tools/list"}' | python mcp_server.py
echo '{"method": "tools/call", "params": {"name": "get_latest_prices"}}' | python mcp_server.py
```

## Troubleshooting

**Issue: MCP server won't start**
```
Error: Database not found at data/prices.db
Solution: Run the main application first to create the database
```

**Issue: Copilot doesn't see the MCP server**
```
Solution: 
1. Restart VS Code completely
2. Check that the path in settings.json is correct
3. Verify mcp_server.py exists in the project directory
```

**Issue: Tools not responding**
```
Solution:
1. Check that data/prices.db exists
2. Verify the database has data: python view_data.py
3. Check logs for errors
```

## How It Works

```
┌─ Copilot Chat ─┐
│   (Claude)     │
└────────┬────────┘
         │ JSON request
         ↓
┌──────────────────┐
│  MCP Server      │
│ (mcp_server.py)  │
└────────┬─────────┘
         │ JSON response
         ↓
┌──────────────────┐
│   SQLite DB      │
│ (prices.db)      │
└──────────────────┘
```

## Integration with Your Project

✅ Works with `main.py` - keeps running while collecting prices
✅ Works with `view_data.py` - displays data independently
✅ Works with `export_to_csv.py` - can trigger exports via MCP
✅ Works with `search_iphone.py` - searches while MCP operates

## Next Steps

1. Configure VS Code with the MCP settings above
2. Restart VS Code
3. Open Copilot Chat and ask about your prices
4. Try exporting data through Copilot Chat
5. Use Copilot to analyze trends and patterns

Enjoy having Claude as your price analysis assistant! 🚀
