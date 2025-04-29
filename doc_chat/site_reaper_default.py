import requests
from bs4 import BeautifulSoup, Tag
from docling.document_converter import DocumentConverter
from docling_core.types.doc.document import DoclingDocument
from typing import List
from urllib.parse import urljoin

from site_reaper import SiteReaper

class SiteReaperDefault(SiteReaper):
    def __init__(self, base_url: str):
        super().__init__(base_url)

    @classmethod
    def get_name(cls) -> str:
        return "Default reaper"

    @classmethod
    def get_description(cls) -> str:
        return """This reaper will extract the list of URLs, ending with <code>.htm</code> or <code>.html</code>, from the <code>href</code>s present on the first page.<BR>
                  It will then rip the whole HTML content of these URLs and of the first page."""

    def get_urls(self) -> List[str]:
        """Get all HTML URLs from the documentation site."""
        urls = [ self.base_url ]
        response = requests.get(self.base_url)
        soup = BeautifulSoup(response.text, 'html.parser')

        for link in soup.find_all('a'):
            assert isinstance(link, Tag)
            href = link.get('href')
            assert href
            assert isinstance(href, str)
            if href.endswith('.html') or href.endswith('.htm'):
                urls.append(urljoin(self.base_url, href))

        return list(set(urls))

    def get_url_content(self, url: str) -> DoclingDocument:
        """Get the content of a URL."""
        converter = DocumentConverter()
        result = converter.convert(url)
        return result.document
