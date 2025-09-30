import markdown
from django.utils.html import escape
from django.utils.safestring import mark_safe


def render_markdown(content):
    """Convert markdown to HTML safely"""
    md = markdown.Markdown(
        extensions=[
            'fenced_code',
            'tables',
            'nl2br',
        ]
    )
    return mark_safe(md.convert(escape(content)))
