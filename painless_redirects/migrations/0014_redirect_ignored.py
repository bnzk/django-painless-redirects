# Generated by Django 2.2.17 on 2020-11-24 03:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('painless_redirects', '0013_auto_20201120_0911'),
    ]

    operations = [
        migrations.AddField(
            model_name='redirect',
            name='ignored',
            field=models.BooleanField(default=False, help_text='Shall this redirect be ignored? (use to tighen/cleanup your redirects list)', verbose_name='Ignored'),
        ),
    ]