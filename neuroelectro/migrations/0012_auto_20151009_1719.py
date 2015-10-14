# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('neuroelectro', '0011_auto_20151007_1859'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='metadata',
            name='ref_text',
        ),
        migrations.AddField(
            model_name='articlemetadatamap',
            name='ref_text',
            field=models.ForeignKey(to='neuroelectro.ReferenceText', null=True),
        ),
    ]
