from django.db.models import ForeignKey, FileField, CharField, Model
from mezzanine.pages.models import Page


class ManualPage(Page):
    class Meta:
        verbose_name = 'Manual Page'

    def __unicode__(self):
        return self.title


class Manual(Model):
    titulo = CharField(max_length=128)
    arquivo = FileField(upload_to='uploads/manuais')
    pagina = ForeignKey(ManualPage, related_name='manuais')