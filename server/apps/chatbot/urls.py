from django.urls import path

from .logic.chat import ChatView
from .logic.homepage import HomepageView
from .views_stream import RenderMarkdownView, StreamChatView

urlpatterns = [
    path('', HomepageView.as_view(), name='homepage'),
    path('<int:conversation_id>/', ChatView.as_view(), name='chat'),
    path(
        '<int:conversation_id>/stream/',
        StreamChatView.as_view(),
        name='stream_chat',
    ),
    path(
        '<int:conversation_id>/render-markdown/',
        RenderMarkdownView.as_view(),
        name='render_markdown',
    ),
]
