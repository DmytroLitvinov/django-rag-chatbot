from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView

from server.apps.documents.models import Document


class DocumentListView(LoginRequiredMixin, ListView):
    model = Document
    template_name = 'documents/document_list.html'
    context_object_name = 'documents'

    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)
