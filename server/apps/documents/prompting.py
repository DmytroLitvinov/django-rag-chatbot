def build_prompt(question: str, chunks):
    context = '\n\n---\n'.join(
        f'[Page {c.page_number}] {c.content}' for c in chunks
    )
    return f"""You are a helpful assistant. Use only the context to answer.

Context:
{context}

Question: {question}

Answer concisely. If not in context, say "I don’t know." in the language of the question.
"""
