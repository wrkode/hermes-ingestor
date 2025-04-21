"""
HTML document processor.
"""

import os
from typing import Dict, Any
from bs4 import BeautifulSoup

from .base import BaseProcessor


class HTMLProcessor(BaseProcessor):
    """Processor for HTML documents."""

    def extract_text(self) -> str:
        """
        Extract text content from an HTML file.

        Returns:
            str: The extracted text
        """
        with open(self.file_path, "r", encoding="utf-8") as file:
            html_content = file.read()
            
            soup = BeautifulSoup(html_content, "html.parser")
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.extract()
                
            # Get text
            text = soup.get_text(separator=" ", strip=True)
            
            # Remove excessive whitespace
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = " ".join(chunk for chunk in chunks if chunk)
            
            return text

    def extract_metadata(self) -> Dict[str, Any]:
        """
        Extract metadata from an HTML file.

        Returns:
            dict: HTML metadata including title, description, etc.
        """
        metadata = {
            "source": self.file_path,
            "filename": os.path.basename(self.file_path),
            "file_type": "html",
        }

        with open(self.file_path, "r", encoding="utf-8") as file:
            html_content = file.read()
            soup = BeautifulSoup(html_content, "html.parser")
            
            # Extract title
            title_tag = soup.find("title")
            if title_tag:
                metadata["title"] = title_tag.get_text(strip=True)
                
            # Extract meta tags
            for meta in soup.find_all("meta"):
                name = meta.get("name", "").lower()
                content = meta.get("content", "")
                
                if name and content:
                    metadata[name] = content
                    
                # Also check for OpenGraph and Twitter meta tags
                prop = meta.get("property", "").lower()
                if prop.startswith("og:") and content:
                    metadata[prop] = content
                    
                name = meta.get("name", "").lower()
                if name.startswith("twitter:") and content:
                    metadata[name] = content
            
            # Extract first h1 if no title found
            if "title" not in metadata:
                h1 = soup.find("h1")
                if h1:
                    metadata["title"] = h1.get_text(strip=True)
            
            # Get approximate word count
            text_content = self.extract_text()
            metadata["word_count"] = len(text_content.split())

        return metadata 