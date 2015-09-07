# -*- coding: utf-8 -*-

__author__ = 'shreejoy'

import unittest
from django.test import TestCase
from article_text_mining.assign_table_ephys_data import find_data_vals_in_table
import neuroelectro.models as m

class FindDataValuesTest(unittest.TestCase):

    def setUp(self):
        # data table object 16055
        with open('tests/test_data/example_html_table_simple.html', mode='rb') as f:
            simple_table_text = f.read()
        article_ob = m.Article.objects.create(title='asdf', pmid = '123')
        data_table_ob = m.DataTable.objects.create(table_html = simple_table_text, article = article_ob)
        data_source_ob = m.DataSource.objects.create(data_table = data_table_ob)

        # create neuron concept maps
        neuron_ob = m.Neuron.objects.create(name = 'Other')
        ncm = m.NeuronConceptMap.objects.create(dt_id = 'th-2', source = data_source_ob, neuron = neuron_ob, neuron_long_name = 'lateral hypothalamus fast-spiking GAD65-GFP neuron')

        # create ephys concept maps
        ephys_ob = m.EphysProp.objects.create(name = 'input resistance')
        ecm = m.EphysConceptMap.objects.create(dt_id = 'td-68', source = data_source_ob, ephys_prop = ephys_ob)


    def test_find_data_vals_in_table(self):
        expected_output_dict = {'td-69':
                                    {'ncm_pk': 1L, 'ecm_pk': 1L, 'data_value_dict':
                                        {'num_obs': 15, 'max_range': None, 'min_range': None, 'value': 463.0, 'error': 89.0},
                                     'efcm_pk_list': []
                                     }
                                }
        data_table_ob = m.DataTable.objects.get(article__pmid = '123')
        nedm_dict = find_data_vals_in_table(data_table_ob)
        self.assertEqual(expected_output_dict, nedm_dict)


if __name__ == '__main__':
    unittest.main()