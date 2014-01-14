from django import template
register = template.Library()


@register.filter
def format_cnpj(cnpj):
    if len(cnpj) == 14:
        return "%s.%s.%s/%s-%s" % (cnpj[0:2], cnpj[2:5], cnpj[5:8], cnpj[8:12], cnpj[12:14])

    return cnpj