import os

content = '''import requests
from bs4 import BeautifulSoup
from markdownify import markdownify as md
import xml.etree.ElementTree as ET

class BaseScraper:
    def __init__(self, university_name: str):
        self.university_name = university_name
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }

    def scrape_latest_news(self):
        raise NotImplementedError("Subclasses must implement this method")

    def fetch_article_content(self, url):
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            if response.status_code != 200: return ""
            soup = BeautifulSoup(response.text, "html.parser")
            for noise in soup(["script", "style", "nav", "header", "footer", "aside", "noscript"]):
                noise.decompose()
            main_block = soup.select_one("main") or soup.select_one("article") or soup.select_one("#main") or soup.find("body")
            if not main_block: return ""
            markdown_text = md(str(main_block), strip=['a', 'img']) 
            lines = [line.strip() for line in markdown_text.split('\\n')]
            cleaned_text = '\\n'.join([line for line in lines if line])
            return cleaned_text[:3000]
        except Exception as e:
            return ""

class GenericRequestsScraper(BaseScraper):
    def __init__(self, university_name: str, base_url: str, news_urls: list):
        super().__init__(university_name)
        self.base_url = base_url
        self.news_urls = news_urls

    def scrape_latest_news(self):
        news_items = []
        seen_urls = set()
        for news_url in self.news_urls:
            try:
                response = requests.get(news_url, headers=self.headers, timeout=10)
                response.encoding = response.apparent_encoding
                if response.status_code != 200: continue
                
                # Handle RSS XML
                if news_url.endswith('.xml'):
                    try:
                        root = ET.fromstring(response.content)
                        for item in root.findall('.//item') or root.findall('.//entry'):
                            title_elem = item.find('title')
                            link_elem = item.find('link')
                            if title_elem is not None and link_elem is not None:
                                url = link_elem.text if link_elem.text else link_elem.get('href', '')
                                title = title_elem.text
                                if url and url not in seen_urls:
                                    news_items.append({"title": title, "url": url, "date": ""})
                                    seen_urls.add(url)
                    except Exception as e:
                        print(f"  [{self.university_name}] XML Parse Error on {news_url}: {e}")
                    continue

                # Handle standard HTML
                soup = BeautifulSoup(response.content, "html.parser")
                main_block = soup.select_one("main") or soup.find("body")
                if not main_block: continue
                
                for link in main_block.find_all("a"):
                    url = link.get("href")
                    if not url or url.startswith("#") or url.lower().endswith(".pdf") or "javascript" in url: continue
                    title = link.get_text(strip=True)
                    if len(title) < 8: continue
                    if not url.startswith("http"):
                        if url.startswith("/"): url = self.base_url + url
                        else: url = self.base_url + "/" + url
                    if url not in seen_urls:
                        news_items.append({"title": title, "url": url, "date": ""})
                        seen_urls.add(url)
                    if len(news_items) >= 20: break # Grab up to 20 total across all URLs
            except Exception as e:
                print(f"  [{self.university_name}] Request Error on {news_url}: {e}")
                
        return news_items

class WasedaScraper(GenericRequestsScraper):
    def __init__(self):
        super().__init__("Waseda University", "https://www.waseda.jp", [
            "https://www.waseda.jp/inst/admission/news/",
            "https://www.waseda.jp/inst/admission/visiting/",
            "https://www.waseda.jp/inst/admission/undergraduate/system/international/"
        ])

class UTokyoScraper(GenericRequestsScraper):
    def __init__(self):
        super().__init__("The University of Tokyo", "https://www.u-tokyo.ac.jp", [
            "https://www.u-tokyo.ac.jp/ja/admissions/undergraduate/e01_06_01.html",
            "https://www.u-tokyo.ac.jp/focus/ja/index.html",
            "https://www.u-tokyo.ac.jp/ja/admissions/undergraduate/e01_02_04.html"
        ])

class KyotoUScraper(GenericRequestsScraper):
    def __init__(self):
        super().__init__("Kyoto University", "https://www.kyoto-u.ac.jp", [
            "https://www.kyoto-u.ac.jp/ja/international/students1/study1/undergraduate/addmissions",
            "https://www.kyoto-u.ac.jp/ja/news?audience=45&target%5B45%5D=45",
            "https://www.kyoto-u.ac.jp/ja/event?audience=45&target%5B45%5D=45"
        ])

class OsakaUScraper(GenericRequestsScraper):
    def __init__(self):
        super().__init__("Osaka University", "https://www.osaka-u.ac.jp", [
            "https://www.osaka-u.ac.jp/ja/admissions/faculty/expense",
            "https://www.osaka-u.ac.jp/ja/news/topics"
        ])

class TohokuUScraper(GenericRequestsScraper):
    def __init__(self):
        super().__init__("Tohoku University", "https://www.tohoku.ac.jp", [
            "https://www.tohoku.ac.jp/japanese/2026/",
            "https://www.tohoku.ac.jp/japanese/2026/cate_news/",
            "https://www.tohoku.ac.jp/japanese/rss/cate_tar_learn/index.xml",
            "https://admissions.tohoku.ac.jp/ja/entrance-info/undergraduate-info/admissions_sp/"
        ])

class HokkaidoUScraper(GenericRequestsScraper):
    def __init__(self):
        super().__init__("Hokkaido University", "https://www.hokudai.ac.jp", [
            "https://www.hokudai.ac.jp/admission/admission-info/",
            "https://www.oia.hokudai.ac.jp/cier/news/"
        ])

class NagoyaUScraper(GenericRequestsScraper):
    def __init__(self):
        super().__init__("Nagoya University", "https://www.nagoya-u.ac.jp", [
            "https://www.nagoya-u.ac.jp/admissions/exam/us-exam/cat2/",
            "https://www.nagoya-u.ac.jp/admissions/news/index.html"
        ])

class TsukubaUScraper(GenericRequestsScraper):
    def __init__(self):
        super().__init__("University of Tsukuba", "https://ac.tsukuba.ac.jp", [
            "https://ac.tsukuba.ac.jp/news/category/info/",
            "https://ac.tsukuba.ac.jp/news/category/info/info_exam/",
            "https://ac.tsukuba.ac.jp/apply/application-guidelines/"
        ])

class ChibaUScraper(GenericRequestsScraper):
    def __init__(self):
        super().__init__("Chiba University", "https://www.chiba-u.jp", [
            "https://www.chiba-u.jp/news/exam/2026/",
            "https://www.chiba-u.jp/event/index.html",
            "https://www.f-eng.chiba-u.jp/admission/information.html",
            "https://informatics.chiba-u.jp/admission/undergraduate.html"
        ])

class YNUScraper(GenericRequestsScraper):
    def __init__(self):
        super().__init__("Yokohama National University", "https://www.ynu.ac.jp", [
            "https://www.ynu.ac.jp/exam/faculty/",
            "https://www.ynu.ac.jp/news_center/"
        ])

class ScienceTokyoScraper(GenericRequestsScraper):
    def __init__(self):
        super().__init__("Institute of Science Tokyo", "https://admissions.isct.ac.jp", [
            "https://admissions.isct.ac.jp/ja/news",
            "https://admissions.isct.ac.jp/ja/news?tab=94",
            "https://admissions.isct.ac.jp/ja/013/undergraduate"
        ])

class UECScraper(GenericRequestsScraper):
    def __init__(self):
        super().__init__("The University of Electro-Communications", "https://www.uec.ac.jp", [
            "https://www.uec.ac.jp/news/admission/",
            "https://www.uec.ac.jp/news/prospect/",
            "https://www.uec.ac.jp/education/undergraduate/event/opencampus.html",
            "https://www.uec.ac.jp/education/undergraduate/admission/senbatsu_type.html"
        ])

class TUATScraper(GenericRequestsScraper):
    def __init__(self):
        super().__init__("Tokyo University of Agriculture and Technology", "https://www.tuat.ac.jp", [
            "https://www.tuat.ac.jp/admission/nyushi_gakubu/info/",
            "https://www.tuat.ac.jp/admission/nyushi_gakubu/youkou/"
        ])

class KeioScraper(GenericRequestsScraper):
    def __init__(self):
        super().__init__("Keio University", "https://www.keio.ac.jp", [
            "https://www.keio.ac.jp/ja/admissions/faculty/news/",
            "https://www.keio.ac.jp/ja/admissions/faculty/examinations/international-student/"
        ])

class TMUScraper(GenericRequestsScraper):
    def __init__(self):
        super().__init__("Tokyo Metropolitan University", "https://www.tmu.ac.jp", [
            "https://www.tmu.ac.jp/news.html?parent=1729",
            "https://www.tmu.ac.jp/entrance/faculty/application_guideline.html"
        ])
'''

with open('app/services/scrapers.py', 'w', encoding='utf-8') as f:
    f.write(content)
print("Updated scrapers.py with user manual URLs and multi-URL logic.")
