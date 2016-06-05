# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('neuroelectro', '0021_datatablestat'),
    ]

    operations = [
        migrations.AlterField(
            model_name='datatablestat',
            name='last_curated_on',
            field=models.DateTimeField(default=datetime.datetime.now),
        ),
    ]
