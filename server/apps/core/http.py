# Typing pattern recommended by django-stubs:
# https://github.com/typeddjango/django-stubs#how-can-i-create-a-httprequest-thats-guaranteed-to-have-an-authenticated-user
from django.http import HttpRequest

from server.apps.users.models import User


class AuthenticatedHttpRequest(HttpRequest):
    user: User
