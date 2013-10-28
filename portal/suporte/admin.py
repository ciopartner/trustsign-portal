from django.contrib import admin
from django.contrib.contenttypes.generic import GenericTabularInline
from django.forms import ModelForm, ModelMultipleChoiceField
from mezzanine.pages.admin import PageAdmin
from portal.suporte.models import Manual, ManualPage, Item, GlossarioPage, FAQPage, Question, FerramentasPage, \
    TaggedItem, Tag


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


class QuestionForm(ModelForm):
    tags_field = ModelMultipleChoiceField(Tag.objects.all(), required=False, label='tags')

    class Meta:
        fields = ['question', 'answer', 'tags_field']
        model = Question

    def __init__(self, *args, **kwargs):
        super(QuestionForm, self).__init__(*args, **kwargs)
        self.fields['tags_field'].initial = [taggeditem.tag for taggeditem in self.instance.tags.all()]

    def save(self, commit=True):
        question = super(QuestionForm, self).save(commit=True)

        tags = self.cleaned_data['tags_field']

        question.tags.exclude(tag__in=tags).delete()

        for tag in tags:
            if not question.tags.filter(tag=tag).exists():
                question.tags.create(tag=tag)

        return question


class QuestionAdminInline(admin.TabularInline):
    model = Question
    inlines = (TaggedItemInline, )
    form = QuestionForm


class FAQPageAdmin(PageAdmin):
    inlines = [QuestionAdminInline, TaggedItemInline]


admin.site.register(FAQPage, FAQPageAdmin)
admin.site.register(ManualPage, ManualPageAdmin)
admin.site.register(GlossarioPage, GlossarioPageAdmin)
admin.site.register(FerramentasPage, PageAdmin)
admin.site.register(Tag)
admin.site.register(TaggedItem)