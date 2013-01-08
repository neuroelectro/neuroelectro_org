# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'NeuronEphysDataMap'
        db.create_table('neuroelectro_neuronephysdatamap', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('neuron_concept_map', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['neuroelectro.NeuronConceptMap'])),
            ('ephys_concept_map', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['neuroelectro.EphysConceptMap'])),
            ('val', self.gf('django.db.models.fields.FloatField')()),
            ('err', self.gf('django.db.models.fields.FloatField')(null=True)),
            ('n', self.gf('django.db.models.fields.IntegerField')(null=True)),
            ('ref_text', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('data_table', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['neuroelectro.DataTable'], null=True)),
            ('dt_id', self.gf('django.db.models.fields.CharField')(max_length=20, null=True)),
            ('date_mod', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('added_by', self.gf('django.db.models.fields.CharField')(default='robot', max_length=20)),
            ('times_validated', self.gf('django.db.models.fields.IntegerField')(default=0)),
        ))
        db.send_create_signal('neuroelectro', ['NeuronEphysDataMap'])


    def backwards(self, orm):
        
        # Deleting model 'NeuronEphysDataMap'
        db.delete_table('neuroelectro_neuronephysdatamap')


    models = {
        'neuroelectro.article': {
            'Meta': {'object_name': 'Article'},
            'abstract': ('django.db.models.fields.CharField', [], {'max_length': '10000', 'null': 'True'}),
            'full_text_link': ('django.db.models.fields.CharField', [], {'max_length': '1000', 'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'journal': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['neuroelectro.Journal']", 'null': 'True'}),
            'pmid': ('django.db.models.fields.IntegerField', [], {}),
            'substances': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['neuroelectro.Substance']", 'null': 'True', 'symmetrical': 'False'}),
            'terms': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['neuroelectro.MeshTerm']", 'null': 'True', 'symmetrical': 'False'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '500'})
        },
        'neuroelectro.articlefulltext': {
            'Meta': {'object_name': 'ArticleFullText'},
            'article': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['neuroelectro.Article']"}),
            'full_text': ('picklefield.fields.PickledObjectField', [], {'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
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
        'neuroelectro.datatable': {
            'Meta': {'object_name': 'DataTable'},
            'article': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['neuroelectro.Article']"}),
            'ephys_props': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['neuroelectro.EphysProp']", 'null': 'True', 'through': "orm['neuroelectro.EphysConceptMap']", 'symmetrical': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'link': ('django.db.models.fields.CharField', [], {'max_length': '1000'}),
            'neurons': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['neuroelectro.Neuron']", 'null': 'True', 'symmetrical': 'False'}),
            'table_html': ('picklefield.fields.PickledObjectField', [], {'null': 'True'}),
            'table_text': ('django.db.models.fields.CharField', [], {'max_length': '10000', 'null': 'True'})
        },
        'neuroelectro.datatabletag': {
            'Meta': {'object_name': 'DataTableTag'},
            'ephys_prop': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['neuroelectro.EphysProp']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'neuron': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['neuroelectro.Neuron']"})
        },
        'neuroelectro.ephysconceptmap': {
            'Meta': {'object_name': 'EphysConceptMap'},
            'added_by': ('django.db.models.fields.CharField', [], {'default': "'robot'", 'max_length': '20'}),
            'data_table': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['neuroelectro.DataTable']", 'null': 'True'}),
            'date_mod': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'dt_id': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True'}),
            'ephys_prop': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['neuroelectro.EphysProp']"}),
            'ephys_prop_syn': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['neuroelectro.EphysPropSyn']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'match_quality': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'ref_text': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'times_validated': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        'neuroelectro.ephysprop': {
            'Meta': {'object_name': 'EphysProp'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'unit': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True'})
        },
        'neuroelectro.ephyspropsyn': {
            'Meta': {'object_name': 'EphysPropSyn'},
            'ephys_prop': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['neuroelectro.EphysProp']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'term': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        'neuroelectro.insituexpt': {
            'Meta': {'object_name': 'InSituExpt'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'imageseriesid': ('django.db.models.fields.IntegerField', [], {}),
            'plane': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'regionexprs': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['neuroelectro.RegionExpr']", 'null': 'True', 'symmetrical': 'False'}),
            'valid': ('django.db.models.fields.BooleanField', [], {'default': 'True'})
        },
        'neuroelectro.journal': {
            'Meta': {'object_name': 'Journal'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '300'})
        },
        'neuroelectro.meshterm': {
            'Meta': {'object_name': 'MeshTerm'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'term': ('django.db.models.fields.CharField', [], {'max_length': '300'})
        },
        'neuroelectro.neuron': {
            'Meta': {'object_name': 'Neuron'},
            'added_by': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True'}),
            'date_mod': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
            'defining_articles': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['neuroelectro.Article']", 'null': 'True', 'symmetrical': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '500'}),
            'nlex_id': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True'}),
            'regions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['neuroelectro.BrainRegion']", 'null': 'True', 'symmetrical': 'False'}),
            'synonyms': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['neuroelectro.NeuronSyn']", 'null': 'True', 'symmetrical': 'False'})
        },
        'neuroelectro.neuronarticlemap': {
            'Meta': {'object_name': 'NeuronArticleMap'},
            'added_by': ('django.db.models.fields.CharField', [], {'default': "'robot'", 'max_length': '20'}),
            'article': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['neuroelectro.Article']", 'null': 'True'}),
            'date_mod': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'neuron': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['neuroelectro.Neuron']"}),
            'neuron_syn': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['neuroelectro.NeuronSyn']", 'null': 'True'}),
            'num_mentions': ('django.db.models.fields.IntegerField', [], {'null': 'True'})
        },
        'neuroelectro.neuronconceptmap': {
            'Meta': {'object_name': 'NeuronConceptMap'},
            'added_by': ('django.db.models.fields.CharField', [], {'default': "'robot'", 'max_length': '20'}),
            'data_table': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['neuroelectro.DataTable']", 'null': 'True'}),
            'date_mod': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'dt_id': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'match_quality': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'neuron': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['neuroelectro.Neuron']"}),
            'neuron_syn': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['neuroelectro.NeuronSyn']", 'null': 'True'}),
            'ref_text': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'times_validated': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        'neuroelectro.neuronephysdatamap': {
            'Meta': {'object_name': 'NeuronEphysDataMap'},
            'added_by': ('django.db.models.fields.CharField', [], {'default': "'robot'", 'max_length': '20'}),
            'data_table': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['neuroelectro.DataTable']", 'null': 'True'}),
            'date_mod': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'dt_id': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True'}),
            'ephys_concept_map': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['neuroelectro.EphysConceptMap']"}),
            'err': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'n': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'neuron_concept_map': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['neuroelectro.NeuronConceptMap']"}),
            'ref_text': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'times_validated': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'val': ('django.db.models.fields.FloatField', [], {})
        },
        'neuroelectro.neuronephyslink': {
            'Meta': {'object_name': 'NeuronEphysLink'},
            'data_table': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['neuroelectro.DataTable']"}),
            'ephys_prop': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['neuroelectro.EphysProp']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'neuron': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['neuroelectro.Neuron']"}),
            'num_reps': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'val': ('django.db.models.fields.FloatField', [], {}),
            'val_err': ('django.db.models.fields.FloatField', [], {'null': 'True'})
        },
        'neuroelectro.neuronsyn': {
            'Meta': {'object_name': 'NeuronSyn'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'term': ('django.db.models.fields.CharField', [], {'max_length': '500'})
        },
        'neuroelectro.protein': {
            'Meta': {'object_name': 'Protein'},
            'allenid': ('django.db.models.fields.IntegerField', [], {}),
            'common_name': ('django.db.models.fields.CharField', [], {'max_length': '400', 'null': 'True'}),
            'entrezid': ('django.db.models.fields.IntegerField', [], {}),
            'gene': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'in_situ_expts': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['neuroelectro.InSituExpt']", 'null': 'True', 'symmetrical': 'False'}),
            'is_channel': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '400'}),
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
            'region': ('django.db.models.fields.related.ForeignKey', [], {'default': '0', 'to': "orm['neuroelectro.BrainRegion']"}),
            'val': ('django.db.models.fields.FloatField', [], {})
        },
        'neuroelectro.species': {
            'Meta': {'object_name': 'Species'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'specie': ('django.db.models.fields.CharField', [], {'max_length': '500'})
        },
        'neuroelectro.substance': {
            'Meta': {'object_name': 'Substance'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'term': ('django.db.models.fields.CharField', [], {'max_length': '300'})
        },
        'neuroelectro.superprotein': {
            'Meta': {'object_name': 'SuperProtein'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_channel': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '400'}),
            'synonyms': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['neuroelectro.ProteinSyn']", 'null': 'True', 'symmetrical': 'False'})
        },
        'neuroelectro.unit': {
            'Meta': {'object_name': 'Unit'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '20'})
        }
    }

    complete_apps = ['neuroelectro']
