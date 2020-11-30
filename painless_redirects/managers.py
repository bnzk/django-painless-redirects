from django.db import models
# from django.db.models import Sum


class RedirectQuerySet(models.QuerySet):

    # def __init__(self, *args, **kwargs):
    #     qs = super().__init__(*args, **kwargs)
    #     qs = qs.annotate(total_hits=Sum('redirecthit__hits'))  # .order_by('total_hits')
    #     return qs

    def enabled(self):
        return self.filter(enabled=True)
