from playwright.sync_api import sync_playwright
import sys

sys.stdout.reconfigure(encoding='utf-8')

def analyze_page(name, url, selector):
    print(f'\n=== Analyzing {name} ===')
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        try:
            page = browser.new_page()
            page.goto(url, wait_until="networkidle", timeout=15000)
            
            print(f"Page Title: {page.title()}")
            
            container = page.query_selector(selector)
            if not container:
                print(f"FAILED: Container '{selector}' not found. Trying 'main' or 'body'.")
                container = page.query_selector("main") or page.query_selector("body")
                
            links = container.query_selector_all("a")
            print(f"Found {len(links)} links in container.")
            
            count = 0
            for link in links:
                text = link.inner_text().strip()
                href = link.get_attribute("href")
                if text and len(text) > 5 and href and not href.startswith('#') and not href.endswith('.pdf'):
                    print(f"  - [{text}]({href})")
                    count += 1
                    if count >= 10: break
        except Exception as e:
            print(f"Error: {e}")
        finally:
            browser.close()

analyze_page('KyotoU', 'https://www.kyoto-u.ac.jp/ja/admissions/undergrad/other/foreign', 'main')
analyze_page('OsakaU', 'https://www.osaka-u.ac.jp/ja/admissions/faculty/special/international', 'main')
analyze_page('TohokuU', 'https://www.tnc.tohoku.ac.jp/ryugaku.php', '#Contents')
