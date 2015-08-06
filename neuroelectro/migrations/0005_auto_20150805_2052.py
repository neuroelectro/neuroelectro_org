# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('neuroelectro', '0004_auto_20150805_2021'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='uservalidation',
            name='user',
        ),
        migrations.RemoveField(
            model_name='articlemetadatamap',
            name='validated_by',
        ),
        migrations.DeleteModel(
            name='UserValidation',
        ),
    ]
