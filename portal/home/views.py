from django.conf import settings
from django.contrib.auth import login as auth_login
from django.http import HttpResponseRedirect
from django.shortcuts import resolve_url
from django.utils.http import is_safe_url
from django.views.generic import TemplateView
from mezzanine.utils.views import render
from django.utils.translation import ugettext as _
from .forms import LoginForm
from portal.banners.models import Banners
from portal.testimonials.models import Testimonial


def login(request, template="accounts/login.html"):
    """
    Login form.
    """
    form = LoginForm(request.POST or None)
    if request.method == "POST" and form.is_valid():

        redirect_to = request.REQUEST.get('next', '')
        # Ensure the user-originating redirection url is safe.
        if not is_safe_url(url=redirect_to, host=request.get_host()):
            redirect_to = resolve_url(settings.LOGIN_REDIRECT_URL)

        authenticated_user = form.save()
        auth_login(request, authenticated_user)

        return HttpResponseRedirect(redirect_to)
    context = {"form": form, "title": _("Log in")}
    return render(request, template, context)


class HomeView(TemplateView):
    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        context = super(HomeView, self).get_context_data(**kwargs)
        context['banners'] = Banners.objects.get_in_date()
        context['testimonials'] = Testimonial.objects.all()

        return context