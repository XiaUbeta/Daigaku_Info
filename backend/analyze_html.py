import requests
from bs4 import BeautifulSoup
import sys

sys.stdout.reconfigure(encoding='utf-8')

urls = {
    'KyotoU': 'https://www.kyoto-u.ac.jp/ja/admissions',
    'OsakaU': 'https://www.osaka-u.ac.jp/ja/admissions',
    'TohokuU': 'https://www.tohoku.ac.jp/japanese/studentinfo/admission/'
}

for name, url in urls.items():
    print(f'\n==== {name} ====')
    try:
        res = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
        res.encoding = res.apparent_encoding
        soup = BeautifulSoup(res.content, 'html.parser')
        
        main_block = soup.select_one("main") or soup.select_one("#main") or soup.select_one(".main") or soup.find("body")
        
        print("Looking for all <a> tags with length > 10 in main block:")
        count = 0
        for a in main_block.find_all('a'):
            text = a.get_text(strip=True)
            href = a.get('href', '')
            if text and len(text) > 10 and not href.startswith('#'):
                print(f"  - [{text}]({href})")
                count += 1
                if count > 20: break
    except Exception as e:
        print(e)
