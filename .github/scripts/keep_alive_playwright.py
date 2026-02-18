# .github/scripts/keep_alive_playwright.py
import sys
import time
from playwright.sync_api import sync_playwright

APP_URL = "https://app2dcolormap-6kdothisijw76lj7hyxl3n.streamlit.app/"
MAX_RETRIES = 3
RETRY_INTERVAL = 30  # seconds


def visit_app(page):
    """アプリにアクセスし、Streamlit の起動完了を確認する"""
    print(f"Navigating to {APP_URL}")
    page.goto(APP_URL, wait_until="load", timeout=180_000)

    # Streamlit アプリ本体の描画を待つ（スリープ復帰を含む）
    print("Waiting for Streamlit app to render...")
    page.wait_for_selector(
        '[data-testid="stAppViewContainer"]',
        timeout=180_000,
    )

    # 描画後に少し待機してアクティビティを発生させる
    page.wait_for_timeout(10_000)
    print("App is alive and rendered successfully.")


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        try:
            for attempt in range(1, MAX_RETRIES + 1):
                page = browser.new_page()
                try:
                    print(f"--- Attempt {attempt}/{MAX_RETRIES} ---")
                    visit_app(page)
                    print("Done")
                    return
                except Exception as e:
                    print(f"Attempt {attempt} failed: {e}")
                    if attempt < MAX_RETRIES:
                        print(f"Retrying in {RETRY_INTERVAL}s...")
                        time.sleep(RETRY_INTERVAL)
                finally:
                    page.close()

            print("All attempts failed.")
            sys.exit(1)
        finally:
            browser.close()


if __name__ == "__main__":
    main()
