from django.contrib import admin
from .models import AcademicDocument, DocumentChunk

@admin.register(AcademicDocument)
class AcademicDocumentAdmin(admin.ModelAdmin):
    list_display = ('filename', 'source_type', 'document_type', 'date_ingested')
    search_fields = ('filename',)
    list_filter = ('source_type', 'document_type')

@admin.register(DocumentChunk)
class DocumentChunkAdmin(admin.ModelAdmin):
    list_display = ('document', 'page_number', 'section', 'chunk_hash')
    search_fields = ('content', 'document__filename')
    list_filter = ('document',)
