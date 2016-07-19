# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('neuroelectro', '0025_auto_20160607_1439'),
    ]

    operations = [
        migrations.CreateModel(
            name='ArticleCheck',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('pmid', models.IntegerField()),
                ('created_on', models.DateTimeField(default=datetime.datetime(2016, 6, 29, 23, 41, 29, 370868, tzinfo=utc))),
                ('last_modified', models.DateTimeField(auto_now=True)),
                ('journal', models.ForeignKey(to='neuroelectro.Journal', null=True)),
            ],
        ),
        migrations.RemoveField(
            model_name='articlefulltext',
            name='full_text_file_path',
        ),
        migrations.AlterField(
            model_name='articlefulltext',
            name='full_text_file',
            field=models.FileField(null=True, upload_to=b'full_texts'),
        ),
    ]
