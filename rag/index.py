from pdf_loader import PDFLoader
from pathlib import Path

path = Path(__file__).parent / "return_label_uk_2025.pdf"

loader = PDFLoader(file_path=path)
pages = loader.load_pages()