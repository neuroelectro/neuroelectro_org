# -*- coding: utf-8 -*-

__author__ = 'shreejoy'

import unittest
import neuroelectro.models as m
from db_functions.normalize_ephys_data import check_data_val_range, normalize_nedm_val


class DataRangeTest(unittest.TestCase):

    def test_check_data_val_range_in(self):
        ephys_prop = m.EphysProp.objects.create(name = 'input resistance')

        data_val = 100
        output_bool = check_data_val_range(data_val, ephys_prop)
        expected_bool = True
        self.assertEqual(output_bool, expected_bool)

    def test_check_data_val_range_out(self):
        ephys_prop = m.EphysProp.objects.create(name = 'input resistance')

        data_val = -10
        output_bool = check_data_val_range(data_val, ephys_prop)
        expected_bool = False
        self.assertEqual(output_bool, expected_bool)


class NormalizeValTest(unittest.TestCase):

    def test_normalize_nedm_val(self):
        with open('tests/test_html_data_tables/example_html_table_exp_facts.html', mode='rb') as f:
            exp_fact_table_text = f.read()
        article_ob = m.Article.objects.create(title='asdf', pmid='456')
        data_table_ob = m.DataTable.objects.create(table_html=exp_fact_table_text, article=article_ob)
        data_source_ob = m.DataSource.objects.create(data_table=data_table_ob)

        # create ephys concept maps
        ephys_unit = m.Unit.objects.create(name=u'Ω', prefix = 'M')
        ir_ephys_ob = m.EphysProp.objects.create(name='input resistance', units = ephys_unit)
        ecm = m.EphysConceptMap.objects.create(dt_id='td-68', source=data_source_ob, ephys_prop=ir_ephys_ob, ref_text = u'blah (GΩ)')

        neuron_ob = m.Neuron.objects.get_or_create(name='Other')[0]
        ncm = m.NeuronConceptMap.objects.create(dt_id='th-2', source=data_source_ob, neuron=neuron_ob,
                                                neuron_long_name='thalamus parafascicular nucleus')

        input_value = .2
        nedm = m.NeuronEphysDataMap(neuron_concept_map = ncm, ephys_concept_map = ecm, dt_id = 'td-3', source = data_source_ob, val = input_value)

        normalized_value = normalize_nedm_val(nedm)
        expected_value = 200
        self.assertEqual(normalized_value, expected_value)