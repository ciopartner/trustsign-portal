import zlib


def url(request):
    from django.conf import settings
    return {'url_portal':settings.URL_PORTAL, 'url_ecommerce': settings.URL_ECOMMERCE, 'url_continuar_comprando' : settings.URL_CONTINUAR_COMPRANDO}


def quantidade_carrinho(request):
    from django.conf import settings
    cookie_key = settings.OSCAR_BASKET_COOKIE_OPEN
    ids = []
    user = request.user
    from django.db import connection
    cursor = connection.cursor()

    if cookie_key in request.COOKIES:
        # se o usuario tem uma basket de quando estava sem login
        parts = request.COOKIES[cookie_key].split("_")
        if len(parts) == 2:
            basket_id, basket_hash_cookie = parts
            basket_hash = str(zlib.crc32(str(basket_id) + settings.SECRET_KEY))
            if basket_hash == basket_hash_cookie:
                ids.append(str(basket_id))

    if user.is_authenticated():
        # se tiver logado ele pode ter diversas baskets que o oscar vai fazer um merge
        cursor.execute("SELECT id FROM basket_basket WHERE status='Open' owner_id=%s", [user.pk])
        for row in cursor.fetchall():
            ids.append(str(row[0]))

    if ids:
        cursor.execute("SELECT SUM(quantity) FROM basket_line WHERE basket_id IN (%s)" % ','.join(ids))
        row = cursor.fetchone()
        return {'qtd_itens_carrinho': row[0]}

    return {'qtd_itens_carrinho': 0}

