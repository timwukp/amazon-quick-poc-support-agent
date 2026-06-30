#!/usr/bin/env python3
"""Cookie-injection bootstrap for Approach A (Runtime mode).

Goal: prove we can authenticate an AgentCore Browser session to an SSO-gated console
(QuickSight) WITHOUT any interactive Live View login — by injecting the human's existing
session cookies into the browser context via Playwright CDP. This sidesteps the Harness
Live-View teardown limitation (see issue aws/bedrock-agentcore-sdk-python#518).

Flow:
  1. Start an AgentCore Browser session (data plane).
  2. Connect Playwright to it over CDP using the SDK-generated ws headers.
  3. context.add_cookies(<exported QuickSight cookies>).
  4. Navigate to the Quick console URL and verify it is authenticated (not the sign-in page).

The cookies are SENSITIVE. Pass them as a file path (JSON array in Playwright cookie format);
this script never prints cookie values. The file should look like:
  [{"name":"...","value":"...","domain":".quicksight.aws.amazon.com","path":"/", ...}, ...]

Usage:
  pip install playwright boto3 && playwright install chromium
  python cookie_inject_bootstrap.py --cookies cookies.json \
      --url "https://us-east-1.quicksight.aws.amazon.com/sn/account/<ns>/start/home" --region us-east-1
"""
import argparse
import json
import sys


def main() -> int:
    ap = argparse.ArgumentParser(description="Validate cookie-injection auth into an AgentCore Browser session")
    ap.add_argument("--cookies", required=True, help="Path to JSON file of Playwright-format cookies (sensitive)")
    ap.add_argument("--url", required=True, help="Quick/QuickSight console URL to verify")
    ap.add_argument("--region", default="us-east-1")
    ap.add_argument("--screenshot", default="/tmp/quick_auth_check.png")
    args = ap.parse_args()

    try:
        with open(args.cookies, encoding="utf-8") as f:
            cookies = json.load(f)
    except (OSError, json.JSONDecodeError) as e:
        print(f"FAIL  cannot read cookies file: {e}")
        return 2
    if not isinstance(cookies, list) or not cookies:
        print("FAIL  cookies file must be a non-empty JSON array of cookie objects")
        return 2
    print(f"loaded {len(cookies)} cookie(s) (values not shown)")

    try:
        from bedrock_agentcore.tools.browser_client import BrowserClient
    except Exception as e:  # noqa: BLE001
        print(f"FAIL  import BrowserClient (pip install bedrock-agentcore): {e}")
        return 2
    try:
        from playwright.sync_api import sync_playwright
    except Exception as e:  # noqa: BLE001
        print(f"FAIL  import Playwright (pip install playwright && playwright install chromium): {e}")
        return 2

    client = BrowserClient(region=args.region)
    client.start()
    print(f"OK    started AgentCore Browser session: {client.session_id}")
    try:
        ws_url, headers = client.generate_ws_headers()
        with sync_playwright() as p:
            browser = p.chromium.connect_over_cdp(ws_url, headers=headers)
            ctx = browser.contexts[0] if browser.contexts else browser.new_context()
            # inject the authenticated cookies (no interactive SSO)
            ctx.add_cookies(cookies)
            page = ctx.pages[0] if ctx.pages else ctx.new_page()
            page.goto(args.url, wait_until="domcontentloaded", timeout=60000)
            page.wait_for_timeout(4000)
            url_now = page.url
            title = page.title()
            body = (page.inner_text("body")[:400] if page.query_selector("body") else "")
            page.screenshot(path=args.screenshot)
            is_signin = "/sn/auth/signin" in url_now or "sign in" in (title or "").lower() or "Sign-In" in body
            print(f"final url   : {url_now}")
            print(f"page title  : {title}")
            print(f"screenshot  : {args.screenshot}")
            if is_signin:
                print("RESULT: STILL ON SIGN-IN — cookies did not authenticate (expired/incomplete/wrong domain?).")
                return 1
            print("RESULT: AUTHENTICATED ✅ — cookie injection works; Runtime+cookie approach is viable.")
            return 0
    finally:
        try:
            client.stop()
            print("stopped browser session")
        except Exception:  # noqa: BLE001
            pass


if __name__ == "__main__":
    sys.exit(main())
