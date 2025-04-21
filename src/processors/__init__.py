"""
Document processors for different file types.
"""

from .base import BaseProcessor
from .pdf import PDFProcessor
from .markdown import MarkdownProcessor
from .html import HTMLProcessor
from .text import TextProcessor
from .docx import DocxProcessor 