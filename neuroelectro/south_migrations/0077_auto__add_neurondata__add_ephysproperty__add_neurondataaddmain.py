# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'NeuronData'
        db.create_table(u'neuroelectro_neurondata', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('article_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['neuroelectro.NeuronDataAddMain'])),
            ('neuron_name', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal(u'neuroelectro', ['NeuronData'])

        # Adding model 'EphysProperty'
        db.create_table(u'neuroelectro_ephysproperty', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('neuron_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['neuroelectro.NeuronData'])),
            ('ephys_name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('ephys_value', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal(u'neuroelectro', ['EphysProperty'])

        # Adding model 'NeuronDataAddMain'
        db.create_table(u'neuroelectro_neurondataaddmain', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('pubmed_id', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal(u'neuroelectro', ['NeuronDataAddMain'])


    def backwards(self, orm):
        # Deleting model 'NeuronData'
        db.delete_table(u'neuroelectro_neurondata')

        # Deleting model 'EphysProperty'
        db.delete_table(u'neuroelectro_ephysproperty')

        # Deleting model 'NeuronDataAddMain'
        db.delete_table(u'neuroelectro_neurondataaddmain')


    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'neuroelectro.api': {
            'Meta': {'object_name': 'API'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip': ('django.db.models.fields.GenericIPAddressField', [], {'max_length': '39'}),
            'path': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'time': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        u'neuroelectro.article': {
            'Meta': {'object_name': 'Article'},
            'abstract': ('django.db.models.fields.CharField', [], {'max_length': '10000', 'null': 'True'}),
            'author_list_str': ('django.db.models.fields.CharField', [], {'max_length': '500', 'null': 'True'}),
            'authors': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['neuroelectro.Author']", 'null': 'True', 'symmetrical': 'False'}),
            'full_text_link': ('django.db.models.fields.CharField', [], {'max_length': '1000', 'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'journal': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['neuroelectro.Journal']", 'null': 'True'}),
            'pmid': ('django.db.models.fields.IntegerField', [], {}),
            'pub_year': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'substances': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['neuroelectro.Substance']", 'null': 'True', 'symmetrical': 'False'}),
            'suggester': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': u"orm['neuroelectro.User']", 'null': 'True'}),
            'terms': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['neuroelectro.MeshTerm']", 'null': 'True', 'symmetrical': 'False'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '500'})
        },
        u'neuroelectro.articlefulltext': {
            'Meta': {'object_name': 'ArticleFullText'},
            'article': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['neuroelectro.Article']"}),
            'full_text_file': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'neuroelectro.articlefulltextstat': {
            'Meta': {'object_name': 'ArticleFullTextStat'},
            'article_full_text': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['neuroelectro.ArticleFullText']"}),
            'data_table_ephys_processed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'date_mod': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'metadata_human_assigned': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'metadata_processed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'methods_tag_found': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'neuron_article_map_processed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'num_unique_ephys_concept_maps': ('django.db.models.fields.IntegerField', [], {'null': 'True'})
        },
        u'neuroelectro.articlemetadatamap': {
            'Meta': {'object_name': 'ArticleMetaDataMap'},
            'added_by': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['neuroelectro.User']", 'null': 'True'}),
            'article': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['neuroelectro.Article']"}),
            'date_mod': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'metadata': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['neuroelectro.MetaData']"}),
            'note': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True'}),
            'times_validated': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True'})
        },
        u'neuroelectro.articlesummary': {
            'Meta': {'object_name': 'ArticleSummary'},
            'article': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['neuroelectro.Article']"}),
            'data': ('django.db.models.fields.TextField', [], {'default': "''"}),
            'date_mod': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'num_nedms': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'num_neurons': ('django.db.models.fields.IntegerField', [], {'null': 'True'})
        },
        u'neuroelectro.author': {
            'Meta': {'object_name': 'Author'},
            'first': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'initials': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True'}),
            'last': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True'}),
            'middle': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True'})
        },
        u'neuroelectro.brainregion': {
            'Meta': {'object_name': 'BrainRegion'},
            'abbrev': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'allenid': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True'}),
            'color': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'isallen': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '500'}),
            'treedepth': ('django.db.models.fields.IntegerField', [], {'null': 'True'})
        },
        u'neuroelectro.contvalue': {
            'Meta': {'object_name': 'ContValue'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'max_range': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'mean': ('django.db.models.fields.FloatField', [], {}),
            'min_range': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'n': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'stderr': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'stdev': ('django.db.models.fields.FloatField', [], {'null': 'True'})
        },
        u'neuroelectro.datasource': {
            'Meta': {'object_name': 'DataSource'},
            'data_table': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['neuroelectro.DataTable']", 'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'user_submission': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['neuroelectro.UserSubmission']", 'null': 'True'}),
            'user_upload': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['neuroelectro.UserUpload']", 'null': 'True'})
        },
        u'neuroelectro.datatable': {
            'Meta': {'object_name': 'DataTable'},
            'article': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['neuroelectro.Article']"}),
            'date_mod': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'link': ('django.db.models.fields.CharField', [], {'max_length': '1000', 'null': 'True'}),
            'needs_expert': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'note': ('django.db.models.fields.CharField', [], {'max_length': '500', 'null': 'True'}),
            'table_html': ('picklefield.fields.PickledObjectField', [], {'null': 'True'}),
            'table_text': ('django.db.models.fields.CharField', [], {'max_length': '10000', 'null': 'True'})
        },
        u'neuroelectro.ephysconceptmap': {
            'Meta': {'object_name': 'EphysConceptMap'},
            'added_by': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['neuroelectro.User']", 'null': 'True'}),
            'date_mod': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'dt_id': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True'}),
            'ephys_prop': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['neuroelectro.EphysProp']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'match_quality': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'note': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True'}),
            'ref_text': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True'}),
            'source': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['neuroelectro.DataSource']"}),
            'times_validated': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        u'neuroelectro.ephysprop': {
            'Meta': {'object_name': 'EphysProp'},
            'definition': ('django.db.models.fields.CharField', [], {'max_length': '1000', 'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'nlex_id': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True'}),
            'norm_criteria': ('django.db.models.fields.CharField', [], {'max_length': '1000', 'null': 'True'}),
            'synonyms': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['neuroelectro.EphysPropSyn']", 'symmetrical': 'False'}),
            'units': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['neuroelectro.Unit']", 'null': 'True'})
        },
        u'neuroelectro.ephysproperty': {
            'Meta': {'object_name': 'EphysProperty'},
            'ephys_name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'ephys_value': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'neuron_id': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['neuroelectro.NeuronData']"})
        },
        u'neuroelectro.ephyspropsummary': {
            'Meta': {'object_name': 'EphysPropSummary'},
            'data': ('django.db.models.fields.TextField', [], {'default': "''"}),
            'date_mod': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'ephys_prop': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['neuroelectro.EphysProp']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'num_articles': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'num_nedms': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'num_neurons': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'value_mean_articles': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'value_mean_neurons': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'value_sd_articles': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'value_sd_neurons': ('django.db.models.fields.FloatField', [], {'null': 'True'})
        },
        u'neuroelectro.ephyspropsyn': {
            'Meta': {'object_name': 'EphysPropSyn'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'term': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        u'neuroelectro.insituexpt': {
            'Meta': {'object_name': 'InSituExpt'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'imageseriesid': ('django.db.models.fields.IntegerField', [], {}),
            'plane': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'regionexprs': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['neuroelectro.RegionExpr']", 'null': 'True', 'symmetrical': 'False'}),
            'valid': ('django.db.models.fields.BooleanField', [], {'default': 'True'})
        },
        u'neuroelectro.institution': {
            'Meta': {'object_name': 'Institution'},
            'country': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'state': ('django.db.models.fields.CharField', [], {'max_length': '2', 'null': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True'})
        },
        u'neuroelectro.journal': {
            'Meta': {'object_name': 'Journal'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'publisher': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['neuroelectro.Publisher']", 'null': 'True'}),
            'short_title': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '300'})
        },
        u'neuroelectro.mailinglistentry': {
            'Meta': {'object_name': 'MailingListEntry'},
            'comments': ('django.db.models.fields.CharField', [], {'max_length': '500', 'null': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True'})
        },
        u'neuroelectro.meshterm': {
            'Meta': {'object_name': 'MeshTerm'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'term': ('django.db.models.fields.CharField', [], {'max_length': '300'})
        },
        u'neuroelectro.metadata': {
            'Meta': {'object_name': 'MetaData'},
            'cont_value': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['neuroelectro.ContValue']", 'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True'})
        },
        u'neuroelectro.neuron': {
            'Meta': {'object_name': 'Neuron'},
            'added_by': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True'}),
            'date_mod': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '500'}),
            'neuron_db_id': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'nlex_id': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True'}),
            'regions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['neuroelectro.BrainRegion']", 'null': 'True', 'symmetrical': 'False'}),
            'synonyms': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['neuroelectro.NeuronSyn']", 'null': 'True', 'symmetrical': 'False'})
        },
        u'neuroelectro.neuronarticlemap': {
            'Meta': {'object_name': 'NeuronArticleMap'},
            'added_by': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['neuroelectro.User']", 'null': 'True'}),
            'article': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['neuroelectro.Article']", 'null': 'True'}),
            'date_mod': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'neuron': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['neuroelectro.Neuron']"}),
            'num_mentions': ('django.db.models.fields.IntegerField', [], {'null': 'True'})
        },
        u'neuroelectro.neuronconceptmap': {
            'Meta': {'object_name': 'NeuronConceptMap'},
            'added_by': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['neuroelectro.User']", 'null': 'True'}),
            'date_mod': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'dt_id': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'match_quality': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'neuron': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['neuroelectro.Neuron']"}),
            'note': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True'}),
            'ref_text': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True'}),
            'source': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['neuroelectro.DataSource']"}),
            'times_validated': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        u'neuroelectro.neurondata': {
            'Meta': {'object_name': 'NeuronData'},
            'article_id': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['neuroelectro.NeuronDataAddMain']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'neuron_name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'neuroelectro.neurondataaddmain': {
            'Meta': {'object_name': 'NeuronDataAddMain'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'pubmed_id': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'neuroelectro.neuronephysdatamap': {
            'Meta': {'object_name': 'NeuronEphysDataMap'},
            'added_by': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['neuroelectro.User']", 'null': 'True'}),
            'date_mod': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'dt_id': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True'}),
            'ephys_concept_map': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['neuroelectro.EphysConceptMap']"}),
            'err': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'match_quality': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'metadata': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['neuroelectro.MetaData']", 'symmetrical': 'False'}),
            'n': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'neuron_concept_map': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['neuroelectro.NeuronConceptMap']"}),
            'norm_flag': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'note': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True'}),
            'ref_text': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True'}),
            'source': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['neuroelectro.DataSource']"}),
            'times_validated': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'val': ('django.db.models.fields.FloatField', [], {}),
            'val_norm': ('django.db.models.fields.FloatField', [], {'null': 'True'})
        },
        u'neuroelectro.neuronephyssummary': {
            'Meta': {'object_name': 'NeuronEphysSummary'},
            'data': ('django.db.models.fields.TextField', [], {'default': "''"}),
            'date_mod': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'ephys_prop': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['neuroelectro.EphysProp']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'neuron': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['neuroelectro.Neuron']"}),
            'num_articles': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'num_nedms': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'value_mean': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'value_sd': ('django.db.models.fields.FloatField', [], {'null': 'True'})
        },
        u'neuroelectro.neuronsummary': {
            'Meta': {'object_name': 'NeuronSummary'},
            'cluster_xval': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'cluster_yval': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'data': ('django.db.models.fields.TextField', [], {'default': "''"}),
            'date_mod': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'neuron': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['neuroelectro.Neuron']"}),
            'num_articles': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'num_ephysprops': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'num_nedms': ('django.db.models.fields.IntegerField', [], {'null': 'True'})
        },
        u'neuroelectro.neuronsyn': {
            'Meta': {'object_name': 'NeuronSyn'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'term': ('django.db.models.fields.CharField', [], {'max_length': '500'})
        },
        u'neuroelectro.protein': {
            'Meta': {'object_name': 'Protein'},
            'allenid': ('django.db.models.fields.IntegerField', [], {}),
            'common_name': ('django.db.models.fields.CharField', [], {'max_length': '400', 'null': 'True'}),
            'entrezid': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'gene': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'in_situ_expts': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['neuroelectro.InSituExpt']", 'null': 'True', 'symmetrical': 'False'}),
            'is_channel': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '400'}),
            'synonyms': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['neuroelectro.ProteinSyn']", 'null': 'True', 'symmetrical': 'False'})
        },
        u'neuroelectro.proteinsyn': {
            'Meta': {'object_name': 'ProteinSyn'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'term': ('django.db.models.fields.CharField', [], {'max_length': '500'})
        },
        u'neuroelectro.publisher': {
            'Meta': {'object_name': 'Publisher'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'neuroelectro.regionexpr': {
            'Meta': {'object_name': 'RegionExpr'},
            'expr_density': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'expr_energy': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'expr_energy_cv': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'region': ('django.db.models.fields.related.ForeignKey', [], {'default': '0', 'to': u"orm['neuroelectro.BrainRegion']"})
        },
        u'neuroelectro.species': {
            'Meta': {'object_name': 'Species'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '500'})
        },
        u'neuroelectro.substance': {
            'Meta': {'object_name': 'Substance'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'term': ('django.db.models.fields.CharField', [], {'max_length': '300'})
        },
        u'neuroelectro.unit': {
            'Meta': {'object_name': 'Unit'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'prefix': ('django.db.models.fields.CharField', [], {'max_length': '1'})
        },
        u'neuroelectro.user': {
            'Meta': {'object_name': 'User'},
            'assigned_neurons': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['neuroelectro.Neuron']", 'null': 'True', 'symmetrical': 'False'}),
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Group']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'institution': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['neuroelectro.Institution']", 'null': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_curator': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'lab_head': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True'}),
            'lab_website_url': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'last_update': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Permission']"}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'neuroelectro.usersubmission': {
            'Meta': {'object_name': 'UserSubmission'},
            'article': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['neuroelectro.Article']", 'null': 'True'}),
            'data': ('picklefield.fields.PickledObjectField', [], {'null': 'True'}),
            'date_mod': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['neuroelectro.User']"})
        },
        u'neuroelectro.userupload': {
            'Meta': {'object_name': 'UserUpload'},
            'data': ('picklefield.fields.PickledObjectField', [], {'null': 'True'}),
            'date_mod': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'path': ('django.db.models.fields.FilePathField', [], {'max_length': '100'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['neuroelectro.User']"})
        }
    }

    complete_apps = ['neuroelectro']