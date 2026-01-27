# File: cv_ai_agent/scripts/post_deploy_check.py
"""
Post-deployment health check script for CV AI Agent Flask application.

Purpose:
- Automatically verifies that the containerized or Gunicorn-deployed application is live.
- Hits /health and /ready endpoints.
- Logs results to stdout/stderr.
- Retries a few times if service is not immediately available.
- Returns exit codes: 0 = all healthy, 1 = failure.

Usage:
    python post_deploy_check.py --host http://localhost:8000 --retries 5 --delay 3
"""

import sys
import time
import argparse
import requests

def check_endpoint(url: str, retries: int = 3, delay: int = 2) -> bool:
    """
    Check a single endpoint with retries.

    Args:
        url (str): Full URL to check (e.g., http://localhost:8000/health)
        retries (int): Number of retry attempts
        delay (int): Delay in seconds between retries

    Returns:
        bool: True if endpoint returns HTTP 200, False otherwise
    """
    for attempt in range(1, retries + 1):
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print(f"[OK] {url} responded with 200")
                return True
            else:
                print(f"[WARN] {url} responded with status {response.status_code}")
        except requests.RequestException as e:
            print(f"[ERROR] Attempt {attempt}: Could not reach {url}: {e}")

        if attempt < retries:
            time.sleep(delay)
    return False


def main():
    parser = argparse.ArgumentParser(description="Post-deployment health check for CV AI Agent")
    parser.add_argument("--host", type=str, default="http://localhost:8000",
                        help="Base URL of the deployed application")
    parser.add_argument("--retries", type=int, default=3, help="Number of retries per endpoint")
    parser.add_argument("--delay", type=int, default=2, help="Delay between retries in seconds")
    args = parser.parse_args()

    endpoints = ["/health", "/ready"]
    all_ok = True

    for ep in endpoints:
        url = f"{args.host.rstrip('/')}{ep}"
        if not check_endpoint(url, retries=args.retries, delay=args.delay):
            print(f"[FAIL] {ep} did not respond with 200 after {args.retries} attempts")
            all_ok = False

    if all_ok:
        print("[SUCCESS] All endpoints healthy and ready.")
        sys.exit(0)
    else:
        print("[FAILURE] One or more endpoints failed health check.")
        sys.exit(1)


if __name__ == "__main__":
    main()
