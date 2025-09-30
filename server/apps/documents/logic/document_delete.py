from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import DeleteView

from server.apps.documents.models import Document


class DocumentDeleteView(LoginRequiredMixin, DeleteView):
    model = Document
    template_name = 'documents/document_confirm_delete.html'
    success_url = reverse_lazy('document_list')
    slug_field = 'uuid'
    slug_url_kwarg = 'uuid'

    def get_queryset(self):
        # Ensure users can only delete their own documents
        return Document.objects.filter(user=self.request.user)
