# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('neuroelectro', '0007_auto_20150910_1254'),
    ]

    operations = [
        migrations.AddField(
            model_name='ephysconceptmap',
            name='expert_validated',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='expfactconceptmap',
            name='expert_validated',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='historicalephysconceptmap',
            name='expert_validated',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='historicalexpfactconceptmap',
            name='expert_validated',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='historicalneuronconceptmap',
            name='expert_validated',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='historicalneuronephysdatamap',
            name='expert_validated',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='neuronconceptmap',
            name='expert_validated',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='neuronephysdatamap',
            name='expert_validated',
            field=models.BooleanField(default=False),
        ),
    ]
