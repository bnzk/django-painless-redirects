# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('painless_redirects', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='redirect',
            name='old_path',
            field=models.CharField(help_text="This should be an absolute path, excluding the domain name. Example: '/events/search/'.", max_length=333, verbose_name='From path'),
        ),
    ]
