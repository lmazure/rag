import os
from pathlib import Path
import tempfile
import requests
from bs4 import BeautifulSoup
from docling.document_converter import DocumentConverter
from docling_core.types.doc.document import DoclingDocument
from site_reaper import SiteReaper

class SiteReaperMkdocs(SiteReaper):

    name = "Mkdocs reaper"
    description = """This reaper will extract the list of URLs, ending with <code>.htm</code> or <code>.html</code>, from the <code>href</code>s present on the first page.<BR>
                  It will then rip the content of the <code>&lt;article&gt;</code> element on these URLs and on the first page.<BR>
                  This will be typically usable for extracting text from Mkdocs sites."""

    def __init__(self, base_url: str):
        super().__init__(base_url)

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
