# -*- coding: utf-8 -*-
from django.conf import settings
from django.contrib.admindocs.tests import fields
from django.db import models
from mezzanine.pages.models import Page
from mezzanine.utils.urls import slugify

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

    class Meta:
        verbose_name = 'Product'
        ordering = ['-order']

    def __unicode__(self):
        return self.title

    def save(self, *args, **kwargs):
        """
        Update the URL slug if settings.UPDATE_SLUG is True.
        """
        if hasattr(settings, 'UPDATE_SLUG') and settings.UPDATE_SLUG:
            self.slug = self.get_slug()
        super(Product, self).save(*args, **kwargs)

    def duplicate(self):
        another_product = self
        another_product.id = Product.objects.count() + 2
        another_product.save()
        for tab in TabContent.objects.all():
            if tab.id > 5:
                break
            another_tab = tab
            another_tab.product = another_product
            another_tab.id = None
            another_tab.save(force_insert=True)
            print another_tab.id


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


class FAQPage(Page):
    class Meta:
        verbose_name = 'FAQ Page'

    def __unicode__(self):
        return self.title

    def save(self, *args, **kwargs):
        """
        Update the URL slug if settings.UPDATE_SLUG is True.
        """
        if hasattr(settings, 'UPDATE_SLUG') and settings.UPDATE_SLUG:
            self.slug = self.get_slug()
        super(FAQPage, self).save(*args, **kwargs)


class Question(models.Model):
    question = models.TextField()
    answer = models.TextField()
    page = models.ForeignKey(FAQPage, related_name="questions")


