from django.contrib.messages import info
from django.contrib.auth import login as auth_login
from mezzanine.utils.urls import login_redirect
from mezzanine.utils.views import render
from django.utils.translation import ugettext as _
from .forms import LoginForm


def login(request, template="accounts/login.html"):
    """
    Login form.
    """
    form = LoginForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        authenticated_user = form.save()
        info(request, _("Successfully logged in"))
        auth_login(request, authenticated_user)
        return login_redirect(request)
    context = {"form": form, "title": _("Log in")}
    return render(request, template, context)
