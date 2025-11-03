from playwright.async_api import async_playwright
import re

class DigikalaScraper:
    """Async Scraper for Digikala product pages using Playwright"""

    def __init__(self):
        pass

    async def scrape_product(self, url: str) -> dict:
        print(f"🌐 Opening product page: {url}")
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page()
                await page.goto(url, timeout=60000)
                await page.wait_for_selector("h1", timeout=15000)

                h1_handle = await page.query_selector("h1")
                name = await h1_handle.inner_text()
                name = name.strip()

                await page.wait_for_selector('[data-theme-animation="price-container"]', timeout=20000)
                price_handle = await page.query_selector('[data-theme-animation="price-container"]')
                price_text = await price_handle.inner_text()
                price_text = price_text.strip()

                # تبدیل اعداد فارسی به انگلیسی
                persian_to_english = str.maketrans('۰۱۲۳۴۵۶۷۸۹', '0123456789')
                price_str = price_text.translate(persian_to_english)
                price = int(re.sub(r"[^\d]", "", price_str))

                await browser.close()

                print(f"✅ Found: {name} - {price:,} تومان")
                return {"name": name, "price": price}

        except Exception as e:
            print(f"❌ Error while scraping: {e}")
            return None

# Test
if __name__ == "__main__":
    import asyncio

    async def main():
        scraper = DigikalaScraper()
        test_url = "https://www.digikala.com/product/dkp-18111827/"
        data = await scraper.scrape_product(test_url)
        print(data)

    asyncio.run(main())
