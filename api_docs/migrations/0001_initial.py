# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Topic'
        db.create_table(u'api_docs_topic', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('slug', self.gf('django.db.models.fields.CharField')(max_length=64)),
        ))
        db.send_create_signal(u'api_docs', ['Topic'])

        # Adding model 'Language'
        db.create_table(u'api_docs_language', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('topic', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['api_docs.Topic'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('slug', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('current_version', self.gf('django.db.models.fields.related.ForeignKey')(related_name='current_for_lang', null=True, to=orm['api_docs.Version'])),
            ('development_version', self.gf('django.db.models.fields.related.ForeignKey')(related_name='development_for_lang', null=True, to=orm['api_docs.Version'])),
        ))
        db.send_create_signal(u'api_docs', ['Language'])

        # Adding model 'Version'
        db.create_table(u'api_docs_version', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('language', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['api_docs.Language'], null=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('slug', self.gf('django.db.models.fields.CharField')(max_length=64)),
        ))
        db.send_create_signal(u'api_docs', ['Version'])

        # Adding model 'Section'
        db.create_table(u'api_docs_section', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('topic_version', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['api_docs.Version'])),
        ))
        db.send_create_signal(u'api_docs', ['Section'])

        # Adding model 'Namespace'
        db.create_table(u'api_docs_namespace', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('platform_section', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['api_docs.Section'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('display_name', self.gf('django.db.models.fields.CharField')(default='', max_length=64, blank=True)),
            ('data', self.gf('django.db.models.fields.TextField')(default='', blank=True)),
            ('source_file', self.gf('django.db.models.fields.CharField')(max_length=128, null=True, blank=True)),
            ('source_format', self.gf('django.db.models.fields.CharField')(max_length=32, null=True, blank=True)),
        ))
        db.send_create_signal(u'api_docs', ['Namespace'])

        # Adding model 'Element'
        db.create_table(u'api_docs_element', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('description', self.gf('django.db.models.fields.CharField')(default='', max_length=256, blank=True)),
            ('namespace', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['api_docs.Namespace'], null=True, blank=True)),
            ('section', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['api_docs.Section'])),
            ('fullname', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('keywords', self.gf('django.db.models.fields.CharField')(default='', max_length=256, blank=True)),
            ('data', self.gf('django.db.models.fields.TextField')(default='', blank=True)),
            ('source_file', self.gf('django.db.models.fields.CharField')(max_length=128, null=True, blank=True)),
            ('source_format', self.gf('django.db.models.fields.CharField')(max_length=32, null=True, blank=True)),
        ))
        db.send_create_signal(u'api_docs', ['Element'])

        # Adding model 'Page'
        db.create_table(u'api_docs_page', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('slug', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('description', self.gf('django.db.models.fields.CharField')(default='', max_length=256, blank=True)),
            ('namespace', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['api_docs.Namespace'], null=True, blank=True)),
            ('section', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['api_docs.Section'])),
            ('fullname', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('keywords', self.gf('django.db.models.fields.CharField')(default='', max_length=256, blank=True)),
            ('data', self.gf('django.db.models.fields.TextField')(default='', blank=True)),
            ('source_file', self.gf('django.db.models.fields.CharField')(max_length=128, null=True, blank=True)),
            ('source_format', self.gf('django.db.models.fields.CharField')(max_length=32, null=True, blank=True)),
            ('order_index', self.gf('django.db.models.fields.PositiveIntegerField')(default=0, blank=True)),
        ))
        db.send_create_signal(u'api_docs', ['Page'])


    def backwards(self, orm):
        # Deleting model 'Topic'
        db.delete_table(u'api_docs_topic')

        # Deleting model 'Language'
        db.delete_table(u'api_docs_language')

        # Deleting model 'Version'
        db.delete_table(u'api_docs_version')

        # Deleting model 'Section'
        db.delete_table(u'api_docs_section')

        # Deleting model 'Namespace'
        db.delete_table(u'api_docs_namespace')

        # Deleting model 'Element'
        db.delete_table(u'api_docs_element')

        # Deleting model 'Page'
        db.delete_table(u'api_docs_page')


    models = {
        u'api_docs.element': {
            'Meta': {'ordering': "('name',)", 'object_name': 'Element'},
            'data': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '256', 'blank': 'True'}),
            'fullname': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'keywords': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '256', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'namespace': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['api_docs.Namespace']", 'null': 'True', 'blank': 'True'}),
            'section': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['api_docs.Section']"}),
            'source_file': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'source_format': ('django.db.models.fields.CharField', [], {'max_length': '32', 'null': 'True', 'blank': 'True'})
        },
        u'api_docs.language': {
            'Meta': {'object_name': 'Language'},
            'current_version': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'current_for_lang'", 'null': 'True', 'to': u"orm['api_docs.Version']"}),
            'development_version': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'development_for_lang'", 'null': 'True', 'to': u"orm['api_docs.Version']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'slug': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'topic': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['api_docs.Topic']"})
        },
        u'api_docs.namespace': {
            'Meta': {'ordering': "('name',)", 'object_name': 'Namespace'},
            'data': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'display_name': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '64', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'platform_section': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['api_docs.Section']"}),
            'source_file': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'source_format': ('django.db.models.fields.CharField', [], {'max_length': '32', 'null': 'True', 'blank': 'True'})
        },
        u'api_docs.page': {
            'Meta': {'ordering': "('order_index',)", 'object_name': 'Page'},
            'data': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '256', 'blank': 'True'}),
            'fullname': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'keywords': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '256', 'blank': 'True'}),
            'namespace': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['api_docs.Namespace']", 'null': 'True', 'blank': 'True'}),
            'order_index': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0', 'blank': 'True'}),
            'section': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['api_docs.Section']"}),
            'slug': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'source_file': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'source_format': ('django.db.models.fields.CharField', [], {'max_length': '32', 'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '64'})
        },
        u'api_docs.section': {
            'Meta': {'object_name': 'Section'},
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'topic_version': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['api_docs.Version']"})
        },
        u'api_docs.topic': {
            'Meta': {'object_name': 'Topic'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'slug': ('django.db.models.fields.CharField', [], {'max_length': '64'})
        },
        u'api_docs.version': {
            'Meta': {'object_name': 'Version'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['api_docs.Language']", 'null': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'slug': ('django.db.models.fields.CharField', [], {'max_length': '64'})
        }
    }

    complete_apps = ['api_docs']