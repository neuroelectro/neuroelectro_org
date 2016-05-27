# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('neuroelectro', '0016_auto_20160307_1719'),
    ]

    operations = [
        migrations.AddField(
            model_name='datatable',
            name='currently_irrelevant_flag',
            field=models.BooleanField(default=False),
        ),
    ]
