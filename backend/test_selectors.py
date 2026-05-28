import requests
from bs4 import BeautifulSoup
import sys

# Force UTF-8 output
sys.stdout.reconfigure(encoding='utf-8')

headers = {'User-Agent': 'Mozilla/5.0'}

urls = [
    ('UTokyo', 'https://www.u-tokyo.ac.jp/ja/admissions/index.html'),
    ('KyotoU', 'https://www.kyoto-u.ac.jp/ja/admissions'),
    ('OsakaU', 'https://www.osaka-u.ac.jp/ja/admissions'),
    ('TohokuU', 'https://www.tohoku.ac.jp/japanese/studentinfo/admission/')
]

for name, url in urls:
    print(f'\n--- Testing {name} ---')
    try:
        res = requests.get(url, headers=headers)
        res.encoding = res.apparent_encoding # Fix mojibake
        soup = BeautifulSoup(res.text, 'html.parser')
        
        main_block = soup.select_one("main") or soup.select_one("#main") or soup.select_one(".main")
        if not main_block:
            print("No main block found, searching body for 'news' or 'list' classes.")
            main_block = soup.find('body')
            
        print("Looking for lists in main block...")
        found = False
        # Search for any list or div that might contain news
        for tag in main_block.find_all(['ul', 'div']):
            classes = tag.get('class', [])
            if not classes:
                continue
            class_str = ' '.join(classes).lower()
            
            # Heuristic: looks like a news list
            if 'news' in class_str or 'list' in class_str or 'topic' in class_str or 'info' in class_str:
                items = tag.find_all('li') or tag.find_all('article') or tag.find_all('dd')
                if len(items) >= 2:
                    print(f'  Found <{tag.name} class="{classes}"> with {len(items)} items')
                    for i in range(min(2, len(items))):
                        link = items[i].find('a')
                        if link:
                            print(f'    Item {i+1}: {link.get_text(strip=True)[:50]}')
                    found = True
                    
    except Exception as e:
        print(f"Error: {e}")
