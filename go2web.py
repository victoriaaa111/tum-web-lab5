#!/usr/bin/env python3
import argparse
import sys


def print_help():
    print("""go2web - a simple HTTP client

Usage:
  go2web -u <URL>          Make an HTTP request to the URL and print the response
  go2web -s <search-term>  Search the term and print top 10 results
  go2web -h                Show this help message
""")


def main():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('-u', metavar='URL', help='URL to fetch')
    parser.add_argument('-s', metavar='TERM', nargs='+', help='Search term')
    parser.add_argument('-h', action='store_true', help='Show help')

    args = parser.parse_args()

    if args.h or len(sys.argv) == 1:
        print_help()
        return

    if args.u:
        from http_client import fetch
        status, headers, body = fetch(args.u)
        print(f"Status: {status}")
        print(body[:300])
        return

    if args.s:
        term = ' '.join(args.s)
        print(f"[TODO] Searching for: {term}")
        return


if __name__ == '__main__':
    main()