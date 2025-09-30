from server.apps.documents.choices import RagBackendChoices

RAG = {
    'EMBED_BACKEND': RagBackendChoices.OPENAI,
    'EMBED_MODEL': 'text-embedding-3-small',
    'EMBED_DIM': 1536,
    'OLLAMA_URL': 'http://ollama:11434',
    'CHUNK_SIZE': 900,
    'CHUNK_OVERLAP': 200,
    'TOP_K': 6,
}
