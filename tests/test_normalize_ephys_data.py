# -*- coding: utf-8 -*-

__author__ = 'shreejoy'

import unittest
import neuroelectro.models as m
from pint import UnitRegistry
from db_functions.normalize_ephys_data import check_data_val_range


# class NormalizeNedmTest(unittest.TestCase):


class DataRangeTest(unittest.TestCase):

    def test_check_data_val_range(self):
        ephys_prop = m.EphysProp.objects.create(name = 'input resistance')

        data_val = 100
        output_bool = check_data_val_range(data_val, ephys_prop)
        expected_bool = True
        self.assertEqual(output_bool, expected_bool)