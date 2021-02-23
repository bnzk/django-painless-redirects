# coding: utf-8
from django.core.management import BaseCommand

from painless_redirects.models import RedirectHit


class Command(BaseCommand):
    help = 'Ensure uniqueness on RedirectHit.referer/redirect. Use if migration 0015 fails.'

    def handle(self, *args, **options):
        qs = RedirectHit.objects.all()
        redirects = []
        redirects_referers = {}
        for hit in qs:
            if hit.redirect not in redirects:
                redirects.append(hit.redirect)
                redirects_referers[hit.redirect.id] = []
                redirects_referers[hit.redirect.id].append(hit.referer)
            else:
                if hit.referer in redirects_referers[hit.redirect.id]:
                    print("found duplicate: {} / {}".format(hit.redirect, hit.referer))
                    hit.delete()
