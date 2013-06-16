# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'Node.firstname'
        db.alter_column('neurotree_node', 'firstname', self.gf('django.db.models.fields.CharField')(max_length=50))

        # Changing field 'Node.middlename'
        db.alter_column('neurotree_node', 'middlename', self.gf('django.db.models.fields.CharField')(max_length=50))

        # Changing field 'Node.lastname'
        db.alter_column('neurotree_node', 'lastname', self.gf('django.db.models.fields.CharField')(max_length=50))

        # Changing field 'Node.location'
        db.alter_column('neurotree_node', 'location', self.gf('django.db.models.fields.CharField')(max_length=200))

    def backwards(self, orm):

        # Changing field 'Node.firstname'
        db.alter_column('neurotree_node', 'firstname', self.gf('django.db.models.fields.CharField')(max_length=25))

        # Changing field 'Node.middlename'
        db.alter_column('neurotree_node', 'middlename', self.gf('django.db.models.fields.CharField')(max_length=25))

        # Changing field 'Node.lastname'
        db.alter_column('neurotree_node', 'lastname', self.gf('django.db.models.fields.CharField')(max_length=25))

        # Changing field 'Node.location'
        db.alter_column('neurotree_node', 'location', self.gf('django.db.models.fields.CharField')(max_length=100))

    models = {
        'neurotree.edge': {
            'Meta': {'object_name': 'Edge'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'node1': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'children'", 'to': "orm['neurotree.Node']"}),
            'node2': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'parents'", 'to': "orm['neurotree.Node']"}),
            'relationcode': ('django.db.models.fields.IntegerField', [], {}),
            'relationstring': ('django.db.models.fields.CharField', [], {'max_length': '25'}),
            'stopyear': ('django.db.models.fields.IntegerField', [], {})
        },
        'neurotree.node': {
            'Meta': {'object_name': 'Node'},
            'altpubmed': ('django.db.models.fields.URLField', [], {'max_length': '200'}),
            'firstname': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lastname': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'location': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'middlename': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'nodes': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['neurotree.Node']", 'through': "orm['neurotree.Edge']", 'symmetrical': 'False'}),
            'tree': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['neurotree.Tree']", 'symmetrical': 'False'})
        },
        'neurotree.tree': {
            'Meta': {'object_name': 'Tree'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '15'})
        }
    }

    complete_apps = ['neurotree']