import os
import hashlib
import chromadb
from pypdf import PdfReader
from django.core.management.base import BaseCommand
from django.conf import settings
from rag.models import AcademicDocument, DocumentChunk
from chromadb.utils import embedding_functions

class Command(BaseCommand):
    help = 'Build RAG index from PDFs'

    def handle(self, *args, **kwargs):
        pdf_dir = os.path.join(settings.BASE_DIR, 'source_data', 'PDFs')
        rag_dir = os.path.join(settings.BASE_DIR, 'rag_data')
        
        # Setup ChromaDB
        chroma_client = chromadb.PersistentClient(path=rag_dir)
        collection_name = "academic_kb"
        
        # Use default embedding function for now, provider-agnostic
        emb_fn = embedding_functions.DefaultEmbeddingFunction()
        
        # Delete old collection if it exists to make it rebuildable safely
        try:
            chroma_client.delete_collection(name=collection_name)
        except Exception:
            pass
            
        collection = chroma_client.create_collection(name=collection_name, embedding_function=emb_fn)
        
        # Only authoritative PDFs
        pdfs = [
            '4. Student Handbook Aug 2026.pdf',
            'SOP STUDENT 17082026 - Final.pdf'
        ]
        
        total_chunks = 0
        
        for pdf_name in pdfs:
            file_path = os.path.join(pdf_dir, pdf_name)
            if not os.path.exists(file_path):
                self.stdout.write(self.style.WARNING(f"{pdf_name} not found."))
                continue
                
            doc, _ = AcademicDocument.objects.get_or_create(
                filename=pdf_name,
                defaults={
                    'source_type': 'regulation' if 'Handbook' in pdf_name else 'sop',
                    'document_type': 'PDF',
                    'source_path': file_path
                }
            )
            
            reader = PdfReader(file_path)
            for i, page in enumerate(reader.pages):
                text = page.extract_text()
                if not text:
                    continue
                    
                text = text.replace('\n', ' ').strip()
                chunk_size = 1000
                chunks = [text[j:j+chunk_size] for j in range(0, len(text), chunk_size)]
                
                for idx, c_text in enumerate(chunks):
                    if len(c_text) < 50:
                        continue
                        
                    content_hash = hashlib.sha256(c_text.encode('utf-8')).hexdigest()
                    
                    chunk, created = DocumentChunk.objects.get_or_create(
                        chunk_hash=content_hash,
                        defaults={
                            'document': doc,
                            'content': c_text,
                            'page_number': i + 1,
                            'metadata': {'page': i + 1, 'chunk_idx': idx}
                        }
                    )
                    
                    # Store in ChromaDB
                    metadata_dict = {
                        "source": doc.filename, 
                        "page": str(i+1),
                        "chunk_idx": str(idx)
                    }
                    
                    collection.add(
                        documents=[c_text],
                        metadatas=[metadata_dict],
                        ids=[content_hash]
                    )
                    
                    if created:
                        total_chunks += 1
                        
        self.stdout.write(self.style.SUCCESS(f"RAG Index built. Indexed {total_chunks} new chunks into ChromaDB."))
