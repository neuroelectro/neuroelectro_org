# -*- coding: utf-8 -*-

__author__ = 'shreejoy'

import unittest
from pint import UnitRegistry
from article_text_mining.unit_conversion import parse_units_from_str, convert_units


class ParseUnitTest(unittest.TestCase):

    def test_millivolt_parsing(self):
        unit_reg = UnitRegistry()
        expected_unit = unit_reg.millivolt

        input_str = 'mV'
        output_str, found_unit = parse_units_from_str(input_str)
        self.assertEqual(found_unit, expected_unit)

    def test_megaohm_parsing(self):
        unit_reg = UnitRegistry()
        expected_unit = unit_reg.megaohm

        input_str = u'MΩ'
        output_str, found_unit = parse_units_from_str(input_str)
        self.assertEqual(found_unit, expected_unit)

    def test_weird_unit_parsing(self):
        unit_reg = UnitRegistry()
        expected_unit = unit_reg.megaohm

        input_str = u'mV ms\u22121'
        found_unit = parse_units_from_str(input_str)
        self.assertIsNone(found_unit)


class UnitConversionTest(unittest.TestCase):

    def test_unit_conversion(self):

        input_unit = u'nA'
        desired_unit = u'pA'

        converted_value = convert_units(input_unit, desired_unit, 23)
        expected_converted_value = 23000

        self.assertAlmostEqual(expected_converted_value, converted_value)

if __name__ == '__main__':
    unittest.main()