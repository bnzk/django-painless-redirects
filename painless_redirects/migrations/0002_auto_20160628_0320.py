# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('painless_redirects', '0001_squashed_0002_auto_20150903_0643'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='redirect',
            options={'ordering': ('old_path',), 'verbose_name': 'Redirect', 'verbose_name_plural': 'Redirects'},
        ),
        migrations.AlterUniqueTogether(
            name='redirect',
            unique_together=set([('site', 'domain', 'old_path')]),
        ),
    ]
