# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('neuroelectro', '0002_auto_20150805_1052'),
    ]

    operations = [
        migrations.RenameField(
            model_name='ephysconceptmap',
            old_name='added_by',
            new_name='changed_by',
        ),
        migrations.RenameField(
            model_name='expfactconceptmap',
            old_name='added_by',
            new_name='changed_by',
        ),
        migrations.RenameField(
            model_name='neuronconceptmap',
            old_name='added_by',
            new_name='changed_by',
        ),
        migrations.RenameField(
            model_name='neuronephysdatamap',
            old_name='added_by',
            new_name='changed_by',
        ),
        migrations.RemoveField(
            model_name='ephysconceptmap',
            name='validated_by',
        ),
        migrations.RemoveField(
            model_name='expfactconceptmap',
            name='validated_by',
        ),
        migrations.RemoveField(
            model_name='neuronconceptmap',
            name='validated_by',
        ),
        migrations.RemoveField(
            model_name='neuronephysdatamap',
            name='validated_by',
        ),
    ]
