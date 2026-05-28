import re
from bs4 import BeautifulSoup
from markdownify import markdownify as md

def clean_html_to_markdown(html_content: str, base_url: str = "") -> str:
    """
    Cleans raw HTML by removing noise (scripts, styles, navs) and converts 
    it to a simplified markdown representation suitable for LLM consumption.
    """
    soup = BeautifulSoup(html_content, "html.parser")
    
    # Remove noise tags entirely
    for noise in soup(["script", "style", "noscript", "meta", "link", "svg", "iframe", "footer"]):
        noise.decompose()
        
    # Attempt to target the main content area to save tokens, but fallback to body
    main_content = soup.select_one("main") or soup.select_one("article") or soup.select_one("#main") or soup.find("body")
    
    if not main_content:
        return ""

    # Convert to markdown, keeping only text and links
    # We want to keep links so the Navigator agent can extract them
    markdown_text = md(str(main_content), strip=['img', 'b', 'strong', 'i', 'em'], heading_style="ATX")
    
    # Clean up excessive newlines and spaces
    lines = [line.strip() for line in markdown_text.split('\n')]
    cleaned_lines = []
    for line in lines:
        if line:
            # Fix relative links if base_url is provided
            if base_url:
                # Basic relative link fixing in markdown `[text](/path)` -> `[text](base_url/path)`
                def fix_link(match):
                    text, url = match.groups()
                    if url.startswith('/'):
                        url = base_url.rstrip('/') + url
                    elif not url.startswith('http') and not url.startswith('#') and not url.startswith('javascript'):
                        url = base_url.rstrip('/') + '/' + url
                    return f"[{text}]({url})"
                line = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', fix_link, line)
            cleaned_lines.append(line)
            
    return '\n'.join(cleaned_lines)
