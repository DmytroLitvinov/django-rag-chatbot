from pgvector.django import CosineDistance

from server.apps.chatbot.models import Conversation
from server.apps.documents import configuration
from server.apps.documents.embeddings import EmbeddingService
from server.apps.documents.models import DocumentChunk


def retrieve_chunks(conversation: Conversation, question: str, top_k=None):
    top_k = top_k or configuration.RAG['TOP_K']

    # 1. Embed the question
    embedder = EmbeddingService()
    [q_emb] = embedder.embed([question])

    # 2. Restrict to docs in this conversation
    docs = conversation.documents.all()
    if not docs.exists():
        return []

    # 3. Query pgvector index
    qs = (
        DocumentChunk.objects.filter(document__in=docs)
        .annotate(distance=CosineDistance('embedding', q_emb))
        .order_by('distance')[:top_k]
    )
    return list(qs)
