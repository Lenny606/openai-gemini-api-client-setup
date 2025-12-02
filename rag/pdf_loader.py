from langchain_community.document_loaders import PyPDFLoader
from pathlib import Path


class PDFLoader:
    def __init__(self, file_path: str | Path):
        self.loader = PyPDFLoader(file_path)

    def load_pages(self):
        # load , returns a list of Document pages
        return self.loader.load()
