# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('neuroelectro', '0020_usersubmission_error_type'),
    ]

    operations = [
        migrations.CreateModel(
            name='DataTableStat',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('last_curated_on', models.DateTimeField(auto_now=True)),
                ('curating_users', models.ManyToManyField(to=settings.AUTH_USER_MODEL)),
                ('data_table', models.ForeignKey(to='neuroelectro.DataTable')),
            ],
        ),
    ]
