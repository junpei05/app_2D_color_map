# .github/scripts/keep_alive_playwright.py
"""Streamlit Community Cloud アプリのスリープ防止スクリプト。

Playwright で定期的にアプリにアクセスし、スリープ状態であれば
ウェイクアップボタンをクリックしてアプリを起動状態に保つ。

Streamlit Community Cloud はアプリを iframe 内にレンダリングするため、
メインフレームとすべてのフレーム両方のセレクターを確認する。
"""
import sys
import time
from playwright.sync_api import sync_playwright, Page

APP_URL = "https://app2dcolormap-6kdothisijw76lj7hyxl3n.streamlit.app/"
MAX_RETRIES = 3
RETRY_INTERVAL = 60  # seconds

# Streamlit アプリが描画されたことを示すセレクター候補（優先度順）
# Streamlit のバージョンによって data-testid が異なるためフォールバック
APP_SELECTORS = [
    '[data-testid="stAppViewContainer"]',
    '[data-testid="stApp"]',
    '[data-testid="stMain"]',
    '[data-testid="stHeader"]',
    '.stApp',
    '.main',
]

# ウェイクアップボタンのセレクター候補
WAKE_BUTTON_SELECTORS = [
    'button:has-text("Yes, get this app back up!")',
    'button:has-text("Wake up")',
    'button:has-text("Yes")',
    '[data-testid="stAppWakeUpButton"]',
]


def wake_up_if_sleeping(page: Page) -> bool:
    """スリープ中のアプリを検知し、起動ボタンをクリックする。

    メインフレームとすべての子フレーム(iframe)を走査する。
    """
    frames = [page] + list(page.frames)
    for frame in frames:
        for selector in WAKE_BUTTON_SELECTORS:
            try:
                btn = frame.locator(selector).first
                if btn.is_visible(timeout=3_000):
                    print(f"App is sleeping. Clicking wake-up button: {selector}")
                    btn.click()
                    print("Waiting for app to boot up after wake...")
                    page.wait_for_timeout(15_000)
                    return True
            except Exception:
                continue
    return False


def check_app_rendered(page: Page, timeout_ms: int = 300_000) -> bool:
    """Streamlit アプリが描画されたか確認する。

    メインフレームおよび iframe 内の両方を対象に、複数のセレクターを
    ポーリングで確認する。
    """
    deadline = time.time() + timeout_ms / 1000
    poll_interval = 5_000  # ms

    while time.time() < deadline:
        frames = [page] + list(page.frames)
        for frame in frames:
            for selector in APP_SELECTORS:
                try:
                    loc = frame.locator(selector).first
                    if loc.is_visible(timeout=1_000):
                        print(f"App rendered! Found selector: {selector}")
                        return True
                except Exception:
                    continue
        print("  Still waiting for app to render...")
        page.wait_for_timeout(poll_interval)

    return False


def visit_app(page: Page) -> None:
    """アプリにアクセスし、Streamlit の起動完了を確認する。"""
    print(f"Navigating to {APP_URL}")
    resp = page.goto(APP_URL, wait_until="load", timeout=180_000)

    status = resp.status if resp else None
    print(f"Page loaded with status: {status}")

    # スリープ中ならウェイクアップボタンをクリック
    woke = wake_up_if_sleeping(page)
    if woke:
        print("Wake-up button clicked, waiting for full load...")
        page.wait_for_timeout(10_000)
        # ウェイクアップ後に再度スリープ判定（リダイレクトされる場合）
        wake_up_if_sleeping(page)

    # Streamlit アプリ本体の描画を待つ
    print("Waiting for Streamlit app to render...")
    rendered = check_app_rendered(page, timeout_ms=300_000)

    if not rendered:
        # フォールバック: ページタイトルやレスポンスステータスで判定
        title = page.title()
        print(f"Selectors not found. Page title: '{title}', status: {status}")
        if status and 200 <= status < 400 and title:
            print("Page responded successfully; treating as alive (selectors may have changed).")
        else:
            raise RuntimeError(
                f"App did not render. status={status}, title='{title}'"
            )

    # 描画後に少し待機してアクティビティを発生させる
    page.wait_for_timeout(10_000)
    print("App is alive and rendered successfully.")


def main() -> None:
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
