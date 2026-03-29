#!/usr/bin/env python3
"""Quick search for iPhone 17 Pro 256GB on Amazon India"""

import requests
from bs4 import BeautifulSoup

url = 'https://www.amazon.in/s?k=Apple+iPhone+17+Pro+256GB&i=electronics'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

try:
    response = requests.get(url, headers=headers, timeout=10)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Find all products
    products = soup.find_all('div', {'data-component-type': 's-search-result'}, limit=5)
    
    print(f'Found {len(products)} products on Amazon India:\n')
    print('=' * 80)
    
    for i, product in enumerate(products, 1):
        title = product.find('h2')
        price = product.find('span', {'class': 'a-price-whole'})
        link = product.find('a', {'class': 'a-link-normal'})
        
        if title and price:
            print(f'\n{i}. {title.text.strip()}')
            print(f'   Price: {price.text.strip()}')
            if link and 'href' in link.attrs:
                print(f'   URL: https://www.amazon.in{link["href"][:80]}')
    
    print('\n' + '=' * 80)
    if len(products) == 0:
        print('No 256GB version found. The 512GB version is likely the available option.')
    
except Exception as e:
    print(f'Error searching: {e}')
