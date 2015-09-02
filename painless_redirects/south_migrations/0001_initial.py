# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Redirect'
        db.create_table(u'painless_redirects_redirect', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('site', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='redirect_old_site', null=True, to=orm['sites.Site'])),
            ('domain', self.gf('django.db.models.fields.CharField')(max_length=1024, blank=True)),
            ('old_path', self.gf('django.db.models.fields.CharField')(max_length=1024)),
            ('new_path', self.gf('django.db.models.fields.CharField')(max_length=1024)),
            ('new_site', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='redirect_new_site', null=True, to=orm['sites.Site'])),
        ))
        db.send_create_signal(u'painless_redirects', ['Redirect'])


    def backwards(self, orm):
        # Deleting model 'Redirect'
        db.delete_table(u'painless_redirects_redirect')


    models = {
        u'painless_redirects.redirect': {
            'Meta': {'object_name': 'Redirect'},
            'domain': ('django.db.models.fields.CharField', [], {'max_length': '1024', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'new_path': ('django.db.models.fields.CharField', [], {'max_length': '1024'}),
            'new_site': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'redirect_new_site'", 'null': 'True', 'to': u"orm['sites.Site']"}),
            'old_path': ('django.db.models.fields.CharField', [], {'max_length': '1024'}),
            'site': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'redirect_old_site'", 'null': 'True', 'to': u"orm['sites.Site']"})
        },
        u'sites.site': {
            'Meta': {'ordering': "(u'domain',)", 'object_name': 'Site', 'db_table': "u'django_site'"},
            'domain': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        }
    }

    complete_apps = ['painless_redirects']