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
        migrations.AlterField(
            model_name='redirect',
            name='new_path',
            field=models.CharField(help_text='Absolute path, or full url (with http://.../).', max_length=255, verbose_name='To'),
        ),
        migrations.AlterField(
            model_name='redirect',
            name='old_path',
            field=models.CharField(help_text="This should be an absolute path, excluding the domain name. Example: '/events/search/'.", max_length=255, verbose_name='From path'),
        ),
        migrations.AlterUniqueTogether(
            name='redirect',
            unique_together=set([('site', 'domain', 'old_path')]),
        ),
    ]
