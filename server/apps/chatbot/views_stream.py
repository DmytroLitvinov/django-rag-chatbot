import json

import httpx
from django.http import HttpResponse, JsonResponse, StreamingHttpResponse
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View
from django.views.generic.detail import SingleObjectMixin

from ..documents.prompting import build_prompt
from ..documents.retriever import retrieve_chunks
from .constants import ERROR_MESSAGES, OLLAMA_CHAT_ENDPOINT, OLLAMA_MODEL
from .models import Conversation, Message
from .services import ConversationService
from .utils import render_markdown


@method_decorator(csrf_exempt, name='dispatch')
class StreamChatView(SingleObjectMixin, View):
    """SSE endpoint for streaming AI responses"""

    model = Conversation
    pk_url_kwarg = 'conversation_id'

    def get(self, request, *args, **kwargs):
        """Stream AI response using Server-Sent Events"""
        message_id = request.GET.get('message_id')
        if not message_id:
            return HttpResponse('Missing message_id', status=400)

        self.object = self.get_object()
        conversation = self.object
        user_message = get_object_or_404(
            Message, id=message_id, conversation=conversation, is_user=True
        )

        # Build conversation context
        # Default: take last 10 msgs as Ollama context
        messages = list(conversation.messages.all().order_by('created_at'))
        ollama_messages = []
        for msg in messages[-10:]:
            role = 'user' if msg.is_user else 'assistant'
            ollama_messages.append({'role': role, 'content': msg.content})

        # If DOCUMENT conversation, replace last user msg with RAG prompt
        if conversation.is_document_type:
            chunks = retrieve_chunks(conversation, user_message.content)
            prompt = build_prompt(user_message.content, chunks)

            if ollama_messages and ollama_messages[-1]['role'] == 'user':
                ollama_messages[-1]['content'] = prompt

        def generate():
            """Generator function for SSE streaming"""
            full_response = ''

            try:
                print('📌 [DEBUG] ollama_messages:')
                for m in ollama_messages:
                    print(m['role'].upper(), '=>', m['content'][:300], '...\n')

                # Use synchronous httpx client with stream
                with httpx.Client(timeout=60.0) as client:
                    with client.stream(
                        'POST',
                        OLLAMA_CHAT_ENDPOINT,
                        json={
                            'model': OLLAMA_MODEL,
                            'messages': ollama_messages,
                            'stream': True,
                        },
                    ) as response:
                        for line in response.iter_lines():
                            if line:
                                try:
                                    data = json.loads(line)
                                    if (
                                        'message' in data
                                        and 'content' in data['message']
                                    ):
                                        token = data['message']['content']
                                        full_response += token
                                        yield f'data: {json.dumps({"type": "token", "content": token})}\n\n'
                                except json.JSONDecodeError:
                                    continue
                                except Exception as e:
                                    yield f'data: {json.dumps({"type": "error", "content": f"Parse error: {e!s}"})}\n\n'
            except Exception as e:
                yield f'data: {json.dumps({"type": "error", "content": f"Connection error: {e!s}"})}\n\n'
                return

            # Save the complete message if we got a response
            if full_response:
                ai_message = ConversationService.add_ai_message(
                    conversation, full_response
                )
                # Send completion signal
                # Convert to local timezone and format to match Django templates (g:i A format)
                local_time = ai_message.created_at.astimezone()
                timestamp_str = (
                    local_time.strftime('%I:%M %p')
                    .lstrip('0')
                    .replace(' 0', ' ')
                )
                yield f'data: {json.dumps({"type": "done", "timestamp": timestamp_str})}\n\n'
            else:
                yield f'data: {json.dumps({"type": "error", "content": ERROR_MESSAGES["NO_RESPONSE"]})}\n\n'

        response = StreamingHttpResponse(
            generate(), content_type='text/event-stream'
        )
        response['Cache-Control'] = 'no-cache'
        response['X-Accel-Buffering'] = 'no'
        return response


@method_decorator(csrf_exempt, name='dispatch')
class RenderMarkdownView(View):
    """API endpoint to render markdown to HTML"""

    def post(self, request, conversation_id):
        """Render markdown content to HTML"""
        try:
            data = json.loads(request.body)
            content = data.get('content', '')
            rendered = render_markdown(content)
            return HttpResponse(rendered)
        except json.JSONDecodeError:
            return JsonResponse(
                {'error': ERROR_MESSAGES['INVALID_JSON']}, status=400
            )
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
