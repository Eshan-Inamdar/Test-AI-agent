# iPhone 17 Pro Price Alert Tool

A Python-based automated price tracking and alert system for the iPhone 17 Pro 256GB. The tool monitors prices across major retailers and sends alerts when the price reaches its 15-day low.

## Features

✅ **Multi-Retailer Scraping**
- Amazon
- Best Buy  
- Apple Store

✅ **Price Tracking**
- SQLite database for historical data
- 15-day price history tracking
- Rolling low price calculation

✅ **Smart Alerts**
- Triggers when current price ≤ 15-day low
- Multiple alert channels (console, email, webhook)
- Cooldown system to prevent alert spam
- HTML email formatting with product links

✅ **Robust & Scalable**
- Error handling and retry logic
- Rotating user agents for scraping
- Automatic old data cleanup
- Comprehensive logging
- Background job scheduling

## Project Structure

```
iPhone-Price-Alert/
├── main.py                 # Main application entry point
├── requirements.txt        # Python dependencies
├── config/
│   └── config.yaml        # Configuration file
├── src/
│   ├── database.py        # SQLite database management
│   ├── scraper.py         # Price scraping logic
│   ├── alerts.py          # Alert system
│   └── utils.py           # Utility functions
├── data/
│   └── prices.db          # SQLite database (auto-created)
└── logs/
    └── price_alert.log    # Application logs (auto-created)
```

## Installation

### Prerequisites
- Python 3.8+
- pip package manager

### Setup

1. **Clone or extract the project**
```bash
cd iPhone-Price-Alert
```

2. **Create virtual environment** (recommended)
```bash
# On Windows
python -m venv venv
venv\Scripts\activate

# On macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

## Configuration

Edit `config/config.yaml` to customize:

```yaml
product: "iPhone 17 Pro 256GB"      # Product to track
retailers:                           # Retailers to monitor
  - amazon
  - bestbuy
  - apple

check_interval: 30                   # Minutes between checks

alerts:
  enabled: true
  handlers:
    console:                         # Console alerts (always on)
      enabled: true
    
    email:                           # Email notifications
      enabled: false
      smtp_server: "smtp.gmail.com"
      sender_email: "your-email@gmail.com"
      sender_password: "app-password"
      recipient_email: "recipient@email.com"
    
    webhook:                         # HTTP webhook
      enabled: false
      url: "https://your-webhook-url.com"
```

### Email Configuration (Gmail)

1. Enable 2-factor authentication on your Gmail account
2. Create an [App Password](https://myaccount.google.com/apppasswords)
3. Copy the 16-character password to `config.yaml`
4. Set `enabled: true` for email handler

## Usage

### Start the Application

```bash
python main.py
```

The application will:
1. ✅ Run an initial price check immediately
2. ✅ Schedule periodic checks every 30 minutes (configurable)
3. ✅ Store prices in SQLite database
4. ✅ Send alerts when price ≤ 15-day low
5. ✅ Log all activity to `logs/price_alert.log`

### Monitor Logs

```bash
# View logs in real-time
tail -f logs/price_alert.log

# On Windows
Get-Content logs\price_alert.log -Tail 20 -Wait
```

### Database Queries

View price history using Python:

```python
from src.database import PriceDatabase

db = PriceDatabase("data/prices.db")

# Get latest price
latest = db.get_latest_price("iPhone 17 Pro 256GB", "Amazon")
print(f"Latest price: ${latest['price']}")

# Get 15-day low
low = db.get_15day_low("iPhone 17 Pro 256GB", "Amazon")
print(f"15-day low: ${low}")

# Get price history
history = db.get_price_history("iPhone 17 Pro 256GB", "Amazon")
for entry in history:
    print(f"${entry['price']} on {entry['timestamp']}")
```

## Alert Examples

### Console Alert
```
╔══════════════════════════════════════════════════════════╗
║             🚨 PRICE ALERT - 15 DAY LOW! 🚨             ║
╠══════════════════════════════════════════════════════════╣
║ Product:  iPhone 17 Pro 256GB                            ║
║ Retailer: Amazon                                         ║
║ Current Price: $899.00                                   ║
║ 15-Day Low:    $899.00                                   ║
║ URL: https://amazon.com/iPhone-17-Pro-256GB             ║
║ Time: 2026-03-29 14:30:00                                ║
╚══════════════════════════════════════════════════════════╝
```

### Email Alert
Receive HTML-formatted emails with:
- Current price (highlighted in red)
- 15-day low price
- Amount saved
- Direct link to product

## Troubleshooting

### No prices found during scrape
- Check internet connection
- Retailers may have changed their HTML structure
- Update scraper selectors if needed
- Check logs for specific errors

### Emails not sending
- Verify Gmail app password is correct
- Check if 2FA is enabled
- Ensure sender email matches in config
- Check `logs/price_alert.log` for SMTP errors

### Database errors
- Ensure `data/` directory exists
- Check file permissions
- Remove corrupted `data/prices.db` to reset

### High CPU usage
- Increase `check_interval` to reduce frequency
- Check for infinite loops in logs

## Performance Tips

1. **Adjust check frequency**: Increase `check_interval` to reduce API calls
2. **Enable email cooldown**: Set `cooldown_minutes` to prevent alert spam
3. **Use webhook for integrations**: Lighter weight than email
4. **Monitor database size**: Old data auto-cleaned after 30 days

## Customization

### Add New Retailers

Edit `src/scraper.py`:

```python
class NewRetailerScraper(PriceScraper):
    def scrape(self, product_name: str) -> Optional[Dict]:
        # Implement scraping logic
        return {
            'retailer': 'New Retailer',
            'price': price,
            'url': url
        }

# Add to MultiRetailerScraper
self.scrapers['new'] = NewRetailerScraper()
```

### Add Custom Alert Handler

Extend `AlertHandler` in `src/alerts.py`:

```python
class SlackAlertHandler(AlertHandler):
    def __init__(self, webhook_url):
        self.webhook_url = webhook_url
    
    def send(self, product_name, price, low_price, retailer, url):
        # Send to Slack webhook
        pass
```

## Limitations

- **HTML Scraping**: Retailers may change their page structure
- **Rate Limiting**: Some sites may block frequent requests
- **Dynamic Content**: Sites with JavaScript rendering need adjustment
- **Accuracy**: Web scraping results depend on page structure

## Future Improvements

- [ ] Use API endpoints instead of HTML scraping
- [ ] Add proxy support for reliability
- [ ] SMS alerts via Twilio
- [ ] Discord/Slack integration
- [ ] Price comparison charts
- [ ] Multiple product tracking
- [ ] Web dashboard UI

## Dependencies

- **requests**: HTTP client
- **beautifulsoup4**: HTML parsing
- **lxml**: HTML/XML parser
- **APScheduler**: Background job scheduling
- **PyYAML**: Configuration file parsing

See `requirements.txt` for versions.

## License

MIT License - Feel free to use and modify

## Support

For issues or improvements, check:
1. `logs/price_alert.log` for error details
2. Verify `config/config.yaml` syntax
3. Ensure all dependencies are installed
4. Test with `python main.py`

---

**Happy tracking! Get notified when iPhone 17 Pro prices hit their 15-day low! 🚨**
