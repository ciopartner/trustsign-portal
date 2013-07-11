# -*- coding: utf-8 -*-
from django.db import models
from mezzanine.pages.models import Page

# The members of Page will be inherited by the Author model, such
# as title, slug, etc. For authors we can use the title field to
# store the author's name. For our model definition, we just add
# any extra fields that aren't part of the Page model, in this
# case, date of birth.

# class Home(Page):
#
#     dob = models.DateField("Date of birth")
#
# class Book(models.Model):
#     author = models.ForeignKey("Author")
#     cover = models.ImageField(upload_to="authors")


class TrustSignProfile(models.Model):
    user = models.OneToOneField("auth.User")
    date_of_birth = models.DateField()
    bio = models.TextField()
    tagline = models.TextField()