# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('neuroelectro', '0015_auto_20160209_1600'),
    ]

    operations = [
        migrations.AddField(
            model_name='historicalneuronconceptmap',
            name='neuroner_ids',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='neuronconceptmap',
            name='neuroner_ids',
            field=models.TextField(null=True),
        ),
    ]
