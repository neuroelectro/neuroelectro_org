# -*- coding: utf-8 -*-
__author__ = 'stripathy'

# test_resolve_data_float.py

import unittest
from article_text_mining.resolve_data_float import resolve_data_float, str_to_float


class DataStringParsingTest(unittest.TestCase):

    def test_str_to_float_simple(self):
        self.assertEqual(str_to_float('-23.34'), -23.34)

    def test_str_to_float_messy(self):
        self.assertEqual(str_to_float('bb-23.34***'), -23.34)

    def test_str_to_float_unparsable_input(self):
        self.assertIsNone(str_to_float('-a'))


class DataStringToDictTest(unittest.TestCase):

    compare_dict = {'value' : -23, 'error': 12.45, 'num_obs': 2, 'min_range': 21, 'max_range': 35}

    def test_mean_only(self):
        output_dict = resolve_data_float(u'-23')
        self.assertEqual(output_dict['value'], DataStringToDictTest.compare_dict['value'])

    def test_mean_plus_error(self):
        output_dict = resolve_data_float(u'-23 +/- 12.45')

        test_keys = ['value', 'error']
        for k in test_keys:
            self.assertEqual(output_dict[k], DataStringToDictTest.compare_dict[k])

    def test_mean_plus_error_plus_n(self):
        output_dict = resolve_data_float(u'-23 ± 12.45 (2)')

        test_keys = ['value', 'error', 'num_obs']
        for k in test_keys:
            self.assertEqual(output_dict[k], DataStringToDictTest.compare_dict[k])

    def test_data_range(self):
        output_dict = resolve_data_float(u'21-35')

        test_keys = ['min_range', 'max_range']
        for k in test_keys:
            self.assertEqual(output_dict[k], DataStringToDictTest.compare_dict[k])

    def test_data_mean_plus_range(self):
        output_dict = resolve_data_float(u'-23 (21-35)')

        test_keys = ['value', 'min_range', 'max_range']
        for k in test_keys:
            self.assertEqual(output_dict[k], DataStringToDictTest.compare_dict[k])
            
    def test_data_range_plus_error_plus_n(self):
        output_dict = resolve_data_float(u'21-35 +/- 12.45 (2)')

        test_keys = ['value', 'min_range', 'max_range', "num_obs", 'error']
        final_dict = DataStringToDictTest.compare_dict.copy()
        final_dict['value'] = (final_dict['min_range'] + final_dict['max_range']) / 2
        for k in test_keys:
            self.assertEqual(output_dict[k], final_dict[k])
            
    def test_range_swap(self):
        output_dict = resolve_data_float(u'\n     (35-21) ± 12.45(N  =2)')

        test_keys = ['value', 'min_range', 'max_range', "num_obs", 'error']
        final_dict = DataStringToDictTest.compare_dict.copy()
        final_dict['value'] = (final_dict['min_range'] + final_dict['max_range']) / 2
        for k in test_keys:
            self.assertEqual(output_dict[k], final_dict[k])
            
    def test_no_digit_before_decimal(self):
        output_dict = resolve_data_float(u'.12 ± .0045 (n2)')

        test_keys = ['value', "num_obs", 'error']
        final_dict = DataStringToDictTest.compare_dict.copy()
        final_dict['value'] = 0.12
        final_dict['error'] = 0.0045
        for k in test_keys:
            self.assertEqual(output_dict[k], final_dict[k])
            
if __name__ == '__main__':
    unittest.main()
