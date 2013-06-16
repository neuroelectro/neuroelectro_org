# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Tree'
        db.create_table('neurotree_tree', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=15)),
        ))
        db.send_create_signal('neurotree', ['Tree'])

        # Adding model 'Node'
        db.create_table('neurotree_node', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('firstname', self.gf('django.db.models.fields.CharField')(max_length=25)),
            ('middlename', self.gf('django.db.models.fields.CharField')(max_length=25)),
            ('lastname', self.gf('django.db.models.fields.CharField')(max_length=25)),
            ('location', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('altpubmed', self.gf('django.db.models.fields.URLField')(max_length=200)),
        ))
        db.send_create_signal('neurotree', ['Node'])

        # Adding M2M table for field tree on 'Node'
        db.create_table('neurotree_node_tree', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('node', models.ForeignKey(orm['neurotree.node'], null=False)),
            ('tree', models.ForeignKey(orm['neurotree.tree'], null=False))
        ))
        db.create_unique('neurotree_node_tree', ['node_id', 'tree_id'])

        # Adding model 'Edge'
        db.create_table('neurotree_edge', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('node1', self.gf('django.db.models.fields.related.ForeignKey')(related_name='node1', to=orm['neurotree.Node'])),
            ('node2', self.gf('django.db.models.fields.related.ForeignKey')(related_name='node2', to=orm['neurotree.Node'])),
            ('relationcode', self.gf('django.db.models.fields.IntegerField')()),
            ('relationstring', self.gf('django.db.models.fields.CharField')(max_length=25)),
            ('stopyear', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('neurotree', ['Edge'])


    def backwards(self, orm):
        # Deleting model 'Tree'
        db.delete_table('neurotree_tree')

        # Deleting model 'Node'
        db.delete_table('neurotree_node')

        # Removing M2M table for field tree on 'Node'
        db.delete_table('neurotree_node_tree')

        # Deleting model 'Edge'
        db.delete_table('neurotree_edge')


    models = {
        'neurotree.edge': {
            'Meta': {'object_name': 'Edge'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'node1': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'node1'", 'to': "orm['neurotree.Node']"}),
            'node2': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'node2'", 'to': "orm['neurotree.Node']"}),
            'relationcode': ('django.db.models.fields.IntegerField', [], {}),
            'relationstring': ('django.db.models.fields.CharField', [], {'max_length': '25'}),
            'stopyear': ('django.db.models.fields.IntegerField', [], {})
        },
        'neurotree.node': {
            'Meta': {'object_name': 'Node'},
            'altpubmed': ('django.db.models.fields.URLField', [], {'max_length': '200'}),
            'firstname': ('django.db.models.fields.CharField', [], {'max_length': '25'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lastname': ('django.db.models.fields.CharField', [], {'max_length': '25'}),
            'location': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'middlename': ('django.db.models.fields.CharField', [], {'max_length': '25'}),
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