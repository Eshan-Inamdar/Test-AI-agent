# Development Notes

## Architecture Overview

### Components

1. **PriceDatabase** (`src/database.py`)
   - SQLite wrapper for price history
   - 15-day low calculation
   - Alert logging
   - Data cleanup

2. **PriceScraper** (`src/scraper.py`)
   - BeautifulSoup-based HTML scraping
   - Multi-retailer support
   - User-agent rotation
   - Error handling

3. **AlertManager** (`src/alerts.py`)
   - Plugin-based alert system
   - Console, Email, Webhook handlers
   - Cooldown mechanism
   - Extensible design

4. **Main App** (`main.py`)
   - Application orchestration
   - Configuration management
   - Background scheduling
   - Lifecycle management

### Data Flow

```
Configuration (YAML)
    ↓
Scheduler (every N minutes)
    ↓
PriceScraper (fetch prices)
    ↓
PriceDatabase (store + analyze)
    ↓
AlertManager (notify if needed)
```

## Common Tasks

### Adding a New Retailer

1. Create scraper class in `src/scraper.py`
2. Inherit from `PriceScraper`
3. Implement `scrape()` method
4. Add to `MultiRetailerScraper.scrapers`
5. Add retailer name to `config/config.yaml`

### Debugging Scrapers

1. Check HTML structure changed with browser DevTools
2. Update CSS selectors in scraper class
3. Add debug logging in scraper
4. Test individual retailer: `python -c "from src.scraper import AmazonScraper; print(AmazonScraper().scrape('iPhone 17 Pro'))"`

### Adding Alert Channels

1. Create handler class inheriting `AlertHandler`
2. Implement `send()` method
3. Register in `_setup_alerts()`
4. Add config section to `config/config.yaml`

## Known Issues

- Amazon may require JavaScript rendering
- Best Buy blocks frequent requests
- Apple Store requires authentication
- Rate limiting after ~10 requests/minute
