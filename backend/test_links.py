import requests
from bs4 import BeautifulSoup
import sys

sys.stdout.reconfigure(encoding='utf-8')

urls = {
    'UTokyo': 'https://www.u-tokyo.ac.jp/ja/admissions/index.html',
    'KyotoU': 'https://www.kyoto-u.ac.jp/ja/admissions',
    'OsakaU': 'https://www.osaka-u.ac.jp/ja/admissions',
    'TohokuU': 'https://www.tohoku.ac.jp/japanese/studentinfo/admission/'
}

for name, url in urls.items():
    print(f'==== {name} ====')
    res = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
    res.encoding = res.apparent_encoding
    soup = BeautifulSoup(res.text, 'html.parser')
    main_block = soup.select_one("main") or soup.select_one("#main") or soup.select_one(".main") or soup.find("body")
    
    # print all links with dates or text
    count = 0
    for a in main_block.find_all('a'):
        text = a.get_text(strip=True)
        if text and len(text) > 10:
            print(f"- {text} ({a.get('href')})")
            count += 1
            if count > 15: break
