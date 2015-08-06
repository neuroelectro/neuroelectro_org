# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('neuroelectro', '0002_auto_20150805_1052'),
    ]

    operations = [
        migrations.CreateModel(
            name='HistoricalEphysConceptMap',
            fields=[
                ('id', models.IntegerField(verbose_name='ID', db_index=True, auto_created=True, blank=True)),
                ('ref_text', models.CharField(max_length=200, null=True)),
                ('match_quality', models.IntegerField(null=True)),
                ('dt_id', models.CharField(max_length=20, null=True)),
                ('times_validated', models.IntegerField(default=0)),
                ('note', models.CharField(max_length=200, null=True)),
                ('history_id', models.AutoField(serialize=False, primary_key=True)),
                ('history_date', models.DateTimeField()),
                ('history_type', models.CharField(max_length=1, choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')])),
                ('changed_by', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('ephys_prop', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to='neuroelectro.EphysProp', null=True)),
                ('history_user', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, null=True)),
                ('source', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to='neuroelectro.DataSource', null=True)),
            ],
            options={
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
                'verbose_name': 'historical ephys concept map',
            },
        ),
        migrations.CreateModel(
            name='HistoricalExpFactConceptMap',
            fields=[
                ('id', models.IntegerField(verbose_name='ID', db_index=True, auto_created=True, blank=True)),
                ('ref_text', models.CharField(max_length=200, null=True)),
                ('match_quality', models.IntegerField(null=True)),
                ('dt_id', models.CharField(max_length=20, null=True)),
                ('times_validated', models.IntegerField(default=0)),
                ('note', models.CharField(max_length=200, null=True)),
                ('history_id', models.AutoField(serialize=False, primary_key=True)),
                ('history_date', models.DateTimeField()),
                ('history_type', models.CharField(max_length=1, choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')])),
                ('changed_by', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('history_user', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, null=True)),
                ('metadata', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to='neuroelectro.MetaData', null=True)),
                ('source', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to='neuroelectro.DataSource', null=True)),
            ],
            options={
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
                'verbose_name': 'historical exp fact concept map',
            },
        ),
        migrations.CreateModel(
            name='HistoricalNeuronConceptMap',
            fields=[
                ('id', models.IntegerField(verbose_name='ID', db_index=True, auto_created=True, blank=True)),
                ('ref_text', models.CharField(max_length=200, null=True)),
                ('match_quality', models.IntegerField(null=True)),
                ('dt_id', models.CharField(max_length=20, null=True)),
                ('times_validated', models.IntegerField(default=0)),
                ('note', models.CharField(max_length=200, null=True)),
                ('neuron_long_name', models.CharField(max_length=1000, null=True)),
                ('history_id', models.AutoField(serialize=False, primary_key=True)),
                ('history_date', models.DateTimeField()),
                ('history_type', models.CharField(max_length=1, choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')])),
                ('changed_by', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('history_user', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, null=True)),
                ('neuron', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to='neuroelectro.Neuron', null=True)),
                ('source', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to='neuroelectro.DataSource', null=True)),
            ],
            options={
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
                'verbose_name': 'historical neuron concept map',
            },
        ),
        migrations.CreateModel(
            name='HistoricalNeuronEphysDataMap',
            fields=[
                ('id', models.IntegerField(verbose_name='ID', db_index=True, auto_created=True, blank=True)),
                ('ref_text', models.CharField(max_length=200, null=True)),
                ('match_quality', models.IntegerField(null=True)),
                ('dt_id', models.CharField(max_length=20, null=True)),
                ('times_validated', models.IntegerField(default=0)),
                ('note', models.CharField(max_length=200, null=True)),
                ('val', models.FloatField()),
                ('err', models.FloatField(null=True)),
                ('n', models.IntegerField(null=True)),
                ('val_norm', models.FloatField(null=True)),
                ('norm_flag', models.BooleanField(default=False)),
                ('history_id', models.AutoField(serialize=False, primary_key=True)),
                ('history_date', models.DateTimeField()),
                ('history_type', models.CharField(max_length=1, choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')])),
                ('changed_by', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
                'verbose_name': 'historical neuron ephys data map',
            },
        ),
        migrations.RenameField(
            model_name='ephysconceptmap',
            old_name='added_by',
            new_name='changed_by',
        ),
        migrations.RenameField(
            model_name='expfactconceptmap',
            old_name='added_by',
            new_name='changed_by',
        ),
        migrations.RenameField(
            model_name='neuronconceptmap',
            old_name='added_by',
            new_name='changed_by',
        ),
        migrations.RenameField(
            model_name='neuronephysdatamap',
            old_name='added_by',
            new_name='changed_by',
        ),
        migrations.RemoveField(
            model_name='expfactconceptmap',
            name='date_mod',
        ),
        migrations.RemoveField(
            model_name='expfactconceptmap',
            name='validated_by',
        ),
        migrations.AlterUniqueTogether(
            name='ephysconceptmap',
            unique_together=set([('source', 'dt_id')]),
        ),
        migrations.AlterUniqueTogether(
            name='neuronconceptmap',
            unique_together=set([('source', 'dt_id')]),
        ),
        migrations.AlterUniqueTogether(
            name='neuronephysdatamap',
            unique_together=set([('source', 'dt_id')]),
        ),
        migrations.AddField(
            model_name='historicalneuronephysdatamap',
            name='ephys_concept_map',
            field=models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to='neuroelectro.EphysConceptMap', null=True),
        ),
        migrations.AddField(
            model_name='historicalneuronephysdatamap',
            name='history_user',
            field=models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='historicalneuronephysdatamap',
            name='neuron_concept_map',
            field=models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to='neuroelectro.NeuronConceptMap', null=True),
        ),
        migrations.AddField(
            model_name='historicalneuronephysdatamap',
            name='source',
            field=models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to='neuroelectro.DataSource', null=True),
        ),
        migrations.RemoveField(
            model_name='ephysconceptmap',
            name='date_mod',
        ),
        migrations.RemoveField(
            model_name='ephysconceptmap',
            name='validated_by',
        ),
        migrations.RemoveField(
            model_name='neuronconceptmap',
            name='date_mod',
        ),
        migrations.RemoveField(
            model_name='neuronconceptmap',
            name='validated_by',
        ),
        migrations.RemoveField(
            model_name='neuronephysdatamap',
            name='date_mod',
        ),
        migrations.RemoveField(
            model_name='neuronephysdatamap',
            name='validated_by',
        ),
    ]
