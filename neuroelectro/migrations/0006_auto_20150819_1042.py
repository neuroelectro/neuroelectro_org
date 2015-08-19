# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('neuroelectro', '0005_auto_20150805_2052'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='insituexpt',
            name='regionexprs',
        ),
        migrations.RemoveField(
            model_name='protein',
            name='in_situ_expts',
        ),
        migrations.RemoveField(
            model_name='protein',
            name='synonyms',
        ),
        migrations.RemoveField(
            model_name='regionexpr',
            name='region',
        ),
        migrations.AlterField(
            model_name='article',
            name='authors',
            field=models.ManyToManyField(to='neuroelectro.Author'),
        ),
        migrations.AlterField(
            model_name='article',
            name='substances',
            field=models.ManyToManyField(to='neuroelectro.Substance'),
        ),
        migrations.AlterField(
            model_name='article',
            name='terms',
            field=models.ManyToManyField(to='neuroelectro.MeshTerm'),
        ),
        migrations.AlterField(
            model_name='neuron',
            name='regions',
            field=models.ManyToManyField(to='neuroelectro.BrainRegion'),
        ),
        migrations.AlterField(
            model_name='neuron',
            name='synonyms',
            field=models.ManyToManyField(to='neuroelectro.NeuronSyn'),
        ),
        migrations.AlterField(
            model_name='neuronephysdatamap',
            name='exp_fact_concept_maps',
            field=models.ManyToManyField(to='neuroelectro.ExpFactConceptMap'),
        ),
        migrations.AlterField(
            model_name='user',
            name='assigned_neurons',
            field=models.ManyToManyField(to='neuroelectro.Neuron', blank=True),
        ),
        migrations.DeleteModel(
            name='InSituExpt',
        ),
        migrations.DeleteModel(
            name='Protein',
        ),
        migrations.DeleteModel(
            name='ProteinSyn',
        ),
        migrations.DeleteModel(
            name='RegionExpr',
        ),
    ]
