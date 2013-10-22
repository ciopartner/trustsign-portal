from django.contrib import admin
from mezzanine.blog.models import BlogPost
from mezzanine.blog.admin import BlogPostAdmin as CoreBlogPostAdmin
from portal.home.models import TrustSignProfile


class BlogPostAdmin(CoreBlogPostAdmin):
    def __init__(self, *args, **kwargs):
        super(BlogPostAdmin, self).__init__(*args, **kwargs)
        self.fieldsets[0][1]["fields"].insert(-2, "user")

    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        formfield = super(BlogPostAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)
        if db_field.name == "user":
            formfield.initial = request.user.id
        return formfield

admin.site.unregister(BlogPost)

admin.site.register(BlogPost, BlogPostAdmin)

admin.site.register(TrustSignProfile)