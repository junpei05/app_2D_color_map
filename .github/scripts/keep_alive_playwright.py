# .github/scripts/keep_alive_playwright.py
import sys
import time
from playwright.sync_api import sync_playwright

APP_URL = "https://app2dcolormap-6kdothisijw76lj7hyxl3n.streamlit.app/"
MAX_RETRIES = 3
RETRY_INTERVAL = 60  # seconds


def wake_up_if_sleeping(page):
    """スリープ中のアプリを検知し、起動ボタンをクリックする"""
    # Streamlit Community Cloud のウェイクアップボタンを探す
    wake_buttons = [
        'button:has-text("Yes, get this app back up!")',
        'button:has-text("Wake up")',
        'button:has-text("Yes")',
        '[data-testid="stAppWakeUpButton"]',
    ]
    for selector in wake_buttons:
        try:
            btn = page.locator(selector).first
            if btn.is_visible(timeout=5_000):
                print(f"App is sleeping. Clicking wake-up button: {selector}")
                btn.click()
                # 起動を待つ（コールドスタートは時間がかかる）
                print("Waiting for app to boot up after wake...")
                page.wait_for_timeout(10_000)
                return True
        except Exception:
            continue
    return False


def visit_app(page):
    """アプリにアクセスし、Streamlit の起動完了を確認する"""
    print(f"Navigating to {APP_URL}")
    page.goto(APP_URL, wait_until="load", timeout=180_000)

    # スリープ中ならウェイクアップボタンをクリック
    wake_up_if_sleeping(page)

    # Streamlit アプリ本体の描画を待つ
    print("Waiting for Streamlit app to render...")
    page.wait_for_selector(
        '[data-testid="stAppViewContainer"]',
        state="visible",
        timeout=300_000,
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
