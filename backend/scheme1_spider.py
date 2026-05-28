import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time
import sys

sys.stdout.reconfigure(encoding='utf-8')

class UniversitySpider:
    """
    Implementation of Scheme 1: Comprehensive Site Scanner.
    Crawls from a root URL up to a max_depth, scoring pages based on relevance to 
    'Privately Financed International Students' and 'Admissions'.
    """
    def __init__(self, root_url, max_depth=2):
        self.root_url = root_url
        self.domain = urlparse(root_url).netloc
        self.max_depth = max_depth
        self.visited = set()
        self.scored_pages = []
        self.headers = {"User-Agent": "Mozilla/5.0"}
        
        # Keywords that indicate a highly relevant page
        self.bonus_keywords = ['私費', '留学生', '外国人', '入試', '受験', 'お知らせ', 'ニュース', 'news', 'admission']
        # Keywords that indicate a likely irrelevant page
        self.penalty_keywords = ['大学院', '交換留学', '奨学金', '研究', '論文', 'access', 'campusmap']

    def crawl(self, url, depth=0):
        if depth > self.max_depth or url in self.visited:
            return
        
        self.visited.add(url)
        try:
            res = requests.get(url, headers=self.headers, timeout=5)
            res.encoding = res.apparent_encoding
            if res.status_code != 200:
                return
                
            soup = BeautifulSoup(res.text, 'html.parser')
            text_content = soup.get_text()
            title = soup.title.string if soup.title else url
            
            # Score the page
            score = 0
            for kw in self.bonus_keywords:
                score += text_content.count(kw) * 2
                if soup.title and kw in soup.title.string:
                    score += 20 # High bonus for title match
                    
            for kw in self.penalty_keywords:
                score -= text_content.count(kw) * 2
                
            # If the page has lists of links (potential news index)
            list_items = soup.find_all(['li', 'dt', 'dd', 'article'])
            if len(list_items) > 5:
                score += 10
                
            if score > 20:
                self.scored_pages.append({'url': url, 'title': title.strip(), 'score': score})
                print(f"[{score} pts] Found relevant page: {title.strip()[:30]} ({url})")
            
            # Find next links
            if depth < self.max_depth:
                for a in soup.find_all('a', href=True):
                    next_url = urljoin(url, a['href'])
                    parsed_next = urlparse(next_url)
                    # Stay within domain and avoid assets
                    if parsed_next.netloc == self.domain and not next_url.lower().endswith(('.pdf', '.jpg', '.png', '.zip')):
                        # Basic heuristic to only follow links that seem like navigation or admission
                        link_text = a.get_text()
                        if any(kw in link_text for kw in ['入', '留', '学', 'news', 'info', 'admiss']):
                            time.sleep(0.5) # Rate limit
                            self.crawl(next_url, depth + 1)
                            
        except Exception as e:
            pass # Ignore request errors during spidering

    def run(self):
        print(f"Starting Scheme 1 Spider for {self.root_url}")
        self.crawl(self.root_url)
        print("\nTop Recommended Information Sources:")
        # Sort by score descending
        self.scored_pages.sort(key=lambda x: x['score'], reverse=True)
        for page in self.scored_pages[:5]:
            print(f"Score: {page['score']} | {page['title']} | {page['url']}")

if __name__ == "__main__":
    # Example usage for one university
    spider = UniversitySpider("https://www.hokudai.ac.jp/")
    spider.run()
