# -*- coding: utf-8 -*-
from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
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
    user = models.OneToOneField(User)
    date_of_birth = models.DateField(blank=True, null=True)
    bio = models.TextField(blank=True)
    tagline = models.TextField(blank=True)


def create_profile(sender, **kwargs):
    if kwargs["created"]:
        profile = TrustSignProfile(user=kwargs['instance'])
        profile.save()

post_save.connect(create_profile, sender=User)