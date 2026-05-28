import requests
from bs4 import BeautifulSoup
import sys

sys.stdout.reconfigure(encoding='utf-8')

urls = {
    'OsakaU_Admissions': 'https://www.osaka-u.ac.jp/ja/admissions',
    'TohokuU_Admissions': 'https://www.tnc.tohoku.ac.jp/'
}

for name, url in urls.items():
    print(f'==== {name} ====')
    try:
        res = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
        res.encoding = res.apparent_encoding
        soup = BeautifulSoup(res.content, 'html.parser')
        for a in soup.find_all('a'):
            text = a.get_text(strip=True)
            if '私費' in text or '留学生' in text or 'foreign' in a.get('href', '').lower() or 'ryugaku' in a.get('href', '').lower():
                print(f"- {text} ({a.get('href')})")
    except Exception as e:
        print(e)
