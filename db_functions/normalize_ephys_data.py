import re
import nltk
import neuroelectro.models as m
from pint import UnitRegistry, UndefinedUnitError
from article_text_mining.mine_ephys_prop_in_table import get_units_from_table_header
from article_text_mining.unit_conversion import convert_units

__author__ = 'shreejoy'


def normalize_nedm_val(nedm, range_check = True):
    """Normalize the data within neuroelectro.models NeuronEphysDataMap to standard units and range
    """
    unit_reg = UnitRegistry()
    ecm = nedm.ephys_concept_map
    natural_unit = unicode(ecm.ephys_prop.units)

    # try to get unit from table header, if can't, assume unit is natural unit
    found_unit = ecm.identified_unit
    if found_unit is None:
        found_unit = get_units_from_table_header(ecm.ref_text)
    if found_unit is None:
        found_unit = natural_unit

    data_value = nedm.val
    converted_value = convert_units(found_unit, natural_unit, data_value)

    ephys_prop = nedm.ephys_concept_map.ephys_prop
    ephys_prop_name = ephys_prop.name
    voltage_prop_list = ['resting membrane potential', 'spike threshold', 'AHP amplitude', 'fast AHP amplitude',
                         'medium AHP amplitude', 'slow AHP amplitude']
    if ephys_prop_name in voltage_prop_list:
        if not check_data_val_range(converted_value, ephys_prop):
            converted_value = -nedm.val

    # TODO deal with ratio percentage issue
    elif ephys_prop_name == 'sag ratio' or ephys_prop_name == 'adaptation ratio':
        ref_text = nedm.ephys_concept_map.ref_text
        rep_val = nedm.val
        toks = nltk.word_tokenize(ref_text)
        not_match_flag = 0
        for tok in toks:
            if tok == '%':
                print '%', ref_text
                not_match_flag = 1
                converted_value = rep_val/100.0
                break
            elif rep_val > 2 and rep_val < 200:
                converted_value = rep_val/100.0
                break
            elif rep_val > 2 and rep_val < 0:
                converted_value = rep_val/100.0
                break
    if range_check:
        if not check_data_val_range(converted_value, ephys_prop):
            print 'neuron ephys data map %s out of appropriate range' % data_value, ephys_prop
            return None
    return converted_value

def check_data_val_range(data_value, ephys_prop):
    """Assesses whether data value is in an appropriate range given the property type

    Args:
        data_value (float): the data value to be checked, in natural units of the ephys property
        ephys_prop (neuroelectro.models EphysProp object): ephys property of the data_value

    Returns:
        Boolean if data_value in appropriate range
    """

    # TODO: ideally these should be stored in the database directly
    ephys_prop_range_dict = {
        'resting membrane potential' : (-150, -20),
        'spike threshold' : (-100, 10),
        'input resistance' : (0, 20000),
        'cell capacitance' : (0, 10000),
        'rheobase' : (0, 10000),
        'spike width' : (0, 20),
        'spike half-width' : (0, 10),
        'sag ratio': (-1, 2),
        'adaptation ratio': (-1, 2),
        'fast AHP amplitude': (0, 50),
        'AHP amplitude': (0, 50),
        'medium AHP amplitude': (0, 50),
        'slow AHP amplitude': (0, 50),
        'AHP duration': (0, 100000),
        'fast AHP duration': (0, 100000),
        'slow AHP duration': (0, 100000),

    }
    if ephys_prop.name in ephys_prop_range_dict:
        low_range, high_range = ephys_prop_range_dict[ephys_prop.name]
        if data_value > low_range and data_value < high_range:
            return True
        else:
            return False
    else:
        return True


# def check_all_nedms():
#     """Goes through all validated nedms and checks whether they get normalized correctly"""
#
#     nedms = m.NeuronEphysDataMap.objects.filter(neuron_concept_map__times_validated__gte = 1)
#     for nedm in nedms:
#         pass
