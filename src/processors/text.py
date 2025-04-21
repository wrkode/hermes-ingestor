"""
Plain text document processor.
"""

import os
from typing import Dict, Any

from .base import BaseProcessor


class TextProcessor(BaseProcessor):
    """Processor for plain text documents."""

    def extract_text(self) -> str:
        """
        Extract text content from a plain text file.

        Returns:
            str: The extracted text
        """
        with open(self.file_path, "r", encoding="utf-8", errors="replace") as file:
            return file.read()

    def extract_metadata(self) -> Dict[str, Any]:
        """
        Extract metadata from a plain text file.

        Returns:
            dict: Basic file metadata
        """
        metadata = {
            "source": self.file_path,
            "filename": os.path.basename(self.file_path),
            "file_type": "text",
        }

        # Get file size in KB
        metadata["size_kb"] = round(os.path.getsize(self.file_path) / 1024, 2)
        
        # Get creation and modification dates
        metadata["created"] = os.path.getctime(self.file_path)
        metadata["modified"] = os.path.getmtime(self.file_path)
        
        # Get approximate word count
        with open(self.file_path, "r", encoding="utf-8", errors="replace") as file:
            text = file.read()
            metadata["word_count"] = len(text.split())
            metadata["line_count"] = len(text.splitlines())

        return metadata 