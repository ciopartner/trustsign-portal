# -*- coding: utf-8 -*-
from django.conf import settings
from django.db import models
from mezzanine.pages.models import Page

# The members of Page will be inherited by the Author model, such
# as title, slug, etc. For authors we can use the title field to
# store the author's name. For our model definition, we just add
# any extra fields that aren't part of the Page model, in this
# case, date of birth.


class Products(Page):
    """
    Esta Page é responsável por armazenar o conteúdo da página 'Certificado Digital',
      ou seja, a lista de produtos
    """
    # dob = models.DateField("Date of birth")
    pass


class Product(Page):
    """
    This page is responsible for storing the Content of each Product Page
    """
    subtitle = models.CharField('Subtitle', max_length=256, blank=True)
    youtube_title = models.CharField('YouTube Title', max_length=256)
    youtube_url = models.URLField('YouTube URL')
    tab_title = models.CharField('Tab Title', max_length=256)
    cart_add_url = models.CharField('Add to Cart URL', max_length=64, blank=True)
    order = models.IntegerField('Order', default=999)

    product_code = models.CharField('Código do produto', blank=True, null=True, max_length=16)

    class Meta:
        verbose_name = 'Product'
        ordering = ['-order']

    def __unicode__(self):
        return self.title

    def save(self, *args, **kwargs):
        """
        Update the URL slug if settings.UPDATE_SLUG is True.
        """
        if getattr(settings, 'UPDATE_SLUG', False):
            self.slug = self.get_slug()
        super(Product, self).save(*args, **kwargs)



class TabContent(models.Model):
    """
    This model is used to configure the tabs in product page.
    """
    tab_title = models.CharField('Tab Title', max_length=256)
    tab_short_description = models.CharField('Tab Short Description', max_length=256)
    tab_description = models.TextField('Tab Description')
    tab_description_image = models.ImageField('Image in Tab Description', upload_to="/", blank=True)
    product = models.ForeignKey(Product, related_name='tabs')

    def __unicode__(self):
        return self.tab_title