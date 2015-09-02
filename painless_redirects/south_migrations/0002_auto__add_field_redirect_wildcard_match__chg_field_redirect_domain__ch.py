# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Redirect.wildcard_match'
        db.add_column(u'painless_redirects_redirect', 'wildcard_match',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)


        # Changing field 'Redirect.domain'
        db.alter_column(u'painless_redirects_redirect', 'domain', self.gf('django.db.models.fields.CharField')(max_length=64))

        # Changing field 'Redirect.new_path'
        db.alter_column(u'painless_redirects_redirect', 'new_path', self.gf('django.db.models.fields.CharField')(max_length=333))

        # Changing field 'Redirect.old_path'
        db.alter_column(u'painless_redirects_redirect', 'old_path', self.gf('django.db.models.fields.CharField')(max_length=333))
        # Adding index on 'Redirect', fields ['old_path']
        db.create_index(u'painless_redirects_redirect', ['old_path'])


    def backwards(self, orm):
        # Removing index on 'Redirect', fields ['old_path']
        db.delete_index(u'painless_redirects_redirect', ['old_path'])

        # Deleting field 'Redirect.wildcard_match'
        db.delete_column(u'painless_redirects_redirect', 'wildcard_match')


        # Changing field 'Redirect.domain'
        db.alter_column(u'painless_redirects_redirect', 'domain', self.gf('django.db.models.fields.CharField')(max_length=1024))

        # Changing field 'Redirect.new_path'
        db.alter_column(u'painless_redirects_redirect', 'new_path', self.gf('django.db.models.fields.CharField')(max_length=1024))

        # Changing field 'Redirect.old_path'
        db.alter_column(u'painless_redirects_redirect', 'old_path', self.gf('django.db.models.fields.CharField')(max_length=1024))

    models = {
        u'painless_redirects.redirect': {
            'Meta': {'object_name': 'Redirect'},
            'domain': ('django.db.models.fields.CharField', [], {'max_length': '64', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'new_path': ('django.db.models.fields.CharField', [], {'max_length': '512'}),
            'new_site': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'redirect_new_site'", 'null': 'True', 'to': u"orm['sites.Site']"}),
            'old_path': ('django.db.models.fields.CharField', [], {'max_length': '512', 'db_index': 'True'}),
            'site': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'redirect_old_site'", 'null': 'True', 'to': u"orm['sites.Site']"}),
            'wildcard_match': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        u'sites.site': {
            'Meta': {'ordering': "(u'domain',)", 'object_name': 'Site', 'db_table': "u'django_site'"},
            'domain': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        }
    }

    complete_apps = ['painless_redirects']