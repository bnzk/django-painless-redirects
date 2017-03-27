# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sites', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Redirect',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('domain', models.CharField(help_text='Optional, exlicitly limit to specific domain.', max_length=64, blank=True)),
                ('old_path', models.CharField(help_text="This should be an absolute path, excluding the domain name. Example: '/events/search/'.", max_length=255, verbose_name='From path')),
                ('wildcard_match', models.BooleanField(default=False, help_text='Add wildcard (*) to from path', verbose_name='Wildcard mode')),
                ('new_path', models.CharField(help_text='Absolute path, or full url (with http://.../).', max_length=255, verbose_name='To')),
                ('new_site', models.ForeignKey(related_name='redirect_new_site', blank=True, to='sites.Site', help_text='Optional, automatically insert correct domain name of this site.', null=True)),
                ('site', models.ForeignKey(related_name='redirect_old_site', blank=True, to='sites.Site', help_text='Optional, limit redirect to this site.', null=True)),
            ],
            options={
                'ordering': ('old_path',),
                'verbose_name': 'Redirect',
                'verbose_name_plural': 'Redirects',
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='redirect',
            unique_together=set([('site', 'domain', 'old_path')]),
        ),
    ]
