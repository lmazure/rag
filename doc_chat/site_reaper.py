import os
from pathlib import Path
import tempfile
from numpy import delete
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

    def get_url_content_mkdocs(self, url: str) -> DoclingDocument:
        """Get the content of a URL of a site generated with mkdocs."""
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        article = soup.find('article')
        tmp_file = tempfile.NamedTemporaryFile(suffix='.html', delete=False)
        tmp_file.write(str(article).encode('utf-8'))
        tmp_file.close()
        converter = DocumentConverter()
        result = converter.convert(Path(tmp_file.name))
        os.unlink(tmp_file.name)
        return result.document
