from django.contrib import admin
from django.contrib.contenttypes.generic import GenericTabularInline
from django.forms import ModelForm, ModelMultipleChoiceField
from mezzanine.pages.admin import PageAdmin
from portal.suporte.models import Manual, ManualPage, Item, GlossarioPage, FAQPage, Question, FerramentasPage, \
    TaggedItem, Tag, TutorialPage, Tutorial


class TaggedItemInline(GenericTabularInline):
    model = TaggedItem


class ManualAdminInline(admin.TabularInline):
    model = Manual


class ManualPageAdmin(PageAdmin):
    inlines = (ManualAdminInline, TaggedItemInline)


class ItemAdminInline(admin.TabularInline):
    model = Item


class GlossarioPageAdmin(PageAdmin):
    inlines = (ItemAdminInline, TaggedItemInline)


class TaggedItemForm(ModelForm):
    tags_field = ModelMultipleChoiceField(Tag.objects.all(), required=False, label='tags')

    def __init__(self, *args, **kwargs):
        super(TaggedItemForm, self).__init__(*args, **kwargs)
        self.fields['tags_field'].initial = [taggeditem.tag for taggeditem in self.instance.tags.all()]

    def save(self, commit=True):
        item = super(TaggedItemForm, self).save(commit=commit)
        if commit:
            tags = self.cleaned_data['tags_field']

            item.tags.exclude(tag__in=tags).delete()

            for tag in tags:
                if not item.tags.filter(tag=tag).exists():
                    item.tags.create(tag=tag)

        return item


class QuestionForm(TaggedItemForm):

    class Meta:
        fields = ['question', 'answer', 'tags_field']
        model = Question


class QuestionAdminInline(admin.TabularInline):
    model = Question
    form = QuestionForm


class FAQPageAdmin(PageAdmin):
    inlines = [QuestionAdminInline, TaggedItemInline]


class TutorialForm(TaggedItemForm):

    class Meta:
        fields = ['titulo', 'texto', 'tags_field']
        model = Tutorial


class TutorialAdminInline(admin.TabularInline):
    model = Tutorial
    form = TutorialForm


class TutorialPageAdmin(PageAdmin):
    inlines = [TutorialAdminInline, TaggedItemInline]


admin.site.register(FAQPage, FAQPageAdmin)
admin.site.register(TutorialPage, TutorialPageAdmin)
admin.site.register(ManualPage, ManualPageAdmin)
admin.site.register(GlossarioPage, GlossarioPageAdmin)
admin.site.register(FerramentasPage, PageAdmin)
admin.site.register(Tag)
admin.site.register(TaggedItem)