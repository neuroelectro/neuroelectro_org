# -*- coding: utf-8 -*-

__author__ = 'shreejoy'

import unittest
from pint import UnitRegistry, UndefinedUnitError
from article_text_mining.unit_conversion import parse_units_from_str, convert_units

class GetUnitsFromStringTest(unittest.TestCase):

    def check_millivolt_parsing_from_string(self):
        unit_reg = UnitRegistry()
        expected_unit = unit_reg.millivolt

        input_str = 'mV'
        output_str, found_unit = parse_units_from_str(input_str)
        self.assertEqual(found_unit, expected_unit)

    def check_megaohm_parsing_from_string(self):
        unit_reg = UnitRegistry()
        expected_unit = unit_reg.megaohm

        input_str = 'MΩ'
        output_str, found_unit = parse_units_from_str(input_str)
        self.assertEqual(found_unit, expected_unit)


class UnitConversionTest(unittest.TestCase):

    def test_unit_conversion(self):

        input_unit = 'MOhm'
        desired_unit = 'GOhm'

        converted_value = convert_units(input_unit, desired_unit, 23)
        expected_converted_value = .023

        self.assertEqual(expected_converted_value, converted_value)

if __name__ == '__main__':
    unittest.main()