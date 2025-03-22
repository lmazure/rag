import os
from pathlib import Path
import tempfile
import requests
from bs4 import BeautifulSoup
from docling.document_converter import DocumentConverter
from docling_core.types.doc.document import DoclingDocument
from typing import List
from urllib.parse import urljoin

class SiteReaper:
    def __init__(self, base_url: str):
        self.base_url = base_url

    def get_urls(self) -> List[str]:
        """Get all HTML URLs from the documentation site."""
        urls = [ self.base_url ]
        response = requests.get(self.base_url)
        soup = BeautifulSoup(response.text, 'html.parser')
    
        for link in soup.find_all('a'):
            href = link.get('href')
            if href and (href.endswith('.html') or href.endswith('.htm')):
                urls.append(urljoin(self.base_url, href))
        
        return list(set(urls))

    def get_url_content(self, url: str) -> DoclingDocument:
        """Get the content of a URL."""
        converter = DocumentConverter()
        result = converter.convert(url)
        return result.document
