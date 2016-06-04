# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('neuroelectro', '0019_auto_20160602_1832'),
    ]

    operations = [
        migrations.AddField(
            model_name='usersubmission',
            name='error_type',
            field=models.CharField(default=b'sem', max_length=50, choices=[(b'sem', b'Standard error of mean'), (b'sd', b'Standard deviation'), (b'other', b'other')]),
        ),
    ]
