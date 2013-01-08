# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Journal'
        db.create_table('neuroelectro_journal', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=300)),
        ))
        db.send_create_signal('neuroelectro', ['Journal'])

        # Adding model 'Substance'
        db.create_table('neuroelectro_substance', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('term', self.gf('django.db.models.fields.CharField')(max_length=300)),
        ))
        db.send_create_signal('neuroelectro', ['Substance'])

        # Adding model 'Article'
        db.create_table('neuroelectro_article', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=500)),
            ('abstract', self.gf('django.db.models.fields.CharField')(max_length=10000, null=True)),
            ('pmid', self.gf('django.db.models.fields.IntegerField')()),
            ('journal', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['neuroelectro.Journal'], null=True)),
            ('full_text_link', self.gf('django.db.models.fields.CharField')(max_length=1000, null=True)),
        ))
        db.send_create_signal('neuroelectro', ['Article'])

        # Adding M2M table for field terms on 'Article'
        db.create_table('neuroelectro_article_terms', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('article', models.ForeignKey(orm['neuroelectro.article'], null=False)),
            ('meshterm', models.ForeignKey(orm['neuroelectro.meshterm'], null=False))
        ))
        db.create_unique('neuroelectro_article_terms', ['article_id', 'meshterm_id'])

        # Adding M2M table for field substances on 'Article'
        db.create_table('neuroelectro_article_substances', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('article', models.ForeignKey(orm['neuroelectro.article'], null=False)),
            ('substance', models.ForeignKey(orm['neuroelectro.substance'], null=False))
        ))
        db.create_unique('neuroelectro_article_substances', ['article_id', 'substance_id'])

        # Adding model 'MeshTerm'
        db.create_table('neuroelectro_meshterm', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('term', self.gf('django.db.models.fields.CharField')(max_length=300)),
        ))
        db.send_create_signal('neuroelectro', ['MeshTerm'])

        # Adding model 'DataTable'
        db.create_table('neuroelectro_datatable', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('link', self.gf('django.db.models.fields.CharField')(max_length=1000)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=1000, null=True)),
            ('table', self.gf('django.db.models.fields.CharField')(max_length=10000)),
            ('table_headers', self.gf('django.db.models.fields.CharField')(max_length=200, null=True)),
            ('article', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['neuroelectro.Article'])),
        ))
        db.send_create_signal('neuroelectro', ['DataTable'])

        # Adding model 'Species'
        db.create_table('neuroelectro_species', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('specie', self.gf('django.db.models.fields.CharField')(max_length=500)),
        ))
        db.send_create_signal('neuroelectro', ['Species'])


    def backwards(self, orm):
        
        # Deleting model 'Journal'
        db.delete_table('neuroelectro_journal')

        # Deleting model 'Substance'
        db.delete_table('neuroelectro_substance')

        # Deleting model 'Article'
        db.delete_table('neuroelectro_article')

        # Removing M2M table for field terms on 'Article'
        db.delete_table('neuroelectro_article_terms')

        # Removing M2M table for field substances on 'Article'
        db.delete_table('neuroelectro_article_substances')

        # Deleting model 'MeshTerm'
        db.delete_table('neuroelectro_meshterm')

        # Deleting model 'DataTable'
        db.delete_table('neuroelectro_datatable')

        # Deleting model 'Species'
        db.delete_table('neuroelectro_species')


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
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'link': ('django.db.models.fields.CharField', [], {'max_length': '1000'}),
            'table': ('django.db.models.fields.CharField', [], {'max_length': '10000'}),
            'table_headers': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '1000', 'null': 'True'})
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
        }
    }

    complete_apps = ['neuroelectro']
