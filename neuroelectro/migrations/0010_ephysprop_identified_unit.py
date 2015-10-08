# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('neuroelectro', '0009_auto_20151007_1433'),
    ]

    operations = [
        migrations.AddField(
            model_name='ephysprop',
            name='identified_unit',
            field=models.CharField(max_length=10, null=True),
        ),
    ]
