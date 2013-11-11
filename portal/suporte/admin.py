from django.contrib import admin
from django.forms import ModelForm, ModelMultipleChoiceField
from mezzanine.pages.admin import PageAdmin
from portal.suporte.models import Manual, ManualPage, Item, GlossarioPage, FAQPage, Question, FerramentasPage, \
    TaggedItem, Tag, TutorialPage, Tutorial, VideoTutorialPage, VideoTutorial


class TaggedItemForm(ModelForm):
    tags_field = ModelMultipleChoiceField(Tag.objects.all(), required=False, label='tags')

    def __init__(self, *args, **kwargs):
        super(TaggedItemForm, self).__init__(*args, **kwargs)
        self.fields['tags_field'].initial = [taggeditem.tag for taggeditem in self.instance.tags.all()]

    def save(self, commit=True):
        item = super(TaggedItemForm, self).save(commit=commit)

        def save_m2m():
            tags = self.cleaned_data['tags_field']

            item.tags.exclude(tag__in=tags).delete()

            for tag in tags:
                if not item.tags.filter(tag=tag).exists():
                    item.tags.create(tag=tag)

        if not commit:
            self.save_m2m = save_m2m
        else:
            save_m2m()

        return item


class QuestionForm(TaggedItemForm):

    class Meta:
        fields = ['question', 'answer', 'tags_field']
        model = Question


class QuestionAdminInline(admin.TabularInline):
    model = Question
    form = QuestionForm


class FAQPageAdmin(PageAdmin):
    inlines = [QuestionAdminInline]


class TutorialForm(TaggedItemForm):

    class Meta:
        fields = ['titulo', 'texto', 'tags_field']
        model = Tutorial


class TutorialAdminInline(admin.TabularInline):
    model = Tutorial
    form = TutorialForm


class TutorialPageAdmin(PageAdmin):
    inlines = [TutorialAdminInline]


class ItemForm(TaggedItemForm):

    class Meta:
        fields = ['termo', 'descricao', 'tags_field']
        model = Item


class ItemAdminInline(admin.TabularInline):
    model = Item
    form = ItemForm


class GlossarioPageAdmin(PageAdmin):
    inlines = (ItemAdminInline,)


class ManualForm(TaggedItemForm):

    class Meta:
        fields = ['titulo', 'descricao', 'arquivo', 'tags_field']
        model = Manual


class ManualAdminInline(admin.TabularInline):
    model = Manual
    form = ManualForm


class ManualPageAdmin(PageAdmin):
    inlines = (ManualAdminInline,)


class VideoTutorialPageAdmin(PageAdmin):
    model = VideoTutorialPage

admin.site.register(FAQPage, FAQPageAdmin)
admin.site.register(TutorialPage, TutorialPageAdmin)
admin.site.register(ManualPage, ManualPageAdmin)
admin.site.register(GlossarioPage, GlossarioPageAdmin)
admin.site.register(FerramentasPage, PageAdmin)
admin.site.register(VideoTutorialPage, VideoTutorialPageAdmin)
admin.site.register(Tag)
admin.site.register(TaggedItem)
admin.site.register(VideoTutorial)
