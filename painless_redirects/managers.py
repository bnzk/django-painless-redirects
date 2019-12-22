from django.db import models


class RedirectQuerySet(models.QuerySet):

    def enabled(self):
        return self.filter(enabled=True)
