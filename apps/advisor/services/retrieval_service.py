import os
import shutil
import chromadb
from django.conf import settings
from rag.models import DocumentChunk

class RetrievalService:
    def __init__(self):
        rag_dir = os.path.join(settings.BASE_DIR, 'rag_data')
        if 'VERCEL' in os.environ or os.environ.get('VERCEL_ENV'):
            tmp_rag = '/tmp/rag_data'
            if not os.path.exists(tmp_rag) and os.path.exists(rag_dir):
                try:
                    shutil.copytree(rag_dir, tmp_rag, dirs_exist_ok=True)
                except Exception:
                    pass
            if os.path.exists(tmp_rag):
                rag_dir = tmp_rag

        self.chroma_client = chromadb.PersistentClient(path=rag_dir)
        self.collection_name = "academic_kb"
        self.collection = self.chroma_client.get_or_create_collection(name=self.collection_name)

        
    def retrieve_evidence(self, query, top_k=3):
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=top_k
            )
            
            evidence_list = []
            if results and results['ids'] and len(results['ids'][0]) > 0:
                for idx, chunk_id in enumerate(results['ids'][0]):
                    try:
                        db_chunk = DocumentChunk.objects.get(chunk_hash=chunk_id)
                        evidence = {
                            "content": db_chunk.content,
                            "source": db_chunk.document.filename,
                            "page": db_chunk.page_number,
                            "section": db_chunk.section,
                            "metadata": db_chunk.metadata,
                            "score": results['distances'][0][idx] if 'distances' in results else None
                        }
                        evidence_list.append(evidence)
                    except DocumentChunk.DoesNotExist:
                        continue
                        
            return evidence_list
        except Exception as e:
            return []
