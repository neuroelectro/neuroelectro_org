# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('neuroelectro', '0012_auto_20151009_1719'),
    ]

    operations = [
        migrations.AddField(
            model_name='articlefulltextstat',
            name='metadata_curation_note',
            field=models.CharField(max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='articlefulltextstat',
            name='metadata_needs_expert',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='articlefulltextstat',
            name='metadata_needs_peer_review',
            field=models.BooleanField(default=False),
        ),
    ]
