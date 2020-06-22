# Generated by Django 2.2.13 on 2020-06-22 03:12

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('painless_redirects', '0011_auto_20200420_0836'),
    ]

    operations = [
        migrations.CreateModel(
            name='RedirectHit',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('referrer', models.CharField(help_text='Where the hit comes from', max_length=800, verbose_name='Referrer')),
                ('hits', models.PositiveIntegerField(default=0, editable=False)),
                ('redirect', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='painless_redirects.Redirect')),
            ],
        ),
    ]
