# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('neuroelectro', '0008_auto_20150917_1706'),
    ]

    operations = [
        migrations.AddField(
            model_name='historicalneuronephysdatamap',
            name='err_norm',
            field=models.FloatField(null=True),
        ),
        migrations.AddField(
            model_name='neuronephysdatamap',
            name='err_norm',
            field=models.FloatField(null=True),
        ),
    ]
