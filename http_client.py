import socket
import ssl
from urllib.parse import urlparse


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
    for k, v in extra_headers.items():
        request += f"{k}: {v}\r\n"
    request += "\r\n"

    # open TCP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(10)
    sock.connect((host, port))

    # use SSL if needed
    if use_ssl:
        context = ssl.create_default_context()
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
    # split headers from body at the blank line
    header_section, _, body = raw.partition('\r\n\r\n')

    lines = header_section.split('\r\n')
    status_line = lines[0]
    status_code = int(status_line.split()[1])

    headers = {}
    for line in lines[1:]:
        if ':' in line:
            k, _, v = line.partition(':')
            headers[k.strip().lower()] = v.strip()

    # decode chunked transfer encoding if needed
    if headers.get('transfer-encoding', '').lower() == 'chunked':
        body = decode_chunked(body)

    return status_code, headers, body


def fetch(url, extra_headers=None, max_redirects=5):
    if extra_headers is None:
        extra_headers = {}

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

        return status, headers, body

    raise Exception(f"Too many redirects fetching {url}")


def decode_chunked(body):
    result = ""
    while body:
        # read the chunk size line (hex number)
        size_line, _, body = body.partition('\r\n')
        size_line = size_line.strip()
        if not size_line:
            continue
        try:
            size = int(size_line, 16)
        except ValueError:
            break
        if size == 0:
            break
        result += body[:size]
        body = body[size + 2:]  # skip \r\n after chunk data
    return result
