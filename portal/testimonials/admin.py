from django.contrib import admin
from .models import Testimonial


class TestimonialAdmin(admin.ModelAdmin):
    list_filter = ('name',)
    list_display = ('_order', 'name', 'testimonial')
    list_editable = ('_order',)
    list_display_links = ('name', 'testimonial')

admin.site.register(Testimonial, TestimonialAdmin)