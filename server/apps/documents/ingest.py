from django.db import transaction
from django.utils import timezone
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader

from server.apps.documents import configuration
from server.apps.documents.choices import DocumentStatusChoices
from server.apps.documents.embeddings import EmbeddingService
from server.apps.documents.models import Document, DocumentChunk


def ingest_document(document_id: int):
    """Ingest a document by loading, splitting, embedding, and saving chunks."""
    doc = Document.objects.get(pk=document_id)
    doc.status = DocumentStatusChoices.PROCESSING
    doc.save(update_fields=['status'])

    # 1) Load pages
    loader = PyPDFLoader(doc.file.path)
    raw_docs = loader.load()  # returns list of LangChain Document objects

    # 2) Split into chunks
    # (recursive handles sentences/paragraphs intelligently)
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=configuration.RAG['CHUNK_SIZE'],
        chunk_overlap=configuration.RAG['CHUNK_OVERLAP'],
    )
    split_docs = splitter.split_documents(raw_docs)

    # 3) Get embeddings
    texts = [d.page_content for d in split_docs]
    embedder = EmbeddingService()
    vectors = embedder.embed(texts)

    # 4) Save to DB
    objs = []
    for idx, (doc_obj, emb) in enumerate(
        zip(split_docs, vectors, strict=False)
    ):
        metadata = doc_obj.metadata
        objs.append(
            DocumentChunk(
                document=doc,
                page_number=metadata.get('page', 1),
                chunk_index=idx,
                content=doc_obj.page_content,
                tokens=len(doc_obj.page_content.split()),
                embedding=emb,
            )
        )

    with transaction.atomic():
        doc.chunks.all().delete()
        DocumentChunk.objects.bulk_create(objs, batch_size=500)

        doc.processed_at = timezone.now()
        doc.status = DocumentStatusChoices.COMPLETED
        doc.save(update_fields=['processed_at', 'status'])
