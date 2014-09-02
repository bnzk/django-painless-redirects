# coding: utf-8
from django.dispatch import receiver
from django.db.models.signals import pre_save
from cms.models import Title
from painless_redirects.models import Redirect


@receiver(pre_save, sender=Title)
def old_page_slug2redirect(sender, instance, **kwargs):
    """
    automatically insert redirect if slug changes.
    """
    try:
        old = Title.objects.get(pk=instance.id)
    except Title.DoesNotExist:
        # newly created page
        return

    if (instance.path != old.path):
        redirects = Redirect.objects.filter(
            old_path="/%s/%s/" % (instance.language, instance.path), domain="")
        redirects.delete()

        # check if the old path is really a 404.
        # TODO: check with reverse?!
        check = Title.objects.filter(path=old.path).exclude(pk=instance.id)
        if check.count():
            return
        else:
            redirect = Redirect(
                old_path="/%s/%s/" % (instance.language, old.path),
                new_path="/%s/%s/" % (instance.language, instance.path))
            redirect.save()
