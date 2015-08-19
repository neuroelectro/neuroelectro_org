# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Protein'
        db.create_table('neuroelectro_protein', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('gene', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=300)),
            ('allenid', self.gf('django.db.models.fields.IntegerField')()),
            ('entrezid', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('neuroelectro', ['Protein'])

        # Adding M2M table for field synonyms on 'Protein'
        db.create_table('neuroelectro_protein_synonyms', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('protein', models.ForeignKey(orm['neuroelectro.protein'], null=False)),
            ('proteinsyn', models.ForeignKey(orm['neuroelectro.proteinsyn'], null=False))
        ))
        db.create_unique('neuroelectro_protein_synonyms', ['protein_id', 'proteinsyn_id'])

        # Adding M2M table for field in_situ_expts on 'Protein'
        db.create_table('neuroelectro_protein_in_situ_expts', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('protein', models.ForeignKey(orm['neuroelectro.protein'], null=False)),
            ('insituexpt', models.ForeignKey(orm['neuroelectro.insituexpt'], null=False))
        ))
        db.create_unique('neuroelectro_protein_in_situ_expts', ['protein_id', 'insituexpt_id'])

        # Adding model 'InSituExpt'
        db.create_table('neuroelectro_insituexpt', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('imageseriesid', self.gf('django.db.models.fields.IntegerField')()),
            ('plane', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('valid', self.gf('django.db.models.fields.BooleanField')(default=True)),
        ))
        db.send_create_signal('neuroelectro', ['InSituExpt'])

        # Adding M2M table for field regionexprs on 'InSituExpt'
        db.create_table('neuroelectro_insituexpt_regionexprs', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('insituexpt', models.ForeignKey(orm['neuroelectro.insituexpt'], null=False)),
            ('regionexpr', models.ForeignKey(orm['neuroelectro.regionexpr'], null=False))
        ))
        db.create_unique('neuroelectro_insituexpt_regionexprs', ['insituexpt_id', 'regionexpr_id'])

        # Adding model 'BrainRegion'
        db.create_table('neuroelectro_brainregion', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=500)),
            ('abbrev', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('isallen', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('allenid', self.gf('django.db.models.fields.IntegerField')(default=0, null=True)),
            ('treedepth', self.gf('django.db.models.fields.IntegerField')(null=True)),
            ('color', self.gf('django.db.models.fields.CharField')(max_length=10, null=True)),
        ))
        db.send_create_signal('neuroelectro', ['BrainRegion'])

        # Adding model 'RegionExpr'
        db.create_table('neuroelectro_regionexpr', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('val', self.gf('django.db.models.fields.FloatField')()),
        ))
        db.send_create_signal('neuroelectro', ['RegionExpr'])

        # Adding model 'Neuron'
        db.create_table('neuroelectro_neuron', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=500)),
            ('nlex_id', self.gf('django.db.models.fields.CharField')(max_length=100, null=True)),
        ))
        db.send_create_signal('neuroelectro', ['Neuron'])

        # Adding M2M table for field synonyms on 'Neuron'
        db.create_table('neuroelectro_neuron_synonyms', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('neuron', models.ForeignKey(orm['neuroelectro.neuron'], null=False)),
            ('neuronsyn', models.ForeignKey(orm['neuroelectro.neuronsyn'], null=False))
        ))
        db.create_unique('neuroelectro_neuron_synonyms', ['neuron_id', 'neuronsyn_id'])

        # Adding M2M table for field regions on 'Neuron'
        db.create_table('neuroelectro_neuron_regions', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('neuron', models.ForeignKey(orm['neuroelectro.neuron'], null=False)),
            ('brainregion', models.ForeignKey(orm['neuroelectro.brainregion'], null=False))
        ))
        db.create_unique('neuroelectro_neuron_regions', ['neuron_id', 'brainregion_id'])

        # Adding model 'NeuronSyn'
        db.create_table('neuroelectro_neuronsyn', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('term', self.gf('django.db.models.fields.CharField')(max_length=500)),
        ))
        db.send_create_signal('neuroelectro', ['NeuronSyn'])

        # Adding model 'ProteinSyn'
        db.create_table('neuroelectro_proteinsyn', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('term', self.gf('django.db.models.fields.CharField')(max_length=500)),
        ))
        db.send_create_signal('neuroelectro', ['ProteinSyn'])


    def backwards(self, orm):
        
        # Deleting model 'Protein'
        db.delete_table('neuroelectro_protein')

        # Removing M2M table for field synonyms on 'Protein'
        db.delete_table('neuroelectro_protein_synonyms')

        # Removing M2M table for field in_situ_expts on 'Protein'
        db.delete_table('neuroelectro_protein_in_situ_expts')

        # Deleting model 'InSituExpt'
        db.delete_table('neuroelectro_insituexpt')

        # Removing M2M table for field regionexprs on 'InSituExpt'
        db.delete_table('neuroelectro_insituexpt_regionexprs')

        # Deleting model 'BrainRegion'
        db.delete_table('neuroelectro_brainregion')

        # Deleting model 'RegionExpr'
        db.delete_table('neuroelectro_regionexpr')

        # Deleting model 'Neuron'
        db.delete_table('neuroelectro_neuron')

        # Removing M2M table for field synonyms on 'Neuron'
        db.delete_table('neuroelectro_neuron_synonyms')

        # Removing M2M table for field regions on 'Neuron'
        db.delete_table('neuroelectro_neuron_regions')

        # Deleting model 'NeuronSyn'
        db.delete_table('neuroelectro_neuronsyn')

        # Deleting model 'ProteinSyn'
        db.delete_table('neuroelectro_proteinsyn')


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
