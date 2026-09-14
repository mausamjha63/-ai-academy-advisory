from django.test import TestCase
from django.core.management import call_command
from rag.models import AcademicDocument, DocumentChunk
from unittest.mock import patch
from io import StringIO

class RAGTests(TestCase):
    @patch('rag.management.commands.build_rag_index.PdfReader')
    @patch('rag.management.commands.build_rag_index.chromadb.PersistentClient')
    def test_build_rag_command(self, mock_chroma, mock_pdf):
        # We mock the PDF reader and ChromaDB to avoid real file dependencies in unit tests
        mock_pdf_instance = mock_pdf.return_value
        mock_pdf_instance.pages = []
        
        mock_collection = mock_chroma.return_value.create_collection.return_value
        
        out = StringIO()
        call_command('build_rag_index', stdout=out)
        self.assertIn("RAG Index built", out.getvalue())
        
    def test_academic_document_model(self):
        doc = AcademicDocument.objects.create(
            filename="Test.pdf",
            source_type="regulation",
            document_type="PDF"
        )
        self.assertEqual(doc.filename, "Test.pdf")
        
        chunk = DocumentChunk.objects.create(
            document=doc,
            content="Test content",
            chunk_hash="abc123hash",
            page_number=1
        )
        self.assertEqual(chunk.document, doc)
