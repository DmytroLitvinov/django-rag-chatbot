from braces.views import FormMessagesMixin
from django import forms
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.views.generic import UpdateView

from server.apps.documents.models import Document


class DocumentEditForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ['title', 'description']
        widgets = {
            'title': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Enter title'}
            ),
            'description': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 3,
                    'placeholder': 'Enter description',
                }
            ),
        }


class DocumentUpdateView(LoginRequiredMixin, FormMessagesMixin, UpdateView):
    model = Document
    form_class = DocumentEditForm
    template_name = 'documents/document_form.html'
    context_object_name = 'document'
    slug_url_kwarg = 'uuid'
    slug_field = 'uuid'
    form_valid_message = 'Document updated!'

    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)

    def get_success_url(self):
        return reverse('document_list')
