import json
from django.http import HttpResponse
from django.views.generic import TemplateView, CreateView, FormView


class JSONResponseMixin(object):
    """
    A mixin that can be used to render a JSON response.
    """
    def render_to_json_response(self, context, **response_kwargs):
        """
        Returns a JSON response, transforming 'context' to make the payload.
        """
        return HttpResponse(
            self.convert_context_to_json(context),
            content_type='application/json',
            mimetype='text/json; charset=UTF-8',
            **response_kwargs
        )

    def convert_context_to_json(self, context):
        "Convert the context dictionary into a JSON object"
        # Note: This is *EXTREMELY* naive; in reality, you'll need
        # to do much more complex handling to ensure that arbitrary
        # objects -- such as Django model instances or querysets
        # -- can be serialized as JSON.
        return json.dumps(context, ensure_ascii=False)


class JSONView(JSONResponseMixin, TemplateView):
    def render_to_response(self, context, **response_kwargs):
        if 'erro' in context:
            response_kwargs['status'] = 400
        return self.render_to_json_response(context, **response_kwargs)


class JSONFormView(JSONResponseMixin, FormView):
    def render_to_response(self, context, **response_kwargs):
        return self.render_to_json_response(context, **response_kwargs)


class JSONCreateView(JSONResponseMixin, CreateView):
    def render_to_response(self, context, **response_kwargs):
        return self.render_to_json_response(context, **response_kwargs)


class CollectStaticView(TemplateView):
    template_name = 'collect_static.html'

    def get_context_data(self, **kwargs):
        if not self.request.user.is_superuser:
            raise PermissionDenied
        context = super(CollectStaticView, self).get_context_data(**kwargs)
        from django.core import management
        f = StringIO()
        management.call_command('collectstatic', noinput=True, stdout=f, interactive=False)
        context['stdout'] = f.getvalue()
        return context