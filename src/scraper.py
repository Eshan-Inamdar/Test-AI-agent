import requests
from bs4 import BeautifulSoup
import logging
import random
from typing import Optional, Dict, List
from urllib.parse import urljoin

logger = logging.getLogger(__name__)

# User agents for rotation
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0',
]


class PriceScraper:
    """Base scraper class for price extraction."""
    
    def __init__(self, timeout: int = 10):
        self.timeout = timeout
        self.session = requests.Session()
    
    def _get_headers(self) -> Dict:
        """Get headers with random user agent."""
        return {
            'User-Agent': random.choice(USER_AGENTS),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        }
    
    def fetch_page(self, url: str) -> Optional[BeautifulSoup]:
        """Fetch and parse a webpage."""
        try:
            response = self.session.get(
                url,
                headers=self._get_headers(),
                timeout=self.timeout
            )
            response.raise_for_status()
            return BeautifulSoup(response.content, 'html.parser')
        except requests.RequestException as e:
            logger.error(f"Error fetching {url}: {e}")
            return None


class AmazonScraper(PriceScraper):
    """Scraper for Amazon US prices."""
    
    def scrape(self, product_name: str) -> Optional[Dict]:
        """Scrape Amazon US for product price."""
        try:
            search_url = f"https://www.amazon.com/s?k={product_name.replace(' ', '+')}"
            soup = self.fetch_page(search_url)
            
            if not soup:
                return None
            
            # Find first product listing
            product = soup.find('div', {'data-component-type': 's-search-result'})
            if not product:
                logger.warning("No products found on Amazon US")
                return None
            
            # Extract price
            price_elem = product.find('span', {'class': 'a-price-whole'})
            if not price_elem:
                logger.warning("Price not found on Amazon US")
                return None
            
            price_text = price_elem.text.strip().replace('$', '').replace(',', '')
            price = float(price_text)
            
            # Extract URL
            link_elem = product.find('a', {'class': 'a-link-normal'})
            url = urljoin('https://www.amazon.com', link_elem['href']) if link_elem else search_url
            
            return {
                'retailer': 'amazon',
                'price': price,
                'url': url
            }
        except Exception as e:
            logger.error(f"Error scraping Amazon US: {e}")
            return None


class AmazonIndiaScraper(PriceScraper):
    """Scraper for Amazon India prices."""
    
    def scrape(self, product_name: str) -> Optional[Dict]:
        """Scrape Amazon India for product price."""
        try:
            # Use more specific search for Apple iPhone
            search_url = f"https://www.amazon.in/s?k=Apple+{product_name.replace(' ', '+')}&i=electronics"
            soup = self.fetch_page(search_url)
            
            if not soup:
                return None
            
            # Find all product listings
            products = soup.find_all('div', {'data-component-type': 's-search-result'})
            if not products:
                logger.warning("No products found on Amazon India")
                return None
            
            # Look for the EXACT 256GB model (non-Plus, non-Max variant)
            target_product = None
            for product in products:
                title_elem = product.find('h2')
                if title_elem:
                    title = title_elem.text.strip()
                    # Find "iPhone 17 Pro 256 GB" but not Max or Plus
                    if "iPhone 17 Pro" in title and "256 GB" in title and "Max" not in title and "Plus" not in title:
                        target_product = product
                        break
            
            if not target_product:
                logger.warning("iPhone 17 Pro 256GB not found on Amazon India")
                return None
            
            # Extract price
            price_elem = target_product.find('span', {'class': 'a-price-whole'})
            if not price_elem:
                logger.warning("Price not found on Amazon India")
                return None
            
            price_text = price_elem.text.strip().replace('₹', '').replace(',', '')
            price_inr = float(price_text)
            
            # Extract URL
            link_elem = target_product.find('a', {'class': 'a-link-normal'})
            url = urljoin('https://www.amazon.in', link_elem['href']) if link_elem else search_url
            
            logger.info(f"Found iPhone 17 Pro 256GB: ₹{price_inr:.0f}")
            
            return {
                'retailer': 'amazon_india',
                'price': price_inr,
                'url': url
            }
        except Exception as e:
            logger.error(f"Error scraping Amazon India: {e}")
            return None


class BestBuyScraper(PriceScraper):
    """Scraper for Best Buy prices."""
    
    def scrape(self, product_name: str) -> Optional[Dict]:
        """Scrape Best Buy for product price."""
        try:
            search_url = f"https://www.bestbuy.com/site/searchpage.jsp?st={product_name.replace(' ', '+')}"
            soup = self.fetch_page(search_url)
            
            if not soup:
                return None
            
            # Find first product
            product = soup.find('div', {'class': 'sku-item'})
            if not product:
                logger.warning("No products found on Best Buy")
                return None
            
            # Extract price
            price_elem = product.find('div', {'class': 'priceView'})
            if not price_elem:
                logger.warning("Price not found on Best Buy")
                return None
            
            price_text = price_elem.text.strip().replace('$', '').replace(',', '')
            price = float(price_text)
            
            # Extract URL
            link_elem = product.find('a', {'class': 'sku-title'})
            url = urljoin('https://www.bestbuy.com', link_elem['href']) if link_elem else search_url
            
            return {
                'retailer': 'Best Buy',
                'price': price,
                'url': url
            }
        except Exception as e:
            logger.error(f"Error scraping Best Buy: {e}")
            return None


class AppleStoreScraper(PriceScraper):
    """Scraper for Apple Store prices."""
    
    def scrape(self, product_name: str) -> Optional[Dict]:
        """Scrape Apple Store for product price."""
        try:
            # Apple Store direct URL for iPhone 17 Pro 256GB
            url = "https://www.apple.com/shop/buy-iphone/iphone-17-pro"
            soup = self.fetch_page(url)
            
            if not soup:
                return None
            
            # Find price element (specific to Apple Store layout)
            price_elem = soup.find('span', {'class': 'numeric'})
            if not price_elem:
                logger.warning("Price not found on Apple Store")
                return None
            
            price_text = price_elem.text.strip().replace('$', '').replace(',', '')
            price = float(price_text)
            
            return {
                'retailer': 'Apple Store',
                'price': price,
                'url': url
            }
        except Exception as e:
            logger.error(f"Error scraping Apple Store: {e}")
            return None


class MultiRetailerScraper:
    """Coordinates scraping from multiple retailers."""
    
    def __init__(self):
        self.scrapers = {
            'amazon': AmazonScraper(),
            'amazon_india': AmazonIndiaScraper(),
        }
    
    def scrape_all(self, product_name: str) -> List[Dict]:
        """Scrape all configured retailers."""
        results = []
        
        logger.info(f"Starting scrape for: {product_name}")
        
        for retailer_name, scraper in self.scrapers.items():
            logger.info(f"Scraping {retailer_name}...")
            result = scraper.scrape(product_name)
            if result:
                results.append(result)
            else:
                logger.warning(f"Failed to scrape {retailer_name}")
        
        logger.info(f"Scrape complete. Found {len(results)} results")
        return results
