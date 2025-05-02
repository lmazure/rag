from typing import List
from bs4.element import Tag
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

class SiteReaper:

    name = ""
    description = ""

    @classmethod
    def get_name(cls) -> str:
        return cls.name

    @classmethod
    def get_description(cls) -> str:
        return cls.description

    def __init__(self, base_url: str):
        self.base_url = base_url

    def get_urls(self) -> List[str]:
        """Get all HTML URLs from the documentation site."""
        urls = [ self.base_url ]
        response = requests.get(self.base_url)
        soup = BeautifulSoup(response.text, 'html.parser')

        for link in soup.find_all('a'):
            assert isinstance(link, Tag)
            href = link.get('href')
            if href and isinstance(href, str) and (href.endswith('.html') or href.endswith('.htm')):
                urls.append(urljoin(self.base_url, href))

        return list(set(urls))
