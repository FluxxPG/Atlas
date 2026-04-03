from pathlib import Path

from playwright.sync_api import Page, sync_playwright


ROOT = Path(__file__).resolve().parents[1]
BASE_URL = "http://127.0.0.1:3003"
def sign_in(page: Page, *, email: str, password: str, expected_path: str) -> None:
    page.goto(f"{BASE_URL}/login", wait_until="networkidle")
    page.get_by_label("Email").fill(email)
    page.get_by_label("Password").fill(password)
    page.get_by_role("button", name="Sign In").click()
    page.wait_for_url(f"**{expected_path}", wait_until="networkidle")


def capture_authenticated_page(
    page: Page,
    *,
    email: str,
    password: str,
    expected_path: str,
    target_url: str,
    screenshot_path: Path,
) -> None:
    sign_in(page, email=email, password=password, expected_path=expected_path)
    page.goto(target_url, wait_until="networkidle")
    page.screenshot(path=str(screenshot_path), full_page=True)


def main() -> None:
    admin_shot = ROOT / "preview-superadmin-live-validation.png"
    client_shot = ROOT / "preview-client-live-validation.png"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)

        admin_ctx = browser.new_context(viewport={"width": 1440, "height": 1100})
        admin_page = admin_ctx.new_page()
        capture_authenticated_page(
            admin_page,
            email="admin@atlasbi.local",
            password="AtlasBI-Admin-2026",
            expected_path="/superadmin",
            target_url=f"{BASE_URL}/superadmin/crawlers",
            screenshot_path=admin_shot,
        )

        client_ctx = browser.new_context(viewport={"width": 1440, "height": 1100})
        client_page = client_ctx.new_page()
        capture_authenticated_page(
            client_page,
            email="client@atlasbi.local",
            password="AtlasBI-Client-2026",
            expected_path="/dashboard",
            target_url=f"{BASE_URL}/search?q=restaurants%20needing%20website&country=India&sort_by=opportunity",
            screenshot_path=client_shot,
        )

        print(
            {
                "admin_screenshot": str(admin_shot),
                "client_screenshot": str(client_shot),
                "admin_url": admin_page.url,
                "client_url": client_page.url,
            }
        )
        browser.close()


if __name__ == "__main__":
    main()
