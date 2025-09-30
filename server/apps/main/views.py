from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render


def index(request: HttpRequest) -> HttpResponse:
    """
    Main (or index) view.

    Returns rendered default page to the user.
    Typed with the help of ``django-stubs`` project.
    """
    if request.user.is_authenticated:
        return redirect('homepage')
    return render(request, 'main/index.html')
