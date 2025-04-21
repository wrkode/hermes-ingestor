"""
Base processor class for document processing.
"""

import os
from abc import ABC, abstractmethod
from typing import List


class BaseProcessor(ABC):
    """Base class for all document processors."""

    def __init__(self, file_path: str):
        """
        Initialize the processor with a file path.

        Args:
            file_path: Path to the document file
        """
        self.file_path = file_path
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

    @abstractmethod
    def extract_text(self) -> str:
        """
        Extract text content from the document.

        Returns:
            str: The extracted text
        """
        pass

    @abstractmethod
    def extract_metadata(self) -> dict:
        """
        Extract metadata from the document.

        Returns:
            dict: Document metadata
        """
        pass

    def get_file_name(self) -> str:
        """
        Get the file name without extension.

        Returns:
            str: File name
        """
        return os.path.splitext(os.path.basename(self.file_path))[0]

    def get_file_extension(self) -> str:
        """
        Get the file extension.

        Returns:
            str: File extension without the dot
        """
        return os.path.splitext(self.file_path)[1][1:].lower() 