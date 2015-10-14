# -*- coding: utf-8 -*-

__author__ = 'shreejoy'

import unittest
from article_text_mining.rep_html_table_struct import rep_html_table_struct


class RepTableStructureTest(unittest.TestCase):

    @property
    def load_html_table_simple(self):
        # creates data table object 16055 with some dummy data
        with open('tests/test_html_data_tables/example_html_table_simple.html', mode='rb') as f:
            simple_table_text = f.read()
        return simple_table_text

    @property
    def load_html_table_complex(self):
        with open('tests/test_html_data_tables/example_html_table_complex.html', mode='rb') as f:
            complex_table_text = f.read()
        return complex_table_text

    def test_rep_html_table_struct_simple(self):
        expected_table_output = [['th-1', 'th-2', 'th-3', 'th-4', 'th-5', 'th-6'],
                                 ['td-1', 'td-1', 'td-1', 'td-1', 'td-1', 'td-1'],
                                 ['td-2', 'td-3', 'td-4', 'td-5', 'td-6', 'td-7'],
                                 ['td-8', 'td-9', 'td-10', 'td-11', 'td-12', 'td-13'],
                                 ['td-14', 'td-15', 'td-16', 'td-17', 'td-18', 'td-19'],
                                 ['td-20', 'td-21', 'td-22', 'td-23', 'td-24', 'td-25'],
                                 ['td-26', 'td-27', 'td-28', 'td-29', 'td-30', 'td-31'],
                                 ['td-32', 'td-33', 'td-34', 'td-35', 'td-36', 'td-37'],
                                 ['td-38', 'td-39', 'td-40', 'td-41', 'td-42', 'td-43'],
                                 ['td-44', 'td-45', 'td-46', 'td-47', 'td-48', 'td-49'],
                                 ['td-50', 'td-51', 'td-52', 'td-53', 'td-54', 'td-55'],
                                 ['td-56', 'td-57', 'td-58', 'td-59', 'td-60', 'td-61'],
                                 ['td-62', 'td-63', 'td-64', 'td-65', 'td-66', 'td-67'],
                                 ['td-68', 'td-69', 'td-70', 'td-71', 'td-72', 'td-73'],
                                 ['td-74', 'td-75', 'td-76', 'td-77', 'td-78', 'td-79'],
                                 ['td-80', 'td-81', 'td-82', 'td-83', 'td-84', 'td-85'],
                                 ['td-86', 'td-87', 'td-88', 'td-89', 'td-90', 'td-91'],
                                 ['td-92', 'td-93', 'td-94', 'td-95', 'td-96', 'td-97'],
                                 ['td-98', 'td-99', 'td-100', 'td-101', 'td-102', 'td-103'],
                                 ['td-104', 'td-105', 'td-106', 'td-107', 'td-108', 'td-109']]
        html_table_text = self.load_html_table_simple
        a, b, html_id_table = rep_html_table_struct(html_table_text)
        self.assertEqual(html_id_table, expected_table_output)

    def test_rep_html_table_struct_complex(self):
        expected_table_output = [['td-1', 0, 0, 0, 0, 0, 0, 0, 0, 0],
                                  ['td-2', 'td-2', 'td-2', 'td-2', 'td-2', 'td-2', 'td-2', 'td-2', 'td-2', 'td-2'],
                                  ['td-3', 'td-4', 'td-4', 'td-5', 'td-5', 'td-6', 'td-6', 0, 0, 0],
                                  ['td-3', 'td-7', 'td-8', 'td-9', 'td-10', 'td-11', 'td-12', 0, 0, 0],
                                  ['td-13', 'td-13', 'td-13', 'td-13', 'td-13', 'td-13', 'td-13', 'td-13', 'td-13', 'td-13'],
                                  ['td-14', 'td-15', 'td-16', 'td-17', 'td-18', 'td-19', 'td-20', 0, 0, 0],
                                  ['td-21', 'td-22', 'td-23', 'td-24', 'td-25', 'td-26', 'td-27', 0, 0, 0],
                                  ['td-28', 'td-29', 'td-30', 'td-31', 'td-32', 'td-33', 'td-34', 0, 0, 0],
                                  ['td-35', 'td-36', 'td-37', 'td-38', 'td-39', 'td-40', 'td-41', 0, 0, 0],
                                  ['td-42', 'td-43', 'td-44', 'td-45', 'td-46', 'td-47', 'td-48', 0, 0, 0],
                                  ['td-49', 'td-50', 'td-51', 'td-52', 'td-53', 'td-54', 'td-55', 0, 0, 0],
                                  ['td-56', 'td-57', 'td-58', 'td-59', 'td-60', 'td-61', 'td-62', 0, 0, 0],
                                  ['td-63', 'td-64', 'td-65', 'td-66', 'td-67', 'td-68', 'td-69', 0, 0, 0],
                                  ['td-70', 'td-71', 'td-72', 'td-73', 'td-74', 'td-75', 'td-76', 0, 0, 0],
                                  ['td-77', 'td-78', 'td-79', 'td-80', 'td-81', 'td-82', 'td-83', 0, 0, 0]]
        html_table_text = self.load_html_table_complex
        a, b, html_id_table = rep_html_table_struct(html_table_text)
        self.assertEqual(html_id_table, expected_table_output)


if __name__ == '__main__':
    unittest.main()