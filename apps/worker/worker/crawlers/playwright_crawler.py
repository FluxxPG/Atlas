from playwright.async_api import async_playwright

from worker.config import settings


async def fetch_page(url: str) -> dict:
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(headless=settings.playwright_headless)
        page = await browser.new_page()
        await page.goto(url, timeout=settings.playwright_timeout_ms, wait_until="networkidle")
        title = await page.title()
        content = await page.content()
        await browser.close()
        return {"title": title, "content": content[:12000]}

