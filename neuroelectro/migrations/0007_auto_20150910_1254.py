# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('neuroelectro', '0006_auto_20150819_1042'),
    ]

    operations = [
        migrations.AddField(
            model_name='datatable',
            name='complex_neurons',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='datatable',
            name='irrelevant_flag',
            field=models.BooleanField(default=False),
        ),
    ]
