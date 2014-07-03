from django.conf import settings
from django.contrib.contenttypes.generic import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db.models import ForeignKey, FileField, CharField, Model, TextField, PositiveIntegerField, ImageField
from mezzanine.core.fields import RichTextField
from mezzanine.pages.models import Page


class Tag(Model):
    texto = CharField(max_length=64)

    class Meta:
        ordering = ('texto', )

    def __unicode__(self):
        return self.texto


class TaggedItem(Model):

    tag = ForeignKey(Tag, related_name='itens')

    content_type = ForeignKey(ContentType)
    object_id = PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')


class ManualPage(Page):

    def __unicode__(self):
        return self.title


class Manual(Model):
    titulo = CharField(max_length=128)
    descricao = TextField(blank=True, default='')
    arquivo = FileField(upload_to='uploads/manuais')
    pagina = ForeignKey(ManualPage, related_name='manuais')
    tags = GenericRelation('TaggedItem')


class GlossarioPage(Page):

    def __unicode__(self):
        return self.title


class Item(Model):
    pagina = ForeignKey(GlossarioPage, related_name='itens')
    termo = CharField(max_length=128)
    descricao = TextField()
    tags = GenericRelation('TaggedItem')

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
    answer = RichTextField()
    page = ForeignKey(FAQPage, related_name="questions")
    tags = GenericRelation('TaggedItem')


class FerramentasPage(Page):
    pass


class TutorialPage(Page):
    class Meta:
        verbose_name = 'Tutorial Page'

    def __unicode__(self):
        return self.title


class Tutorial(Model):
    titulo = TextField()
    texto = RichTextField()
    page = ForeignKey(TutorialPage, related_name="tutoriais")
    tags = GenericRelation('TaggedItem')


class VideoTutorialPage(Page):
    class Meta:
        verbose_name = 'VideoTutorial Page'

    def __unicode__(self):
        return self.title


class VideoTutorial(Model):
    titulo = CharField(max_length=128)
    descricao = RichTextField()
    page = ForeignKey(VideoTutorialPage, related_name='videos')
    video_url = CharField(max_length=256)
    video_thumb = ImageField(upload_to='uploads/video-thumbs/')


class SSLCheckerPage(Page):
    pass


class CSRDecoderPage(Page):
    pass


class CertificateKeyMatcherPage(Page):
    pass


class SSLConverterPage(Page):
    pass