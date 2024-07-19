import os

# define init index
INIT_INDEX = os.getenv('INIT_INDEX', 'false').lower() == 'true'

# vector index persist directory
INDEX_PERSIST_DIRECTORY = os.getenv('INDEX_PERSIST_DIRECTORY', "./data/chromadb")

# target url to scrape
TARGET_URL =  os.getenv('TARGET_URL', "https://tm-en.doc.squashtest.com/latest/")

# http api port
HTTP_PORT = os.getenv('HTTP_PORT', 7654)
