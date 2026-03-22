from bs4 import BeautifulSoup


def render(html):
    soup = BeautifulSoup(html, 'html.parser')

    for tag in soup(['script', 'style', 'nav', 'footer', 'head', 'header', 'meta', 'link']):
        tag.decompose()

    text = '\n'.join(soup.stripped_strings)
    lines = [line.strip() for line in text.splitlines()]
    cleaned = '\n'.join(line for line in lines if line)

    return cleaned
