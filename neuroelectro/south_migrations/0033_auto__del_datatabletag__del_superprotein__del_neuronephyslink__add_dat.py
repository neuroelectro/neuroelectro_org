# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Deleting model 'DataTableTag'
        db.delete_table('neuroelectro_datatabletag')

        # Deleting model 'SuperProtein'
        db.delete_table('neuroelectro_superprotein')

        # Removing M2M table for field synonyms on 'SuperProtein'
        db.delete_table('neuroelectro_superprotein_synonyms')

        # Deleting model 'NeuronEphysLink'
        db.delete_table('neuroelectro_neuronephyslink')

        # Adding model 'DataSource'
        db.create_table('neuroelectro_datasource', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user_submission', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['neuroelectro.UserSubmission'], null=True)),
            ('user_upload', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['neuroelectro.UserUpload'], null=True)),
            ('data_table', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['neuroelectro.DataTable'], null=True)),
        ))
        db.send_create_signal('neuroelectro', ['DataSource'])

        # Adding model 'User'
        db.create_table('neuroelectro_user', (
            ('user_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['auth.User'], unique=True, primary_key=True)),
            ('institution', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['neuroelectro.Institution'])),
        ))
        db.send_create_signal('neuroelectro', ['User'])

        # Adding model 'UserUpload'
        db.create_table('neuroelectro_userupload', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('date_mod', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['neuroelectro.User'])),
            ('path', self.gf('django.db.models.fields.FilePathField')(max_length=100)),
            ('data', self.gf('picklefield.fields.PickledObjectField')(null=True)),
        ))
        db.send_create_signal('neuroelectro', ['UserUpload'])

        # Adding model 'UserSubmission'
        db.create_table('neuroelectro_usersubmission', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('date_mod', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['neuroelectro.User'])),
            ('data', self.gf('picklefield.fields.PickledObjectField')(null=True)),
        ))
        db.send_create_signal('neuroelectro', ['UserSubmission'])

        # Adding model 'Institution'
        db.create_table('neuroelectro_institution', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('type', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('country', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('state', self.gf('django.db.models.fields.CharField')(max_length=2)),
        ))
        db.send_create_signal('neuroelectro', ['Institution'])

        # Adding model 'MetaData'
        db.create_table('neuroelectro_metadata', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('value', self.gf('django.db.models.fields.CharField')(max_length=100)),
        ))
        db.send_create_signal('neuroelectro', ['MetaData'])

        # Deleting field 'EphysConceptMap.ephys_prop_syn'
        db.delete_column('neuroelectro_ephysconceptmap', 'ephys_prop_syn_id')

        # Deleting field 'EphysConceptMap.data_table'
        db.delete_column('neuroelectro_ephysconceptmap', 'data_table_id')

        # Adding field 'EphysConceptMap.source'
        db.add_column('neuroelectro_ephysconceptmap', 'source', self.gf('django.db.models.fields.related.ForeignKey')(default=1, to=orm['neuroelectro.DataSource']), keep_default=False)

        # Deleting field 'EphysProp.unit'
        db.delete_column('neuroelectro_ephysprop', 'unit')

        # Adding field 'EphysProp.units'
        db.add_column('neuroelectro_ephysprop', 'units', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['neuroelectro.Unit'], null=True), keep_default=False)

        # Adding field 'EphysProp.definition'
        db.add_column('neuroelectro_ephysprop', 'definition', self.gf('django.db.models.fields.CharField')(max_length=1000, null=True), keep_default=False)

        # Adding M2M table for field synonyms on 'EphysProp'
        db.create_table('neuroelectro_ephysprop_synonyms', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('ephysprop', models.ForeignKey(orm['neuroelectro.ephysprop'], null=False)),
            ('ephyspropsyn', models.ForeignKey(orm['neuroelectro.ephyspropsyn'], null=False))
        ))
        db.create_unique('neuroelectro_ephysprop_synonyms', ['ephysprop_id', 'ephyspropsyn_id'])

        # Deleting field 'EphysPropSyn.ephys_prop'
        db.delete_column('neuroelectro_ephyspropsyn', 'ephys_prop_id')

        # Deleting field 'NeuronEphysDataMap.data_table'
        db.delete_column('neuroelectro_neuronephysdatamap', 'data_table_id')

        # Adding field 'NeuronEphysDataMap.source'
        db.add_column('neuroelectro_neuronephysdatamap', 'source', self.gf('django.db.models.fields.related.ForeignKey')(default=1, to=orm['neuroelectro.DataSource']), keep_default=False)

        # Adding field 'NeuronEphysDataMap.match_quality'
        db.add_column('neuroelectro_neuronephysdatamap', 'match_quality', self.gf('django.db.models.fields.IntegerField')(null=True), keep_default=False)

        # Adding M2M table for field metadata on 'NeuronEphysDataMap'
        db.create_table('neuroelectro_neuronephysdatamap_metadata', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('neuronephysdatamap', models.ForeignKey(orm['neuroelectro.neuronephysdatamap'], null=False)),
            ('metadata', models.ForeignKey(orm['neuroelectro.metadata'], null=False))
        ))
        db.create_unique('neuroelectro_neuronephysdatamap_metadata', ['neuronephysdatamap_id', 'metadata_id'])

        # Removing M2M table for field defining_articles on 'Neuron'
        db.delete_table('neuroelectro_neuron_defining_articles')

        # Adding field 'Author.middle'
        db.add_column('neuroelectro_author', 'middle', self.gf('django.db.models.fields.CharField')(max_length=100, null=True), keep_default=False)

        # Adding field 'NeuronSummary.data'
        db.add_column('neuroelectro_neuronsummary', 'data', self.gf('django.db.models.fields.TextField')(default=''), keep_default=False)

        # Adding field 'NeuronSummary.num_ephysprops'
        db.add_column('neuroelectro_neuronsummary', 'num_ephysprops', self.gf('django.db.models.fields.IntegerField')(null=True), keep_default=False)

        # Adding field 'Article.suggester'
        db.add_column('neuroelectro_article', 'suggester', self.gf('django.db.models.fields.related.ForeignKey')(default=1, to=orm['neuroelectro.User']), keep_default=False)

        # Adding M2M table for field metadata on 'Article'
        db.create_table('neuroelectro_article_metadata', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('article', models.ForeignKey(orm['neuroelectro.article'], null=False)),
            ('metadata', models.ForeignKey(orm['neuroelectro.metadata'], null=False))
        ))
        db.create_unique('neuroelectro_article_metadata', ['article_id', 'metadata_id'])

        # Adding field 'DataTable.date_mod'
        db.add_column('neuroelectro_datatable', 'date_mod', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, default=datetime.datetime.now(), blank=True), keep_default=False)

        # Removing M2M table for field neurons on 'DataTable'
        db.delete_table('neuroelectro_datatable_neurons')

        # Deleting field 'Species.specie'
        db.delete_column('neuroelectro_species', 'specie')

        # Adding field 'Species.name'
        db.add_column('neuroelectro_species', 'name', self.gf('django.db.models.fields.CharField')(default='', max_length=500), keep_default=False)

        # Adding field 'EphysPropSummary.data'
        db.add_column('neuroelectro_ephyspropsummary', 'data', self.gf('django.db.models.fields.TextField')(default=''), keep_default=False)

        # Deleting field 'NeuronConceptMap.neuron_syn'
        db.delete_column('neuroelectro_neuronconceptmap', 'neuron_syn_id')

        # Deleting field 'NeuronConceptMap.data_table'
        db.delete_column('neuroelectro_neuronconceptmap', 'data_table_id')

        # Adding field 'NeuronConceptMap.source'
        db.add_column('neuroelectro_neuronconceptmap', 'source', self.gf('django.db.models.fields.related.ForeignKey')(default=1, to=orm['neuroelectro.DataSource']), keep_default=False)

        # Deleting field 'NeuronArticleMap.neuron_syn'
        db.delete_column('neuroelectro_neuronarticlemap', 'neuron_syn_id')

        # Adding field 'Unit.prefix'
        db.add_column('neuroelectro_unit', 'prefix', self.gf('django.db.models.fields.CharField')(default='', max_length=1), keep_default=False)

        # Adding field 'ArticleSummary.data'
        db.add_column('neuroelectro_articlesummary', 'data', self.gf('django.db.models.fields.TextField')(default=''), keep_default=False)

        # Adding field 'NeuronEphysSummary.data'
        db.add_column('neuroelectro_neuronephyssummary', 'data', self.gf('django.db.models.fields.TextField')(default=''), keep_default=False)


    def backwards(self, orm):
        
        # Adding model 'DataTableTag'
        db.create_table('neuroelectro_datatabletag', (
            ('neuron', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['neuroelectro.Neuron'])),
            ('ephys_prop', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['neuroelectro.EphysProp'])),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('neuroelectro', ['DataTableTag'])

        # Adding model 'SuperProtein'
        db.create_table('neuroelectro_superprotein', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('is_channel', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=400)),
        ))
        db.send_create_signal('neuroelectro', ['SuperProtein'])

        # Adding M2M table for field synonyms on 'SuperProtein'
        db.create_table('neuroelectro_superprotein_synonyms', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('superprotein', models.ForeignKey(orm['neuroelectro.superprotein'], null=False)),
            ('proteinsyn', models.ForeignKey(orm['neuroelectro.proteinsyn'], null=False))
        ))
        db.create_unique('neuroelectro_superprotein_synonyms', ['superprotein_id', 'proteinsyn_id'])

        # Adding model 'NeuronEphysLink'
        db.create_table('neuroelectro_neuronephyslink', (
            ('val_err', self.gf('django.db.models.fields.FloatField')(null=True)),
            ('ephys_prop', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['neuroelectro.EphysProp'])),
            ('val', self.gf('django.db.models.fields.FloatField')()),
            ('neuron', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['neuroelectro.Neuron'])),
            ('num_reps', self.gf('django.db.models.fields.IntegerField')(null=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('data_table', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['neuroelectro.DataTable'])),
        ))
        db.send_create_signal('neuroelectro', ['NeuronEphysLink'])

        # Deleting model 'DataSource'
        db.delete_table('neuroelectro_datasource')

        # Deleting model 'User'
        db.delete_table('neuroelectro_user')

        # Deleting model 'UserUpload'
        db.delete_table('neuroelectro_userupload')

        # Deleting model 'UserSubmission'
        db.delete_table('neuroelectro_usersubmission')

        # Deleting model 'Institution'
        db.delete_table('neuroelectro_institution')

        # Deleting model 'MetaData'
        db.delete_table('neuroelectro_metadata')

        # Adding field 'EphysConceptMap.ephys_prop_syn'
        db.add_column('neuroelectro_ephysconceptmap', 'ephys_prop_syn', self.gf('django.db.models.fields.related.ForeignKey')(default=0, to=orm['neuroelectro.EphysPropSyn']), keep_default=False)

        # Adding field 'EphysConceptMap.data_table'
        db.add_column('neuroelectro_ephysconceptmap', 'data_table', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['neuroelectro.DataTable'], null=True), keep_default=False)

        # Deleting field 'EphysConceptMap.source'
        db.delete_column('neuroelectro_ephysconceptmap', 'source_id')

        # Adding field 'EphysProp.unit'
        db.add_column('neuroelectro_ephysprop', 'unit', self.gf('django.db.models.fields.CharField')(max_length=20, null=True), keep_default=False)

        # Deleting field 'EphysProp.units'
        db.delete_column('neuroelectro_ephysprop', 'units_id')

        # Deleting field 'EphysProp.definition'
        db.delete_column('neuroelectro_ephysprop', 'definition')

        # Removing M2M table for field synonyms on 'EphysProp'
        db.delete_table('neuroelectro_ephysprop_synonyms')

        # Adding field 'EphysPropSyn.ephys_prop'
        db.add_column('neuroelectro_ephyspropsyn', 'ephys_prop', self.gf('django.db.models.fields.related.ForeignKey')(default=0, to=orm['neuroelectro.EphysProp']), keep_default=False)

        # Adding field 'NeuronEphysDataMap.data_table'
        db.add_column('neuroelectro_neuronephysdatamap', 'data_table', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['neuroelectro.DataTable'], null=True), keep_default=False)

        # Deleting field 'NeuronEphysDataMap.source'
        db.delete_column('neuroelectro_neuronephysdatamap', 'source_id')

        # Deleting field 'NeuronEphysDataMap.match_quality'
        db.delete_column('neuroelectro_neuronephysdatamap', 'match_quality')

        # Removing M2M table for field metadata on 'NeuronEphysDataMap'
        db.delete_table('neuroelectro_neuronephysdatamap_metadata')

        # Adding M2M table for field defining_articles on 'Neuron'
        db.create_table('neuroelectro_neuron_defining_articles', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('neuron', models.ForeignKey(orm['neuroelectro.neuron'], null=False)),
            ('article', models.ForeignKey(orm['neuroelectro.article'], null=False))
        ))
        db.create_unique('neuroelectro_neuron_defining_articles', ['neuron_id', 'article_id'])

        # Deleting field 'Author.middle'
        db.delete_column('neuroelectro_author', 'middle')

        # Deleting field 'NeuronSummary.data'
        db.delete_column('neuroelectro_neuronsummary', 'data')

        # Deleting field 'NeuronSummary.num_ephysprops'
        db.delete_column('neuroelectro_neuronsummary', 'num_ephysprops')

        # Deleting field 'Article.suggester'
        db.delete_column('neuroelectro_article', 'suggester_id')

        # Removing M2M table for field metadata on 'Article'
        db.delete_table('neuroelectro_article_metadata')

        # Deleting field 'DataTable.date_mod'
        db.delete_column('neuroelectro_datatable', 'date_mod')

        # Adding M2M table for field neurons on 'DataTable'
        db.create_table('neuroelectro_datatable_neurons', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('datatable', models.ForeignKey(orm['neuroelectro.datatable'], null=False)),
            ('neuron', models.ForeignKey(orm['neuroelectro.neuron'], null=False))
        ))
        db.create_unique('neuroelectro_datatable_neurons', ['datatable_id', 'neuron_id'])

        # Adding field 'Species.specie'
        db.add_column('neuroelectro_species', 'specie', self.gf('django.db.models.fields.CharField')(default=0, max_length=500), keep_default=False)

        # Deleting field 'Species.name'
        db.delete_column('neuroelectro_species', 'name')

        # Deleting field 'EphysPropSummary.data'
        db.delete_column('neuroelectro_ephyspropsummary', 'data')

        # Adding field 'NeuronConceptMap.neuron_syn'
        db.add_column('neuroelectro_neuronconceptmap', 'neuron_syn', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['neuroelectro.NeuronSyn'], null=True), keep_default=False)

        # Adding field 'NeuronConceptMap.data_table'
        db.add_column('neuroelectro_neuronconceptmap', 'data_table', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['neuroelectro.DataTable'], null=True), keep_default=False)

        # Deleting field 'NeuronConceptMap.source'
        db.delete_column('neuroelectro_neuronconceptmap', 'source_id')

        # Adding field 'NeuronArticleMap.neuron_syn'
        db.add_column('neuroelectro_neuronarticlemap', 'neuron_syn', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['neuroelectro.NeuronSyn'], null=True), keep_default=False)

        # Deleting field 'Unit.prefix'
        db.delete_column('neuroelectro_unit', 'prefix')

        # Deleting field 'ArticleSummary.data'
        db.delete_column('neuroelectro_articlesummary', 'data')

        # Deleting field 'NeuronEphysSummary.data'
        db.delete_column('neuroelectro_neuronephyssummary', 'data')


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
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2012, 11, 20, 23, 24, 54, 65820)'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2012, 11, 20, 23, 24, 54, 65741)'}),
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
            'metadata': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['neuroelectro.MetaData']", 'symmetrical': 'False'}),
            'pmid': ('django.db.models.fields.IntegerField', [], {}),
            'pub_year': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'substances': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['neuroelectro.Substance']", 'null': 'True', 'symmetrical': 'False'}),
            'suggester': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['neuroelectro.User']"}),
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
            'country': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'state': ('django.db.models.fields.CharField', [], {'max_length': '2'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '50'})
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
            'added_by': ('django.db.models.fields.CharField', [], {'default': "'robot'", 'max_length': '20'}),
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
            'region': ('django.db.models.fields.related.ForeignKey', [], {'default': '1', 'to': "orm['neuroelectro.BrainRegion']"}),
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
            'institution': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['neuroelectro.Institution']"}),
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
