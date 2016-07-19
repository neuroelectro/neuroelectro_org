# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('neuroelectro', '0026_auto_20160629_1641'),
    ]

    operations = [
        migrations.AddField(
            model_name='articlecheck',
            name='has_methods_section',
            field=models.NullBooleanField(),
        ),
        migrations.AddField(
            model_name='articlecheck',
            name='has_publisher_source',
            field=models.NullBooleanField(),
        ),
        migrations.AlterField(
            model_name='articlecheck',
            name='created_on',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
