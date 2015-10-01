# -*- coding: utf-8 -*-

__author__ = 'shreejoy'

import unittest
from django.test import TestCase
from article_text_mining.assign_table_ephys_data import find_data_vals_in_table, assign_data_vals_to_table
import neuroelectro.models as m


class AssignTableEphysDataTest(unittest.TestCase):
    def setUp(self):
        # creates data table object 16055 with some dummy data
        with open('tests/test_html_data_tables/example_html_table_simple.html', mode='rb') as f:
            simple_table_text = f.read()
        article_ob = m.Article.objects.create(title='asdf', pmid='123')
        data_table_ob = m.DataTable.objects.create(table_html=simple_table_text, article=article_ob)
        data_source_ob = m.DataSource.objects.create(data_table=data_table_ob)

        # create neuron concept maps
        neuron_ob = m.Neuron.objects.create(name='Other')
        ncm = m.NeuronConceptMap.objects.create(dt_id='th-2', source=data_source_ob, neuron=neuron_ob,
                                                neuron_long_name='lateral hypothalamus fast-spiking GAD65-GFP neuron')

        # create ephys concept maps
        ir_ephys_ob = m.EphysProp.objects.create(name='input resistance')
        ecm = m.EphysConceptMap.objects.create(dt_id='td-68', source=data_source_ob, ephys_prop=ir_ephys_ob)

        # creates data table object 25 with some dummy data
        with open('tests/test_html_data_tables/example_html_table_exp_facts.html', mode='rb') as f:
            exp_fact_table_text = f.read()
        article_ob = m.Article.objects.create(title='asdf', pmid='456')
        data_table_ob = m.DataTable.objects.create(table_html=exp_fact_table_text, article=article_ob)
        data_source_ob = m.DataSource.objects.create(data_table=data_table_ob)

        # create neuron concept maps
        neuron_ob = m.Neuron.objects.get_or_create(name='Other')[0]
        ncm = m.NeuronConceptMap.objects.create(dt_id='th-2', source=data_source_ob, neuron=neuron_ob,
                                                neuron_long_name='thalamus parafascicular nucleus')

        # create ephys concept maps
        ecm = m.EphysConceptMap.objects.create(dt_id='td-5', source=data_source_ob, ephys_prop=ir_ephys_ob)
        rmp_ephys_ob = m.EphysProp.objects.create(name='resting membrane potential')
        ecm = m.EphysConceptMap.objects.create(dt_id='td-9', source=data_source_ob, ephys_prop=rmp_ephys_ob)

        cont_value = m.ContValue.objects.create(mean=10.5, min_range=9, max_range=12)
        metadata_ob = m.MetaData.objects.create(name='AnimalAge', cont_value=cont_value)
        efcm_ob = m.ExpFactConceptMap.objects.create(dt_id='th-2', source=data_source_ob, metadata=metadata_ob)

        # creates data table object 26387 with some dummy data
        with open('tests/test_html_data_tables/example_html_table_super_complex.html', mode='rb') as f:
            exp_fact_table_text = f.read()
        article_ob = m.Article.objects.create(title='asdf', pmid='789')
        data_table_ob = m.DataTable.objects.create(table_html=exp_fact_table_text, article=article_ob)
        data_source_ob = m.DataSource.objects.create(data_table=data_table_ob)

        # create neuron concept maps
        neuron_ob = m.Neuron.objects.get_or_create(name='Other')[0]
        ncm = m.NeuronConceptMap.objects.create(dt_id='td-6', source=data_source_ob, neuron=neuron_ob,
                                                neuron_long_name='Hypothalamus GnRH-expressing neuron')

        # create ephys concept maps
        ap_amp_ephys_ob = m.EphysProp.objects.create(name='spike amplitude')
        ap_hw_ephys_ob = m.EphysProp.objects.create(name='spike half-width')
        ecm = m.EphysConceptMap.objects.create(dt_id='td-77', source=data_source_ob, ephys_prop=ap_amp_ephys_ob)
        ecm = m.EphysConceptMap.objects.create(dt_id='td-94', source=data_source_ob, ephys_prop=ap_hw_ephys_ob)

    def tearDown(self):
        m.EphysConceptMap.objects.all().delete()
        m.NeuronConceptMap.objects.all().delete()
        m.Article.objects.all().delete()
        m.DataTable.objects.all().delete()
        m.DataSource.objects.all().delete()
        m.EphysProp.objects.all().delete()
        m.Neuron.objects.all().delete()

    def test_find_data_vals_in_table_simple(self):
        data_table_ob = m.DataTable.objects.get(article__pmid='123')
        ncm_pk = m.NeuronConceptMap.objects.filter(source__data_table=data_table_ob)[0].pk
        ecm_pk = m.EphysConceptMap.objects.filter(source__data_table=data_table_ob)[0].pk

        expected_output_dict = {'td-69':
                                    {'ncm_pk': ncm_pk, 'ecm_pk': ecm_pk, 'ref_text': u'463\xa0\xb1\xa089\xa0 (15)',
                                     'data_value_dict':
                                         {'num_obs': 15, 'max_range': None, 'min_range': None, 'value': 463.0,
                                          'error': 89.0},
                                     'efcm_pk_list': []
                                     }
                                }
        nedm_dict = find_data_vals_in_table(data_table_ob)
        self.assertDictEqual(expected_output_dict, nedm_dict)

    def test_assign_data_vals_to_table_simple(self):
        data_table_ob = m.DataTable.objects.filter(article__pmid='123')[0]
        assign_data_vals_to_table(data_table_ob)

        nedm_ob = m.NeuronEphysDataMap.objects.filter(source__data_table=data_table_ob)[0]
        nedm_dt_id = 'td-69'
        nedm_value = 463.0
        nedm_num_obs = 15

        self.assertEqual(nedm_dt_id, nedm_ob.dt_id)
        self.assertEqual(nedm_value, nedm_ob.val)
        self.assertEqual(nedm_num_obs, nedm_ob.n)

    def test_assign_data_vals_to_table_efcm(self):
        data_table_ob = m.DataTable.objects.filter(article__pmid='456')[0]
        assign_data_vals_to_table(data_table_ob)

        nedm_ob = m.NeuronEphysDataMap.objects.filter(source__data_table=data_table_ob)[0]
        efcm_ob_expected = m.ExpFactConceptMap.objects.filter(source__data_table=data_table_ob)[0]
        efcm_ob_assigned = nedm_ob.exp_fact_concept_maps.all()[0]

        self.assertEqual(efcm_ob_expected, efcm_ob_assigned)

    def test_assign_data_vals_to_table_complex(self):
        data_table_ob = m.DataTable.objects.filter(article__pmid='456')[0]
        assign_data_vals_to_table(data_table_ob)

        nedm_ob = m.NeuronEphysDataMap.objects.filter(source__data_table=data_table_ob)[0]
        efcm_ob_expected = m.ExpFactConceptMap.objects.filter(source__data_table=data_table_ob)[0]
        efcm_ob_assigned = nedm_ob.exp_fact_concept_maps.all()[0]

        self.assertEqual(efcm_ob_expected, efcm_ob_assigned)

    def test_assign_data_vals_to_table_super_complex(self):
        data_table_ob = m.DataTable.objects.filter(article__pmid='789')[0]
        assign_data_vals_to_table(data_table_ob)

        nedm_ob = m.NeuronEphysDataMap.objects.filter(source__data_table=data_table_ob)[0]
        nedm_dt_id = 'td-78'
        nedm_value = 128.6
        nedm_err = 1.07

        self.assertEqual(nedm_dt_id, nedm_ob.dt_id)
        self.assertEqual(nedm_value, nedm_ob.val)
        self.assertEqual(nedm_err, nedm_ob.err)

        nedm_ob = m.NeuronEphysDataMap.objects.filter(source__data_table=data_table_ob)[1]

        nedm_dt_id = 'td-95'
        nedm_value = 1.55
        nedm_err = .07
        self.assertEqual(nedm_dt_id, nedm_ob.dt_id)
        self.assertEqual(nedm_value, nedm_ob.val)
        self.assertEqual(nedm_err, nedm_ob.err)

        total_nedms = m.NeuronEphysDataMap.objects.filter(source__data_table=data_table_ob).count()
        self.assertEqual(total_nedms, 2)


if __name__ == '__main__':
    unittest.main()
