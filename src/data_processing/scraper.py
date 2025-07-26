import asyncio
from typing import List, Dict
from playwright.async_api import async_playwright, Page, Response, Error as PlaywrightError
from src.config import Config
from src.utils.logger import get_logger
from src.utils.exceptions import DataProcessingException

logger = get_logger(__name__)

class Webscraper:

    def __init__(self):
        self.urls = Config.SCRAPING_URLS


    async def _fetch_page_content(self, url:str) -> str | None:

        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page()
                logger.info(f"Naavigate to {url}")

                response: Response | None = None
                try:
                    response = await page.goto(url, wait_until="networkidle")
                except PlaywrightError as pe:
                    logger.warning(f"Playwright navigation error for {url}: {pe}")
                    return None

                if response and response.status != 200:
                    logger.warning(f"Failed to fetch {url} with status {response.status}")
                    return None

                content = await page.content()
                logger.info(f"Successfully fetched content from {url}")
                await browser.close()
                return content

        except PlaywrightError as e:
            logger.error(f"Playwright error during fetching {url}: {e}")
            return None
        except Exception as e:
            logger.error(f"An unexpected error occurred while fetching {url}: {e}")
            return None

    async def scrape_all(self) -> List[Dict[str, str]]:

        scraped_data = []
        tasks = [self._fetch_page_content(url) for url in self.urls]
        results = await asyncio.gather(*tasks)

        for url, content in zip(self.urls, results):
            if content:
                scraped_data.append({"url": url, "content": content})
            else:
                logger.warning(f"Skipping {url} due to failed content retrieval.")

        if not scraped_data:
            raise DataProcessingException("No content was successfully scraped from any configured URL.")

        logger.info(
            f"Finished scraping. Successfully fetched content from {len(scraped_data)} out of {len(self.urls)} URLs.")
        return scraped_data


if __name__ == "__main__":

    async def run_scraper_test():
        scraper = Webscraper()
        try:
            scraped_content = await scraper.scrape_all()
            for data in scraped_content:
                logger.info(f"--- Content from {data['url']} (first 500 chars): ---")
                logger.info(data['content'][:500])
                logger.info("-" * 50)
        except DataProcessingException as e:
            logger.error(f"Scraping failed: {e}")
        except Exception as e:
            logger.error(f"An unexpected error occurred during scraping test: {e}")


    asyncio.run(run_scraper_test())
