# -*- coding: utf-8 -*-
# test_resolve_data_float.py

import unittest
from resolve_data_float import resolve_data_float, str_to_float

class TestStrToFloat(unittest.TestCase):
    
    def setUp(self):
        pass
    
    def test_str_to_float_1(self):
        self.assertEqual(str_to_float('23'), 23.0)
        
    def test_str_to_float_2(self):
        self.assertEqual(str_to_float('-23.34'), -23.34)
    
    def test_str_to_float_3(self):
        self.assertEqual(str_to_float('bb-23.34a'), -23.34)
    
    def test_str_to_float_4(self):
        self.assertIsNone(str_to_float('-a'))
        
class TestResolveDataFloat(unittest.TestCase):
    
    compare_dict = {'value' : -23., 'error': 12.45, 'numCells': 2, 'minRange': 21, 'maxRange': 35} 

    def test_resolve_1(self):
        output_dict = resolve_data_float(u'-23')
        self.assertEqual(output_dict['value'], TestResolveDataFloat.compare_dict['value'])
        
    def test_resolve_2(self):
        output_dict = resolve_data_float(u'-23 ± 12.45')
        
        test_keys = ['value', 'error']
        for k in test_keys:
            self.assertEqual(output_dict[k], TestResolveDataFloat.compare_dict[k])
        
    def test_resolve_3(self):
        output_dict = resolve_data_float(u'-23 ± 12.45 (2)')
        
        test_keys = ['value', 'error', 'numCells']
        for k in test_keys:
            self.assertEqual(output_dict[k], TestResolveDataFloat.compare_dict[k])
        
    def test_resolve_4(self):
        output_dict = resolve_data_float(u'21-35')
        
        test_keys = ['minRange', 'maxRange']
        for k in test_keys:
            self.assertEqual(output_dict[k], TestResolveDataFloat.compare_dict[k])


if __name__ == '__main__':
    unittest.main()