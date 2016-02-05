import re
import nltk
import pandas as pd
import neuroelectro.models as m
from pint import UnitRegistry, UndefinedUnitError
from article_text_mining.mine_ephys_prop_in_table import get_units_from_table_header
from article_text_mining.unit_conversion import convert_units

__author__ = 'shreejoy'


def normalize_nedm_val(nedm, range_check = True):
    """Normalize the data within neuroelectro.models NeuronEphysDataMap to standard units and range
    """
    data_mean_value = nedm.val
    data_err_value = nedm.err

    # initialize output dictionary
    key_list = ['value', 'error']
    output_dict = dict.fromkeys(key_list)

    unit_reg = UnitRegistry()
    ecm = nedm.ephys_concept_map
    ephys_prop = nedm.ephys_concept_map.ephys_prop
    natural_unit = unicode(ephys_prop.units)

    # try to get unit from table header, if can't, assume unit is natural unit
    found_unit = ecm.identified_unit
    if found_unit is None:
        found_unit = get_units_from_table_header(ecm.ref_text)
    if found_unit is None:
        found_unit = natural_unit

    # normalize mean value
    conv_mean_value = convert_units(found_unit, natural_unit, data_mean_value)
    if conv_mean_value:
        # custom normalization for voltage and ratio values
        conv_mean_value = convert_voltage_value(conv_mean_value, ephys_prop)
        conv_mean_value = convert_percent_to_ratio(conv_mean_value, ephys_prop, ecm.ref_text)

        # check whether mean value in appropriate range
        if range_check:
            if not check_data_val_range(conv_mean_value, ephys_prop):
                print 'neuron ephys data map %s out of appropriate range' % data_mean_value, conv_mean_value, ephys_prop
                conv_mean_value = None
        output_dict['value'] = conv_mean_value

    # normalize error term
    # TODO: address if errors represented as standard deviations

    if data_err_value:
        conv_err_value = convert_units(found_unit, natural_unit, data_err_value)
        if conv_err_value:
            conv_err_value = convert_percent_to_ratio(conv_err_value, ephys_prop, ecm.ref_text)
            #print 'reported err val: %s, norm err val: %s' % (nedm.err, conv_err_value)

            # really basic check for error term validity
            if conv_err_value < 0:
                conv_err_value = None
            output_dict['error'] = conv_err_value

    return output_dict

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
        'spike threshold' : (-100, -5),
        'input resistance' : (1, 20000),
        'cell capacitance' : (1, 10000),
        'rheobase' : (1, 10000),
        'spike width' : (.01, 20),
        'spike half-width' : (.01, 10),
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


def convert_voltage_value(data_value, ephys_prop):
    """Convert a voltage value if it's missing a minus sign"""
    ephys_prop_name = ephys_prop.name
    voltage_prop_list = ['resting membrane potential', 'spike threshold', 'AHP amplitude', 'fast AHP amplitude',
                         'medium AHP amplitude', 'slow AHP amplitude']
    if ephys_prop_name in voltage_prop_list:
        if not check_data_val_range(data_value, ephys_prop):
            converted_value = -data_value
            return converted_value
    return data_value


def convert_percent_to_ratio(data_value, ephys_prop, ecm_ref_text):
    """Convert a percentage value to a ratio"""

    # TODO deal with ratio percentage issue
    ephys_prop_name = ephys_prop.name
    if ephys_prop_name == 'sag ratio' or ephys_prop_name == 'adaptation ratio':
        ref_text = ecm_ref_text
        rep_val = data_value
        toks = nltk.word_tokenize(ref_text)
        not_match_flag = 0
        conv_value = data_value
        for tok in toks:
            if tok == '%':
                print '%', ref_text
                not_match_flag = 1
                conv_value = rep_val/100.0
                break
            elif rep_val > 2 and rep_val < 200:
                conv_value = rep_val/100.0
                break
            elif rep_val > 2 and rep_val < 0:
                conv_value = rep_val/100.0
                break
        return conv_value
    else:
        return data_value


def identify_stdev(nedm_list):
    """Identifies whether error term for nedm list are standard deviations"""

    mean_list = [nedm.val_norm for nedm in nedm_list]
    err_list = [nedm.err_norm for nedm in nedm_list]

    sd_ratio = .15 # ratio of mean to error above which a SD is assumed
    fract_greater = .5 # fraction of many nedms need to have a higher error than expected?

    df = pd.DataFrame()
    df['means'] = mean_list
    df['errs'] = err_list

    greater_count = sum(df['errs'] / df['means'] > sd_ratio)
    total_count = df['errs'].count()

    if float(greater_count) / total_count > fract_greater:
        return True
    else:
        return False