# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('neuroelectro', '0014_auto_20160202_1450'),
    ]

    operations = [
        migrations.AddField(
            model_name='datatable',
            name='sd_error',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='datatable',
            name='uploading_user',
            field=models.ForeignKey(blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='datatable',
            name='user_uploaded',
            field=models.BooleanField(default=False),
        ),
    ]
