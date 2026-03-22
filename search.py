from urllib.parse import quote_plus, unquote
from http_client import fetch
from bs4 import BeautifulSoup


def extract_real_url(ddg_url):
    # DDG wraps real URLs
    if 'uddg=' in ddg_url:
        start = ddg_url.index('uddg=') + 5
        end = ddg_url.find('&rut=', start)
        encoded = ddg_url[start:end] if end != -1 else ddg_url[start:]
        return unquote(encoded)
    return ddg_url


def search(term):
    query = quote_plus(term)
    url = f"https://html.duckduckgo.com/html/?q={query}"

    _, headers, body = fetch(url)
    soup = BeautifulSoup(body, 'html.parser')

    results = []
    seen_urls = set()  # track seen URLs to avoid duplicates

    for a in soup.select('a[href*="duckduckgo.com/l/"]'):
        title = a.get_text(strip=True)
        href = extract_real_url(a.get('href', ''))
        if title and href and href.startswith('http') and href not in seen_urls:
            seen_urls.add(href)
            results.append((title, href))

    if not results:
        print("No results found.")
        return []

    for i, (title, url) in enumerate(results[:10], 1):
        print(f"{i}. {title}")
        print(f"   {url}\n")

    return results[:10]