from operator import truediv
from typing import List, Dict
from bs4 import BeautifulSoup, Comment
import re

from src.utils.logger import get_logger
from src.utils.exceptions import DataProcessingException

logger = get_logger(__name__)

class HTMLCleaner:

    def __init__(self):
        self.unwanted_tags = [
            'script', 'style', 'noscript', 'header', 'footer', 'nav', 'form',
            'button', 'input', 'select', 'textarea', 'iframe', 'svg', 'canvas',
            'img',
            'link', 'meta'
        ]

        self.whitespace_pattern = re.compile(r'\s+')

    def _clean_html_content(self, html_content: str) -> str:

        if not html_content:
            return ""

        soup = BeautifulSoup(html_content, "html.parser")

        for comment in soup(text=lambda text: isinstance(text, Comment)):
            comment.extract()

        for tag in self.unwanted_tags:
            for element in soup.find_all(tag):
                element.decompose()

        main_content = soup.find('main')
        if not main_content:
            main_content = soup.find('article')
        if not main_content:
            main_content = soup.find(id='content')
        if not main_content:
            main_content = soup.body
        if not main_content:
            logger.warning("Could not find main content area or body")
            return ""

        text = main_content.get_text(separator=' ', strip=True)
        text = self.whitespace_pattern.sub(' ', text).strip()
        return text

    def clean_scraped_data(self, scraped_data: List[Dict[str, str]]) -> List[Dict[str, str]] :

        cleaned_results = []
        if not scraped_data:
            logger.warning("No scraped data provided for cleaning.")
            return []

        for item in scraped_data:
            url = item.get("url")
            html_content = item.get("content")

            if not url or not html_content:
                logger.warning(f"Skipping incomplete data item: {item}")
                continue
            try:
                cleaned_text = self._clean_html_content(html_content)
                if cleaned_text:
                    cleaned_results.append({"url": url, "cleaned_text": cleaned_text})
                else:
                    logger.warning(f"No meaningful text extracted from {url}. Skipping.")

            except Exception as e:
                logger.error(f"Error cleaning content from {url}: {e}")

        if not cleaned_results:
            raise DataProcessingException("No text was successfully cleaned from any scraped content.")

        logger.info(f"Finished cleaning. Successfully extracted text from {len(cleaned_results)} documents.")
        return cleaned_results

if __name__ == "__main__":
    dummy_html = """
    <html>
    <head><title>Test Page</title><style>body{color:red;}</style></head>
    <body>
        <header>Navigation</header>
        <script>alert('hello');</script>
        <main>
            <h1>Welcome to Changi!</h1>
            <p>This is some <a href="#">important</a> information about the airport.</p>
            <p>Another paragraph with <b>bold</b> text.</p>
            <div>
                <span>Some inline text.</span>
            </div>
        </main>
        <footer>Contact Us</footer>
        <script src="app.js"></script>
    </body>
    </html>
    """

    scraper_output = [{"url": "http://example.com/test", "content": dummy_html}]

    cleaner = HTMLCleaner()
    try:
        cleaned_data = cleaner.clean_scraped_data(scraper_output)
        for data in cleaned_data:
            logger.info(f"--- Cleaned Text from {data['url']} ---")
            logger.info(data['cleaned_text'])
            logger.info("-" * 50)

        # Test with empty input
        logger.info("Testing with empty input...")
        empty_cleaned_data = cleaner.clean_scraped_data([])
        logger.info(f"Empty input result: {empty_cleaned_data}")

    except DataProcessingException as e:
        logger.error(f"Cleaning failed: {e}")
    except Exception as e:
        logger.error(f"An unexpected error occurred during cleaning test: {e}")

