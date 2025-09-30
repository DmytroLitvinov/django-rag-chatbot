from django_tasks import task

from .ingest import ingest_document


@task()
def ingest_document_task(document_id: int):
    ingest_document(document_id)
