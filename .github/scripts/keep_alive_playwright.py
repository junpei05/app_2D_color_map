# .github/scripts/keep_alive_playwright.py
from playwright.sync_api import sync_playwright

APP_URL = "https://app2dcolormap-6kdothisijw76lj7hyxl3n.streamlit.app/"

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch()  # headless=True がデフォルト
        page = browser.new_page()

        print(f"Opening {APP_URL}")
        page.goto(APP_URL, wait_until="networkidle", timeout=120_000)
        page.wait_for_timeout(10_000)  # 10秒ほど動かしておく

        browser.close()
        print("Done")

if __name__ == "__main__":
    main()
