from django.conf import settings
from django.db.models import ForeignKey, FileField, CharField, Model, TextField
from mezzanine.pages.models import Page


class ManualPage(Page):

    def __unicode__(self):
        return self.title


class Manual(Model):
    titulo = CharField(max_length=128)
    descricao = TextField(blank=True, default='')
    arquivo = FileField(upload_to='uploads/manuais')
    pagina = ForeignKey(ManualPage, related_name='manuais')


class GlossarioPage(Page):

    def __unicode__(self):
        return self.title


class Item(Model):
    pagina = ForeignKey(GlossarioPage, related_name='itens')
    termo = CharField(max_length=128)
    descricao = TextField()

    class Meta:
        ordering = ('termo', )


class FAQPage(Page):
    class Meta:
        verbose_name = 'FAQ Page'

    def __unicode__(self):
        return self.title

    def save(self, *args, **kwargs):
        """
        Update the URL slug if settings.UPDATE_SLUG is True.
        """
        if getattr(settings, 'UPDATE_SLUG', False):
            self.slug = self.get_slug()
        super(FAQPage, self).save(*args, **kwargs)


class Question(Model):
    question = TextField()
    answer = TextField()
    page = ForeignKey(FAQPage, related_name="questions")