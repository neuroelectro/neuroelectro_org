# -*- coding: utf-8 -*-
import django_tables2 as tables


class EphysPropListTable(tables.Table):
    name = tables.Column()
    neuron_count = tables.Column()
    value_count = tables.Column()