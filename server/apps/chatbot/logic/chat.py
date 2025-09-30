from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.template.defaultfilters import linebreaksbr
from django.utils.decorators import method_decorator
from django.utils.html import escape
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import DetailView

from server.apps.chatbot.choices import ConversationTypeChoices
from server.apps.chatbot.constants import ERROR_MESSAGES
from server.apps.chatbot.models import Conversation
from server.apps.chatbot.services import ConversationService
from server.apps.chatbot.utils import render_markdown
from server.apps.documents.prompting import build_prompt
from server.apps.documents.retriever import retrieve_chunks


@method_decorator(csrf_exempt, name='dispatch')
class ChatView(DetailView):
    """Individual chat conversation view - handles both GET and POST"""

    model = Conversation
    template_name = 'chatbot/chat.html'
    context_object_name = 'conversation'
    pk_url_kwarg = 'conversation_id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        conversation = self.object

        # Process messages for display
        messages_with_content = []
        for message in conversation.messages.all():
            if message.is_user:
                # User messages: simple line breaks
                formatted_content = linebreaksbr(escape(message.content))
            else:
                # AI messages: render markdown
                formatted_content = render_markdown(message.content)

            messages_with_content.append({
                'original': message,
                'formatted_content': formatted_content,
            })

        context.update({
            'messages': conversation.messages.all(),
            'messages_with_content': messages_with_content,
        })
        return context

    def post(self, request, conversation_id):
        """Handle new messages in existing chat - returns HTML with SSE endpoint info"""
        message_content = request.POST.get('message', '').strip()

        if not message_content:
            return HttpResponse(ERROR_MESSAGES['EMPTY_MESSAGE'], status=400)

        conversation = get_object_or_404(Conversation, id=conversation_id)

        # Save user message using service
        user_message = ConversationService.add_user_message(
            conversation, message_content
        )

        # 2. If DOCUMENT chat → build RAG prompt
        if conversation.type == ConversationTypeChoices.DOCUMENT:
            chunks = retrieve_chunks(conversation, message_content)
            prompt = build_prompt(message_content, chunks)
            # replace user_message.content with RAG prompt for the AI only
            # (but keep original content visible in UI)
            ai_input = prompt
        else:
            ai_input = message_content

        # Store somewhere accessible by your SSE stream endpoint
        request.session[f'rag_prompt_{user_message.id}'] = ai_input

        # Format user content
        user_formatted = linebreaksbr(escape(user_message.content))

        # Return user message HTML and placeholder for AI response with SSE
        return HttpResponse(
            f"""
            <!-- User Message -->
            <div class="d-flex justify-content-end mb-3 fade-in">
                <div class="message-bubble user-message rounded-3 px-3 py-2">
                    <div class="mb-1">{user_formatted}</div>
                    <small class="opacity-75">{user_message.created_at.astimezone().strftime('%I:%M %p').lstrip('0').replace(' 0', ' ')}</small>
                </div>
            </div>

            <!-- AI Message Placeholder -->
            <div class="d-flex justify-content-start mb-3 fade-in" id="ai-response-{user_message.id}">
                <div class="me-2">
                    <div class="ai-avatar rounded-circle d-flex align-items-center justify-content-center fw-bold">
                        G3
                    </div>
                </div>
                <div class="message-bubble ai-message rounded-3 px-3 py-2">
                    <div class="mb-1 text-break markdown-content" id="ai-content-{user_message.id}"></div>
                    <small class="text-muted" id="ai-timestamp-{user_message.id}"></small>
                </div>
            </div>

            <!-- SSE Script for Streaming -->
            <script>
                (function() {{
                const eventSource = new EventSource('/chat/{conversation.id}/stream/?message_id={user_message.id}');
                let aiContent = '';
                const contentDiv = document.getElementById('ai-content-{user_message.id}');
                const timestampDiv = document.getElementById('ai-timestamp-{user_message.id}');

                eventSource.onmessage = function(event) {{
                    const data = JSON.parse(event.data);

                    if (data.type === 'token') {{
                        aiContent += data.content;
                        contentDiv.textContent = aiContent;
                    }} else if (data.type === 'done') {{
                        timestampDiv.innerHTML = data.timestamp + ' • Gemma 3 4B';
                        eventSource.close();
                        // Convert markdown to HTML
                        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]');
                        if (csrfToken) {{
                            fetch('/chat/{conversation.id}/render-markdown/', {{
                                method: 'POST',
                                headers: {{
                                    'Content-Type': 'application/json',
                                    'X-CSRFToken': csrfToken.value
                                }},
                                body: JSON.stringify({{content: aiContent}})
                            }})
                            .then(response => response.text())
                            .then(html => {{
                                contentDiv.innerHTML = html;
                                hljs.highlightAll();
                            }});
                        }} else {{
                            // Fallback if no CSRF token - just display raw content
                            contentDiv.innerHTML = aiContent;
                        }}
                    }}
                }};

                eventSource.onerror = function(event) {{
                    console.error('SSE error:', event);
                    console.error('ReadyState:', eventSource.readyState);
                    eventSource.close();
                    contentDiv.innerHTML = '<em>Error: Connection lost. Check console for details.</em>';
                }};
                }})();
            </script>
        """
        )
