"""
Markdown document processor.
"""

import os
import re
from typing import Dict, Any
import markdown
from bs4 import BeautifulSoup

from .base import BaseProcessor


class MarkdownProcessor(BaseProcessor):
    """Processor for Markdown documents."""

    def extract_text(self) -> str:
        """
        Extract text content from a Markdown file.

        Returns:
            str: The extracted text
        """
        with open(self.file_path, "r", encoding="utf-8") as file:
            md_content = file.read()
            
            # Convert markdown to HTML
            html = markdown.markdown(md_content)
            
            # Extract text from HTML
            soup = BeautifulSoup(html, "html.parser")
            text = soup.get_text(separator=" ", strip=True)
            
            return text

    def extract_metadata(self) -> Dict[str, Any]:
        """
        Extract metadata from a Markdown file.
        Looks for YAML frontmatter if present.

        Returns:
            dict: Markdown metadata
        """
        metadata = {
            "source": self.file_path,
            "filename": os.path.basename(self.file_path),
            "file_type": "markdown",
        }

        with open(self.file_path, "r", encoding="utf-8") as file:
            content = file.read()

            # Check for YAML frontmatter (between --- markers)
            frontmatter_match = re.search(r"^---\s*\n(.*?)\n---\s*\n", content, re.DOTALL)
            if frontmatter_match:
                frontmatter_text = frontmatter_match.group(1)
                
                # Extract key-value pairs from frontmatter
                for line in frontmatter_text.split("\n"):
                    if ":" in line:
                        key, value = line.split(":", 1)
                        metadata[key.strip().lower()] = value.strip()

            # Get approximate word count
            text_content = self.extract_text()
            metadata["word_count"] = len(text_content.split())

        return metadata 