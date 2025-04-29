import os
from pathlib import Path
import tempfile
import requests
from bs4 import BeautifulSoup
from docling.document_converter import DocumentConverter
from docling_core.types.doc.document import DoclingDocument
from urllib.parse import urljoin
from typing import List
from bs4.element import Tag
from site_reaper import SiteReaper

class SiteReaperMkdocs(SiteReaper):
    def __init__(self, base_url: str):
        super().__init__(base_url)


    @classmethod
    def get_name(cls) -> str:
        return "Mkdocs reaper"
    
    @classmethod
    def get_description(cls) -> str:
        return """This reaper will extract the list of URLs, ending with <code>.htm</code> or <code>.html</code>, from the <code>href</code>s present on the first page.<BR>
                  It will then rip the content of the <code>&lt;article&gt;</code> element on these URLs and on the first page.<BR>
                  This will be typically usable for extracting text from Mkdocs sites."""

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
