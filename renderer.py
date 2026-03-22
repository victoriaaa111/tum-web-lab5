from bs4 import BeautifulSoup


def render(html):
    soup = BeautifulSoup(html, 'html.parser')

    # remove tags that are not human-readable
    for tag in soup(['script', 'style', 'nav', 'footer', 'head']):
        tag.decompose()

    # extract plain text
    text = '\n'.join(soup.stripped_strings)

    # collapse multiple blank lines into one
    lines = [line.strip() for line in text.splitlines()]
    cleaned = '\n'.join(line for line in lines if line)

    return cleaned
