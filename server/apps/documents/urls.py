from django.urls import path

from server.apps.documents.logic.document_create import DocumentCreateView
from server.apps.documents.logic.document_delete import DocumentDeleteView
from server.apps.documents.logic.document_edit import DocumentUpdateView
from server.apps.documents.logic.document_list import DocumentListView

urlpatterns = [
    path('', DocumentListView.as_view(), name='document_list'),
    path('upload/', DocumentCreateView.as_view(), name='document_upload'),
    path(
        '<uuid:uuid>/edit/', DocumentUpdateView.as_view(), name='document_edit'
    ),
    path(
        '<uuid:uuid>/delete/',
        DocumentDeleteView.as_view(),
        name='document_delete',
    ),
]
