from server.apps.documents import configuration
from server.apps.documents.choices import RagBackendChoices


class EmbeddingService:
    def __init__(self):
        self.backend = configuration.RAG['EMBED_BACKEND']
        self.model = configuration.RAG['EMBED_MODEL']

        if self.backend == RagBackendChoices.OPENAI:
            from openai import OpenAI

            self.client = OpenAI()

    def embed(self, texts: list[str]) -> list[list[float]]:
        if self.backend == RagBackendChoices.OPENAI:
            # OpenAI supports batching; keep batches modest (e.g. 64)
            resp = self.client.embeddings.create(model=self.model, input=texts)
            return [d.embedding for d in resp.data]
        if self.backend == RagBackendChoices.OLLAMA:
            import requests

            url = f'{configuration.RAG["OLLAMA_URL"]}/api/embeddings'
            out = []
            for t in texts:
                r = requests.post(url, json={'model': self.model, 'prompt': t})
                r.raise_for_status()
                out.append(r.json()['embedding'])
            return out
        raise ValueError(f'Unknown EMBED_BACKEND: {self.backend}')
