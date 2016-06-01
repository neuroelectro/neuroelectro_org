# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('neuroelectro', '0017_datatable_currently_irrelevant_flag'),
    ]

    operations = [
        migrations.AddField(
            model_name='metadata',
            name='ref_text',
            field=models.ForeignKey(to='neuroelectro.ReferenceText', null=True),
        ),
    ]
