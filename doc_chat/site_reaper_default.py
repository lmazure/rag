from docling.document_converter import DocumentConverter
from docling_core.types.doc.document import DoclingDocument

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

    def get_url_content(self, url: str) -> DoclingDocument:
        """Get the content of a URL."""
        converter = DocumentConverter()
        result = converter.convert(url)
        return result.document
