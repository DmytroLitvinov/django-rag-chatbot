from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.shortcuts import redirect
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView

from server.apps.chatbot.choices import ConversationTypeChoices
from server.apps.chatbot.models import Conversation, Message
from server.apps.core.http import AuthenticatedHttpRequest
from server.apps.documents.models import Document


@method_decorator(csrf_exempt, name='dispatch')
class HomepageView(LoginRequiredMixin, TemplateView):
    """Claude.ai-style homepage showing recent conversations"""

    template_name = 'chatbot/homepage.html'

    def post(self, request, *args, **kwargs):
        """Handle new conversation creation from homepage"""
        message_content = request.POST.get('message', '').strip()
        document_ids = request.POST.getlist('documents')

        if not message_content:
            return HttpResponse('Message cannot be empty', status=400)

        # Create new conversation
        # TODO: add type depending if file was uploaded
        conversation = Conversation.objects.create(
            user=request.user,
            title=(
                message_content[:50] + '...'
                if len(message_content) > 50
                else message_content
            ),
            type=ConversationTypeChoices.DOCUMENT
            if document_ids
            else ConversationTypeChoices.CHAT,
        )

        if document_ids:
            docs = Document.objects.filter(
                id__in=document_ids, user=request.user
            )
            conversation.documents.set(docs)

        # Save the initial message
        Message.objects.create(
            conversation=conversation,
            user=conversation.user,
            content=message_content,
            is_user=True,
        )

        # Redirect to the new chat where streaming will occur
        return redirect('chat', conversation_id=conversation.id)

    def get_context_data(self, **kwargs):
        self.request: AuthenticatedHttpRequest
        context = super().get_context_data(**kwargs)
        context['recent_conversations'] = Conversation.objects.filter(
            user=self.request.user
        ).recent()
        context['recent_documents_conversations'] = (
            Conversation.objects.filter(user=self.request.user)
            .filter_document_type()
            .recent()
        )
        context['documents'] = Document.objects.filter(user=self.request.user)
        return context
