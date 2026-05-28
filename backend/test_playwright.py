from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import sys

sys.stdout.reconfigure(encoding='utf-8')

urls = [
    ('UTokyo', 'https://www.u-tokyo.ac.jp/ja/admissions/index.html'),
    ('OsakaU', 'https://www.osaka-u.ac.jp/ja/admissions'),
    ('TohokuU', 'https://www.tohoku.ac.jp/japanese/studentinfo/admission/')
]

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    
    for name, url in urls:
        print(f'\n--- Playwright Testing {name} ---')
        try:
            page.goto(url, wait_until="networkidle", timeout=15000)
            html = page.content()
            soup = BeautifulSoup(html, 'html.parser')
            
            found = False
            for tag in soup.find_all(['ul', 'dl', 'div']):
                classes = tag.get('class', [])
                if not classes:
                    continue
                class_str = ' '.join(classes).lower()
                
                if 'news' in class_str or 'list' in class_str or 'info' in class_str or 'topics' in class_str:
                    items = tag.find_all(['li', 'dd', 'article'])
                    if len(items) >= 3:
                        print(f'  Found <{tag.name} class="{classes}"> with {len(items)} items')
                        for i in range(min(2, len(items))):
                            link = items[i].find('a')
                            if link:
                                print(f'    Item {i+1}: {link.get_text(strip=True)[:50]}')
                        found = True
                        if found: break # just print one matching block
                        
        except Exception as e:
            print(f"Error: {e}")
            
    browser.close()
