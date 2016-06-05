# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('neuroelectro', '0023_auto_20160604_1620'),
    ]

    operations = [
        migrations.AlterField(
            model_name='datatablestat',
            name='last_curated_on',
            field=models.DateTimeField(null=True),
        ),
    ]
