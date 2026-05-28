import requests
from bs4 import BeautifulSoup

urls = {
    'KyotoU': 'https://www.kyoto-u.ac.jp/ja/admissions/undergrad/foreign',
    'OsakaU': 'https://www.osaka-u.ac.jp/ja/admissions/faculty/shifei',
    'TohokuU': 'https://www.tohoku.ac.jp/japanese/studentinfo/admission/02/admission0203/'
}

for name, url in urls.items():
    print(f'==== {name} ====')
    res = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
    soup = BeautifulSoup(res.content, 'html.parser') # Use .content to let BS4 handle encoding
    
    main_block = soup.select_one("main") or soup.select_one("#main") or soup.find("body")
    count = 0
    for link in main_block.find_all("a"):
        url_href = link.get("href")
        if not url_href or url_href.startswith("#"): continue
        title = link.get_text(strip=True)
        if len(title) > 10:
            print(f"- {title} ({url_href})")
            count += 1
            if count >= 5: break
