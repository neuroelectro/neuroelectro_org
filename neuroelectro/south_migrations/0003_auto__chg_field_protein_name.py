# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Changing field 'Protein.name'
        db.alter_column('neuroelectro_protein', 'name', self.gf('django.db.models.fields.CharField')(max_length=300))


    def backwards(self, orm):
        
        # Changing field 'Protein.name'
        db.alter_column('neuroelectro_protein', 'name', self.gf('django.db.models.fields.CharField')(max_length=400))


    models = {
        'neuroelectro.brainregion': {
            'Meta': {'object_name': 'BrainRegion'},
            'abbrev': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'allenid': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True'}),
            'color': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'isallen': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '500'}),
            'treedepth': ('django.db.models.fields.IntegerField', [], {'null': 'True'})
        },
        'neuroelectro.insituexpt': {
            'Meta': {'object_name': 'InSituExpt'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'imageseriesid': ('django.db.models.fields.IntegerField', [], {}),
            'plane': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'regionexprs': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['neuroelectro.RegionExpr']", 'null': 'True', 'symmetrical': 'False'}),
            'valid': ('django.db.models.fields.BooleanField', [], {'default': 'True'})
        },
        'neuroelectro.neuron': {
            'Meta': {'object_name': 'Neuron'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '500'}),
            'nlex_id': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True'}),
            'regions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['neuroelectro.BrainRegion']", 'null': 'True', 'symmetrical': 'False'}),
            'synonyms': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['neuroelectro.NeuronSyn']", 'null': 'True', 'symmetrical': 'False'})
        },
        'neuroelectro.neuronsyn': {
            'Meta': {'object_name': 'NeuronSyn'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'term': ('django.db.models.fields.CharField', [], {'max_length': '500'})
        },
        'neuroelectro.protein': {
            'Meta': {'object_name': 'Protein'},
            'allenid': ('django.db.models.fields.IntegerField', [], {}),
            'entrezid': ('django.db.models.fields.IntegerField', [], {}),
            'gene': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'in_situ_expts': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['neuroelectro.InSituExpt']", 'null': 'True', 'symmetrical': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '300'}),
            'synonyms': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['neuroelectro.ProteinSyn']", 'null': 'True', 'symmetrical': 'False'})
        },
        'neuroelectro.proteinsyn': {
            'Meta': {'object_name': 'ProteinSyn'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'term': ('django.db.models.fields.CharField', [], {'max_length': '500'})
        },
        'neuroelectro.regionexpr': {
            'Meta': {'object_name': 'RegionExpr'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'val': ('django.db.models.fields.FloatField', [], {})
        }
    }

    complete_apps = ['neuroelectro']
