# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('neuroelectro', '0010_ephysprop_identified_unit'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='ephysprop',
            name='identified_unit',
        ),
        migrations.AddField(
            model_name='ephysconceptmap',
            name='identified_unit',
            field=models.CharField(max_length=10, null=True),
        ),
        migrations.AddField(
            model_name='historicalephysconceptmap',
            name='identified_unit',
            field=models.CharField(max_length=10, null=True),
        ),
    ]
