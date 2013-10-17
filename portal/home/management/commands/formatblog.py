#-*- coding: utf-8
from django.core.management.base import BaseCommand, CommandError
from mezzanine.blog.models import BlogPost
import re

class Command(BaseCommand):
    args = '<old_url new_url>'
    help = 'Converte um arquivo wordpress para a arquitetura do projeto'

    def handle(self, *args, **options):

        try:
            old_url = args[0]
        except:
            old_url = 'http://www.trustsign.com.br/blog/wp-content/uploads/'

        try:
            new_url = args[1]
        except:
            new_url = '/static/media/uploads/blog/'


        print("Substituindo a URL " + old_url + " por " + new_url)

        posts = BlogPost.objects.all()

        for post in posts:

            print("- Formatando o post " + post.title)

            post.content = re.sub('(' + old_url + ')[0-9]{4}/[0-9]{2}/', new_url, post.content)
            post.save()