# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('neuroelectro', '0013_auto_20151106_1210'),
    ]

    operations = [
        migrations.AddField(
            model_name='ephysprop',
            name='max_range',
            field=models.FloatField(null=True),
        ),
        migrations.AddField(
            model_name='ephysprop',
            name='min_range',
            field=models.FloatField(null=True),
        ),
        migrations.AddField(
            model_name='ephysprop',
            name='plot_transform',
            field=models.CharField(default=b'linear', max_length=20),
        ),
        migrations.AddField(
            model_name='ephysprop',
            name='short_name',
            field=models.CharField(max_length=20, null=True),
        ),
    ]
