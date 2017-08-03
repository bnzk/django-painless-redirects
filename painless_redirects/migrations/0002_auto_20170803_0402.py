# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('painless_redirects', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='redirect',
            name='new_path',
            field=models.CharField(help_text='Absolute path, or full url (with http://.../).', max_length=255, verbose_name='To path'),
        ),
    ]
