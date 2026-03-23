import socket
import ssl
from urllib.parse import urlparse
import certifi
import os
import platform
from cache import cache_get, cache_set


def parse_url(url):
    if not url.startswith('http'):
        url = 'https://' + url
    p = urlparse(url)
    host = p.netloc
    path = p.path or '/'
    if p.query:
        path += '?' + p.query
    use_ssl = p.scheme == 'https'
    port = p.port or (443 if use_ssl else 80)
    return host, path, port, use_ssl


def raw_request(host, path, port, use_ssl, extra_headers=None):
    if extra_headers is None:
        extra_headers = {}
    # build raw HTTP request string
    request = f"GET {path} HTTP/1.1\r\n"
    request += f"Host: {host}\r\n"
    request += "Connection: close\r\n"
    request += "User-Agent: go2web/1.0\r\n"
    request += "Accept-Encoding: identity\r\n"
    request += "Accept: application/json, text/html;q=0.9, */*;q=0.8\r\n"
    for k, v in extra_headers.items():
        request += f"{k}: {v}\r\n"
    request += "\r\n"

    # open TCP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(10)
    sock.connect((host, port))

    # use SSL if needed
    if use_ssl:
        context = ssl.create_default_context(cafile=certifi.where())
        if platform.system() == 'Darwin' and os.path.exists('/etc/ssl/cert.pem'):
            context.load_verify_locations('/etc/ssl/cert.pem')
        sock = context.wrap_socket(sock, server_hostname=host)

    # send request
    sock.sendall(request.encode())

    # read full response
    response = b""
    while True:
        chunk = sock.recv(4096)
        if not chunk:
            break
        response += chunk
    sock.close()

    return response.decode('utf-8', errors='replace')


def parse_response(raw):
    header_section, _, body = raw.partition('\r\n\r\n')

    lines = header_section.split('\r\n')
    status_line = lines[0]
    status_code = int(status_line.split()[1])

    headers = {}
    for line in lines[1:]:
        if ':' in line:
            k, _, v = line.partition(':')
            headers[k.strip().lower()] = v.strip()

    return status_code, headers, body


def fetch(url, extra_headers=None, max_redirects=5, use_cache=True):
    if extra_headers is None:
        extra_headers = {}
    original_url = url

    if use_cache:
        cached = cache_get(url)
        if cached:
            print(f"  -> cache hit for {url}")
            return cached

    for _ in range(max_redirects):
        host, path, port, use_ssl = parse_url(url)
        raw = raw_request(host, path, port, use_ssl, extra_headers)
        status, headers, body = parse_response(raw)

        if status in (301, 302, 303, 307, 308):
            location = headers.get('location')
            if not location:
                break
            # handle relative redirects
            if location.startswith('/'):
                scheme = 'https' if use_ssl else 'http'
                location = f"{scheme}://{host}{location}"
            print(f"  -> redirect {status} to {location}")
            url = location
            continue

        if use_cache and status == 200:
            from cache import cache_set
            cache_set(url, status, headers, body)
            # also cache the original URL if we followed redirects
            if url != original_url:
                cache_set(original_url, status, headers, body)
        return status, headers, body

    raise Exception(f"Too many redirects fetching {url}")


def decode_chunked(body):
    decoded = []
    while body:
        line_end = body.find('\r\n')
        if line_end == -1:
            break
        size_str = body[:line_end].strip()
        if not size_str:
            body = body[line_end + 2:]
            continue
        try:
            chunk_size = int(size_str, 16)
        except ValueError:
            return body  # not actually chunked, return as-is
        if chunk_size == 0:
            break
        chunk_data = body[line_end + 2:line_end + 2 + chunk_size]
        decoded.append(chunk_data)
        body = body[line_end + 2 + chunk_size + 2:]
    return ''.join(decoded)
