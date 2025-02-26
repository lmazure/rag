import pytest
from app import app, get_all_html_urls, fetch_and_chunk_content

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_home_page(client):
    """Test that the home page loads correctly"""
    rv = client.get('/')
    assert rv.status_code == 200
    assert b'Squash Documentation Chat' in rv.data

def test_get_all_html_urls():
    """Test URL extraction from a sample page"""
    urls = get_all_html_urls("https://tm-fr.doc.squashtest.com/latest/")
    assert len(urls) > 0
    assert all(url.endswith('.html') for url in urls)

def test_fetch_and_chunk_content():
    """Test content chunking from a sample URL"""
    url = "https://tm-fr.doc.squashtest.com/latest/index.html"
    chunks = fetch_and_chunk_content(url)
    assert len(chunks) > 0
    assert all(isinstance(chunk, tuple) and len(chunk) == 2 for chunk in chunks)
    assert all(isinstance(chunk[0], str) and isinstance(chunk[1], str) for chunk in chunks)
