# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('neuroelectro', '0024_auto_20160604_1750'),
    ]

    operations = [
        migrations.AddField(
            model_name='articlefulltext',
            name='full_text_file_path',
            field=models.FilePathField(null=True, path=b'/data/neuroelectro_db_full_texts'),
        ),
        migrations.AlterField(
            model_name='articlefulltext',
            name='full_text_file',
            field=models.FileField(null=True, upload_to=b'/data/neuroelectro_db_full_texts'),
        ),
    ]
