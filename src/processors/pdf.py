"""
PDF document processor.
"""

import os
from typing import Dict, Any
import pdfminer.high_level
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfparser import PDFParser
from pdfminer.pdftypes import resolve1

from .base import BaseProcessor


class PDFProcessor(BaseProcessor):
    """Processor for PDF documents."""

    def extract_text(self) -> str:
        """
        Extract text content from a PDF file.

        Returns:
            str: The extracted text
        """
        text = pdfminer.high_level.extract_text(self.file_path)
        return text

    def extract_metadata(self) -> Dict[str, Any]:
        """
        Extract metadata from a PDF file.

        Returns:
            dict: PDF metadata including title, author, creation date, etc.
        """
        metadata = {
            "source": self.file_path,
            "filename": os.path.basename(self.file_path),
            "file_type": "pdf",
        }

        # Extract PDF-specific metadata
        with open(self.file_path, "rb") as file:
            parser = PDFParser(file)
            doc = PDFDocument(parser)
            
            if hasattr(doc, "info") and doc.info:
                pdf_info = doc.info[0]
                
                # Extract and decode common PDF metadata fields
                for key, value in pdf_info.items():
                    if isinstance(value, bytes):
                        try:
                            # Try to decode as UTF-8
                            decoded_value = value.decode("utf-8", errors="replace")
                        except UnicodeDecodeError:
                            # If decoding fails, use string representation
                            decoded_value = str(value)
                        metadata[key.lower().decode("utf-8", errors="replace")] = decoded_value
                    else:
                        metadata[key.lower().decode("utf-8", errors="replace")] = str(value)
            
            # Get number of pages
            if "pages" not in metadata and hasattr(doc, "catalog"):
                pages = resolve1(doc.catalog.get("Pages", {}))
                count = resolve1(pages.get("Count", 0))
                metadata["pages"] = count

        return metadata 