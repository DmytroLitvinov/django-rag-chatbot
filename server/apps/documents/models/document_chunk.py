from typing import Final

from django.db import models
from pgvector.django import HnswIndex, VectorField

from server.apps.core.models import BaseModel

__all__ = ('DocumentChunk',)


class DocumentChunk(BaseModel):
    # Assuming usage of text-embedding-3-small (1536 dimensions)
    # Adjust dimensions if using a different embedding model.
    EMBEDDING_DIMENSIONS: Final[int] = 1536

    document = models.ForeignKey(
        'documents.Document', on_delete=models.CASCADE, related_name='chunks'
    )

    page_number = models.IntegerField(default=1)
    chunk_index = models.IntegerField()  # 0..N on that page or doc
    content = models.TextField()
    tokens = models.IntegerField(default=0)
    embedding = VectorField(
        dimensions=EMBEDDING_DIMENSIONS, null=True
    )  # keep in sync with your embedding model

    class Meta:
        indexes = [
            HnswIndex(
                name='docchunk_embedding_hnsw_cosine',
                fields=['embedding'],
                m=16,
                ef_construction=64,
                # OpenAI embeddings are L2 - normalized
                # Cosine similarity is scale-invariant, so it works consistently across documents.
                # It’s the metric OpenAI recommends for retrieval tasks.
                opclasses=['vector_cosine_ops'],
            ),
            models.Index(fields=['document', 'chunk_index']),
        ]
        ordering = ['document_id', 'page_number', 'chunk_index']
