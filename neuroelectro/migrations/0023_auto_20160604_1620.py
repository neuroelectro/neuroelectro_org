# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('neuroelectro', '0022_auto_20160604_1550'),
    ]

    operations = [
        migrations.AddField(
            model_name='datatablestat',
            name='num_ecms',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='datatablestat',
            name='num_ncms',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='datatablestat',
            name='num_nedms',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='datatablestat',
            name='times_validated',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='datatablestat',
            name='last_curated_on',
            field=models.DateTimeField(blank=True),
        ),
    ]
