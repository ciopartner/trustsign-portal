def url(request):
    from django.conf import settings
    return {'url_portal':settings.URL_PORTAL, 'url_ecommerce': settings.URL_ECOMMERCE}
