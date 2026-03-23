# LAB 5 go2web - A Command-Line HTTP Client

A lightweight HTTP client built with TCP sockets in Python. No HTTP libraries (`requests`, `urllib3`, `http.client`) are used, all HTTP communication is done manually over `socket` + `ssl`.

## Features

- **Raw socket HTTP/1.1** - builds and parses HTTP requests/responses manually
- **HTTPS support** - TLS via Python's `ssl` module with certificate verification
- **Redirect handling** - follows 301, 302, 303, 307, 308 redirects automatically (up to 5 hops)
- **Content negotiation** - sends `Accept: application/json, text/html` and renders accordingly
- **Chunked transfer decoding** - handles `Transfer-Encoding: chunked` responses
- **HTTP caching** - TTL-based cache with `Cache-Control` header support and size limits
- **Web search** - search via DuckDuckGo and interactively open results
- **HTML rendering** - strips tags and extracts readable text using BeautifulSoup

## Usage

```bash
go2web -u <URL>            # Fetch a URL and print the response
go2web -s <search-term>    # Search DuckDuckGo and print top 10 results
go2web -h                  # Show help
```

## Test Examples

### Fetch an HTML page
```
$ go2web -u https://example.com

Example Domain
This domain is for use in illustrative examples in documents.
...
```

### Fetch a JSON API
```
$ go2web -u https://jsonplaceholder.typicode.com/posts/1

{
  "userId": 1,
  "id": 1,
  "title": "sunt aut facere repellat provident occaecati excepturi optio reprehenderit",
  "body": "quia et suscipit..."
}
```

### Test redirects
```
$ go2web -u http://google.com

  -> redirect 301 to https://www.google.com/
...
```

### Search and open a result
```
$ go2web -s python sockets tutorial

1. Socket Programming in Python (Guide) - Real Python
   https://realpython.com/python-sockets/

2. Socket Programming HOWTO — Python 3.14.3 documentation
   https://docs.python.org/3/howto/sockets.html

3. Socket Programming in Python - GeeksforGeeks
   https://www.geeksforgeeks.org/python/socket-programming-python/

4. A Complete Guide to Socket Programming in Python - DataCamp
   https://www.datacamp.com/tutorial/a-complete-guide-to-socket-programming-in-python

5. Python Socket: Technical Guide for Beginners and Experts
   https://www.pythoncentral.io/learn-python-socket/

6. Python socket Module - W3Schools
   https://www.w3schools.com/python/ref_module_socket.asp

7. Python Socket Programming: A Comprehensive Guide
   https://coderivers.org/blog/python-socket-programming/

8. Python - Socket Programming - Online Tutorials Library
   https://www.tutorialspoint.com/python/python_socket_programming.htm

9. Python Socket Programming: Server and Client Example Guide
   https://www.digitalocean.com/community/tutorials/python-socket-programming-server-client

10. socket — Low-level networking interface — Python 3.14.3 documentation
   https://docs.python.org/3/library/socket.html

Enter number to open (or press Enter to skip): 1

Fetching: https://realpython.com/python-sockets/
...
```

### Cache behavior
```
$ go2web -u https://example.com    # first request — fetches from server
$ go2web -u https://example.com    # second request — serves from cache
  [cache hit]
  -> cache hit for https://example.com
```

## Project Structure

```
├── go2web           # Bash wrapper script
├── go2web.py        # CLI entry point (argument parsing)
├── http_client.py   # Raw socket HTTP client (TCP, SSL, redirects, chunked decoding)
├── renderer.py      # Response rendering (JSON pretty-print, HTML-to-text)
├── search.py        # DuckDuckGo search + interactive result selection
├── cache.py         # HTTP cache (TTL, Cache-Control, size limits)
└── .gitignore
```

## How It Works

1. **`go2web.py`** parses CLI arguments and routes to either `fetch()` (for `-u`) or `search()` (for `-s`)

2. **`http_client.py`** handles all HTTP communication:
   - `parse_url()` breaks a URL into host, path, port, and scheme
   - `raw_request()` opens a TCP socket, wraps it in TLS if HTTPS, sends a hand-built HTTP/1.1 request, and reads the raw response
   - `parse_response()` splits the response into status code, headers, and body
   - `fetch()` ties it together with redirect following and cache integration
   - `decode_chunked()` handles chunked transfer encoding

3. **`renderer.py`** checks the `Content-Type` header:
   - `application/json` -> pretty-printed with `json.dumps(indent=2)`
   - `text/html` -> parsed with BeautifulSoup, scripts/styles removed, text extracted

4. **`search.py`** sends a search query to DuckDuckGo's HTML endpoint, parses result links, and lets the user pick one to fetch and render

5. **`cache.py`** stores responses as JSON files in `.cache/`:
   - 1-hour TTL per entry
   - Respects `Cache-Control: no-store` / `no-cache`
   - Max 50 entries with oldest-first eviction

## Demo
![lab5pweb.gif](lab5pweb.gif)
