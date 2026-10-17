"""Document processing service"""
import hashlib
import uuid
from typing import List, Dict, Any, Optional, BinaryIO
from pathlib import Path
import pypdf
from langchain_text_splitters import RecursiveCharacterTextSplitter
from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger(__name__)
settings = get_settings()


class DocumentProcessor:
    """Service for processing and chunking documents"""

    def __init__(self):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.chunk_size,
            chunk_overlap=settings.chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""],
        )

    def extract_text_from_pdf(self, file: BinaryIO) -> str:
        """Extract text from PDF file"""
        try:
            pdf_reader = pypdf.PdfReader(file)
            text_parts = []

            for page in pdf_reader.pages:
                text = page.extract_text()
                if text:
                    text_parts.append(text)

            full_text = "\n\n".join(text_parts)
            logger.info(f"Extracted {len(full_text)} characters from PDF")
            return full_text

        except Exception as e:
            logger.error(f"Error extracting text from PDF: {e}")
            raise ValueError(f"Failed to extract text from PDF: {str(e)}")

    def extract_text_from_txt(self, file: BinaryIO) -> str:
        """Extract text from text file"""
        try:
            content = file.read()
            # Try UTF-8 first, fallback to latin-1
            try:
                text = content.decode('utf-8')
            except UnicodeDecodeError:
                text = content.decode('latin-1')

            logger.info(f"Extracted {len(text)} characters from text file")
            return text

        except Exception as e:
            logger.error(f"Error reading text file: {e}")
            raise ValueError(f"Failed to read text file: {str(e)}")

    def process_document(
        self,
        content: str,
        filename: str,
        file_type: str,
    ) -> Dict[str, Any]:
        """Process document and split into chunks"""
        # Generate document ID
        document_id = str(uuid.uuid4())

        # Calculate content hash
        content_hash = hashlib.sha256(content.encode()).hexdigest()

        # Split into chunks
        chunks = self.text_splitter.split_text(content)

        logger.info(f"Split document into {len(chunks)} chunks")

        return {
            "document_id": document_id,
            "content_hash": content_hash,
            "chunks": chunks,
            "chunk_count": len(chunks),
            "filename": filename,
            "file_type": file_type,
        }

    def chunk_text(self, text: str) -> List[str]:
        """Split text into chunks"""
        return self.text_splitter.split_text(text)


# Global document processor instance
document_processor = DocumentProcessor()