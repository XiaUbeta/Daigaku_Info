import re

with open('app/services/scrapers.py', 'r', encoding='utf-8') as f:
    content = f.read()

idx = content.find('# Phase 2: Batch 1')
if idx != -1:
    new_content = content[:idx]
    
    new_content += '''# Phase 2: Batch 1 (Top Imperials)
# ==========================================

class UTokyoScraper(BaseScraper):
    def __init__(self):
        super().__init__("The University of Tokyo")
        self.base_url = "https://www.u-tokyo.ac.jp"
        self.news_url = "https://www.u-tokyo.ac.jp/ja/index.html"

    def scrape_latest_news(self):
        try:
            response = requests.get(self.news_url, headers=self.headers, timeout=10)
            response.encoding = response.apparent_encoding
            if response.status_code != 200: return []
            soup = BeautifulSoup(response.content, "html.parser")
            news_items = []
            main_block = soup.select_one("main") or soup.find("body")
            for link in main_block.find_all("a"):
                url = link.get("href")
                if not url or url.startswith("#") or url.lower().endswith(".pdf"): continue
                title = link.get_text(strip=True)
                if len(title) < 10: continue
                if not url.startswith("http"):
                    if url.startswith("/"): url = self.base_url + url
                    else: url = self.base_url + "/" + url
                news_items.append({"title": title, "url": url, "date": ""})
                if len(news_items) >= 15: break
            return news_items
        except Exception as e:
            print(f"  [{self.university_name}] Request Error: {e}")
            return []

class KyotoUScraper(BaseScraper):
    def __init__(self):
        super().__init__("Kyoto University")
        self.base_url = "https://www.kyoto-u.ac.jp"
        self.news_url = "https://www.kyoto-u.ac.jp/ja/admissions"

    def scrape_latest_news(self):
        try:
            response = requests.get(self.news_url, headers=self.headers, timeout=10)
            response.encoding = response.apparent_encoding
            if response.status_code != 200: return []
            soup = BeautifulSoup(response.content, "html.parser")
            news_items = []
            main_block = soup.select_one("main") or soup.find("body")
            for link in main_block.find_all("a"):
                url = link.get("href")
                if not url or url.startswith("#") or "javascript" in url or url.lower().endswith(".pdf"): continue
                title = link.get_text(strip=True)
                if len(title) < 10: continue
                if not url.startswith("http"):
                    if url.startswith("/"): url = self.base_url + url
                    else: url = self.base_url + "/" + url
                news_items.append({"title": title, "url": url, "date": ""})
                if len(news_items) >= 15: break
            return news_items
        except Exception as e:
            print(f"  [{self.university_name}] Request Error: {e}")
            return []

class OsakaUScraper(BaseScraper):
    def __init__(self):
        super().__init__("Osaka University")
        self.base_url = "https://www.osaka-u.ac.jp"
        self.news_url = "https://www.osaka-u.ac.jp/ja/admissions"

    def scrape_latest_news(self):
        try:
            response = requests.get(self.news_url, headers=self.headers, timeout=10)
            response.encoding = response.apparent_encoding
            if response.status_code != 200: return []
            soup = BeautifulSoup(response.content, "html.parser")
            news_items = []
            main_block = soup.select_one("main") or soup.find("body")
            for link in main_block.find_all("a"):
                url = link.get("href")
                if not url or url.startswith("#") or url.lower().endswith(".pdf"): continue
                title = link.get_text(strip=True)
                if len(title) < 10: continue
                if not url.startswith("http"):
                    if url.startswith("/"): url = self.base_url + url
                    else: url = self.base_url + "/" + url
                news_items.append({"title": title, "url": url, "date": ""})
                if len(news_items) >= 15: break
            return news_items
        except Exception as e:
            print(f"  [{self.university_name}] Request Error: {e}")
            return []

class TohokuUScraper(BaseScraper):
    def __init__(self):
        super().__init__("Tohoku University")
        self.base_url = "https://www.tnc.tohoku.ac.jp"
        self.news_url = "https://www.tnc.tohoku.ac.jp/"

    def scrape_latest_news(self):
        try:
            response = requests.get(self.news_url, headers=self.headers, timeout=10)
            response.encoding = response.apparent_encoding
            if response.status_code != 200: return []
            soup = BeautifulSoup(response.content, "html.parser")
            news_items = []
            main_block = soup.select_one("main") or soup.find("body")
            for link in main_block.find_all("a"):
                url = link.get("href")
                if not url or url.startswith("#") or url.lower().endswith(".pdf"): continue
                title = link.get_text(strip=True)
                if len(title) < 10: continue
                if not url.startswith("http"):
                    if url.startswith("/"): url = self.base_url + url
                    else: url = self.base_url + "/" + url
                news_items.append({"title": title, "url": url, "date": ""})
                if len(news_items) >= 15: break
            return news_items
        except Exception as e:
            print(f"  [{self.university_name}] Request Error: {e}")
            return []
'''
    with open('app/services/scrapers.py', 'w', encoding='utf-8') as f:
        f.write(new_content)
    print('Successfully updated scrapers.py')
