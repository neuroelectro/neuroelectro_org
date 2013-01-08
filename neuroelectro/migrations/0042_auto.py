# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding M2M table for field added_by on 'NeuronArticleMap'
        db.create_table('neuroelectro_neuronarticlemap_added_by', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('neuronarticlemap', models.ForeignKey(orm['neuroelectro.neuronarticlemap'], null=False)),
            ('user', models.ForeignKey(orm['neuroelectro.user'], null=False))
        ))
        db.create_unique('neuroelectro_neuronarticlemap_added_by', ['neuronarticlemap_id', 'user_id'])


    def backwards(self, orm):
        # Removing M2M table for field added_by on 'NeuronArticleMap'
        db.delete_table('neuroelectro_neuronarticlemap_added_by')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'neuroelectro.article': {
            'Meta': {'object_name': 'Article'},
            'abstract': ('django.db.models.fields.CharField', [], {'max_length': '10000', 'null': 'True'}),
            'authors': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['neuroelectro.Author']", 'null': 'True', 'symmetrical': 'False'}),
            'full_text_link': ('django.db.models.fields.CharField', [], {'max_length': '1000', 'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'journal': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['neuroelectro.Journal']", 'null': 'True'}),
            'metadata': ('django.db.models.fields.related.ManyToManyField', [], {'default': 'None', 'to': "orm['neuroelectro.MetaData']", 'null': 'True', 'symmetrical': 'False'}),
            'pmid': ('django.db.models.fields.IntegerField', [], {}),
            'pub_year': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'substances': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['neuroelectro.Substance']", 'null': 'True', 'symmetrical': 'False'}),
            'suggester': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': "orm['neuroelectro.User']", 'null': 'True'}),
            'terms': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['neuroelectro.MeshTerm']", 'null': 'True', 'symmetrical': 'False'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '500'})
        },
        'neuroelectro.articlefulltext': {
            'Meta': {'object_name': 'ArticleFullText'},
            'article': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['neuroelectro.Article']"}),
            'full_text': ('picklefield.fields.PickledObjectField', [], {'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'neuroelectro.articlesummary': {
            'Meta': {'object_name': 'ArticleSummary'},
            'article': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['neuroelectro.Article']"}),
            'author_list_str': ('django.db.models.fields.CharField', [], {'max_length': '500', 'null': 'True'}),
            'data': ('django.db.models.fields.TextField', [], {'default': "''"}),
            'date_mod': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'num_nedms': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'num_neurons': ('django.db.models.fields.IntegerField', [], {'null': 'True'})
        },
        'neuroelectro.author': {
            'Meta': {'object_name': 'Author'},
            'first': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'initials': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True'}),
            'last': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True'}),
            'middle': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True'})
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
        'neuroelectro.datasource': {
            'Meta': {'object_name': 'DataSource'},
            'data_table': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['neuroelectro.DataTable']", 'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'user_submission': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['neuroelectro.UserSubmission']", 'null': 'True'}),
            'user_upload': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['neuroelectro.UserUpload']", 'null': 'True'})
        },
        'neuroelectro.datatable': {
            'Meta': {'object_name': 'DataTable'},
            'article': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['neuroelectro.Article']"}),
            'date_mod': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'link': ('django.db.models.fields.CharField', [], {'max_length': '1000'}),
            'needs_expert': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'table_html': ('picklefield.fields.PickledObjectField', [], {'null': 'True'}),
            'table_text': ('django.db.models.fields.CharField', [], {'max_length': '10000', 'null': 'True'})
        },
        'neuroelectro.ephysconceptmap': {
            'Meta': {'object_name': 'EphysConceptMap'},
            'added_by': ('django.db.models.fields.CharField', [], {'default': "'robot'", 'max_length': '20'}),
            'date_mod': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'dt_id': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True'}),
            'ephys_prop': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['neuroelectro.EphysProp']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'match_quality': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'ref_text': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'source': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['neuroelectro.DataSource']"}),
            'times_validated': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        'neuroelectro.ephysprop': {
            'Meta': {'object_name': 'EphysProp'},
            'definition': ('django.db.models.fields.CharField', [], {'max_length': '1000', 'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'synonyms': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['neuroelectro.EphysPropSyn']", 'symmetrical': 'False'}),
            'units': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['neuroelectro.Unit']", 'null': 'True'})
        },
        'neuroelectro.ephyspropsummary': {
            'Meta': {'object_name': 'EphysPropSummary'},
            'data': ('django.db.models.fields.TextField', [], {'default': "''"}),
            'date_mod': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'ephys_prop': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['neuroelectro.EphysProp']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'num_articles': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'num_nedms': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'num_neurons': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'value_mean_articles': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'value_mean_neurons': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'value_sd_articles': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'value_sd_neurons': ('django.db.models.fields.FloatField', [], {'null': 'True'})
        },
        'neuroelectro.ephyspropsyn': {
            'Meta': {'object_name': 'EphysPropSyn'},
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
        'neuroelectro.institution': {
            'Meta': {'object_name': 'Institution'},
            'country': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'state': ('django.db.models.fields.CharField', [], {'max_length': '2', 'null': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True'})
        },
        'neuroelectro.journal': {
            'Meta': {'object_name': 'Journal'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'short_title': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '300'})
        },
        'neuroelectro.meshterm': {
            'Meta': {'object_name': 'MeshTerm'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'term': ('django.db.models.fields.CharField', [], {'max_length': '300'})
        },
        'neuroelectro.metadata': {
            'Meta': {'object_name': 'MetaData'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'neuroelectro.neuron': {
            'Meta': {'object_name': 'Neuron'},
            'added_by': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True'}),
            'date_mod': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '500'}),
            'nlex_id': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True'}),
            'regions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['neuroelectro.BrainRegion']", 'null': 'True', 'symmetrical': 'False'}),
            'synonyms': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['neuroelectro.NeuronSyn']", 'null': 'True', 'symmetrical': 'False'})
        },
        'neuroelectro.neuronarticlemap': {
            'Meta': {'object_name': 'NeuronArticleMap'},
            'added_by': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['neuroelectro.User']", 'null': 'True', 'symmetrical': 'False'}),
            'article': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['neuroelectro.Article']", 'null': 'True'}),
            'date_mod': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'neuron': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['neuroelectro.Neuron']"}),
            'num_mentions': ('django.db.models.fields.IntegerField', [], {'null': 'True'})
        },
        'neuroelectro.neuronconceptmap': {
            'Meta': {'object_name': 'NeuronConceptMap'},
            'added_by': ('django.db.models.fields.CharField', [], {'default': "'robot'", 'max_length': '20'}),
            'date_mod': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'dt_id': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'match_quality': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'neuron': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['neuroelectro.Neuron']"}),
            'ref_text': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'source': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['neuroelectro.DataSource']"}),
            'times_validated': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        'neuroelectro.neuronephysdatamap': {
            'Meta': {'object_name': 'NeuronEphysDataMap'},
            'added_by': ('django.db.models.fields.CharField', [], {'default': "'robot'", 'max_length': '20'}),
            'date_mod': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'dt_id': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True'}),
            'ephys_concept_map': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['neuroelectro.EphysConceptMap']"}),
            'err': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'match_quality': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'metadata': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['neuroelectro.MetaData']", 'symmetrical': 'False'}),
            'n': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'neuron_concept_map': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['neuroelectro.NeuronConceptMap']"}),
            'ref_text': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'source': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['neuroelectro.DataSource']"}),
            'times_validated': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'val': ('django.db.models.fields.FloatField', [], {}),
            'val_norm': ('django.db.models.fields.FloatField', [], {'null': 'True'})
        },
        'neuroelectro.neuronephyssummary': {
            'Meta': {'object_name': 'NeuronEphysSummary'},
            'data': ('django.db.models.fields.TextField', [], {'default': "''"}),
            'date_mod': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'ephys_prop': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['neuroelectro.EphysProp']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'neuron': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['neuroelectro.Neuron']"}),
            'num_articles': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'num_nedms': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'value_mean': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'value_sd': ('django.db.models.fields.FloatField', [], {'null': 'True'})
        },
        'neuroelectro.neuronsummary': {
            'Meta': {'object_name': 'NeuronSummary'},
            'cluster_xval': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'cluster_yval': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'data': ('django.db.models.fields.TextField', [], {'default': "''"}),
            'date_mod': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'neuron': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['neuroelectro.Neuron']"}),
            'num_articles': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'num_ephysprops': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'num_nedms': ('django.db.models.fields.IntegerField', [], {'null': 'True'})
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
            'name': ('django.db.models.fields.CharField', [], {'max_length': '500'})
        },
        'neuroelectro.substance': {
            'Meta': {'object_name': 'Substance'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'term': ('django.db.models.fields.CharField', [], {'max_length': '300'})
        },
        'neuroelectro.unit': {
            'Meta': {'object_name': 'Unit'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'prefix': ('django.db.models.fields.CharField', [], {'max_length': '1'})
        },
        'neuroelectro.user': {
            'Meta': {'object_name': 'User', '_ormbases': ['auth.User']},
            'assigned_neurons': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['neuroelectro.Neuron']", 'null': 'True', 'symmetrical': 'False'}),
            'institution': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['neuroelectro.Institution']", 'null': 'True'}),
            'is_curator': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'lab_head': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True'}),
            'lab_website_url': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True'}),
            'last_update': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
            'user_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['auth.User']", 'unique': 'True', 'primary_key': 'True'})
        },
        'neuroelectro.usersubmission': {
            'Meta': {'object_name': 'UserSubmission'},
            'data': ('picklefield.fields.PickledObjectField', [], {'null': 'True'}),
            'date_mod': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['neuroelectro.User']"})
        },
        'neuroelectro.userupload': {
            'Meta': {'object_name': 'UserUpload'},
            'data': ('picklefield.fields.PickledObjectField', [], {'null': 'True'}),
            'date_mod': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'path': ('django.db.models.fields.FilePathField', [], {'max_length': '100'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['neuroelectro.User']"})
        }
    }

    complete_apps = ['neuroelectro']