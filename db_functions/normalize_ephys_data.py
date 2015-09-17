import re
import nltk
import neuroelectro.models as m
from pint import UnitRegistry, UndefinedUnitError
from article_text_mining.mine_ephys_prop_in_table import get_units_from_table_header
from article_text_mining.unit_conversion import convert_units

__author__ = 'shreejoy'


def normalize_nedm_val(nedm):
    """Normalize the data within neuroelectro.models NeuronEphysDataMap to standard units and range
    """
    unit_reg = UnitRegistry()
    ecm = nedm.ephys_concept_map
    natural_unit = unicode(ecm.ephys_prop.units)

    # try to get unit from table header, if can't, assume unit is natural unit
    found_unit = get_units_from_table_header(ecm.ref_text)
    if found_unit is None:
        found_unit = natural_unit

    data_value = nedm.val
    converted_value = convert_units(found_unit, natural_unit, data_value)

    data_value = nedm.val
    ephys_prop_name = nedm.ephys_concept_map.ephys_prop.name
    if ephys_prop_name == 'resting membrane potential' or nedm.ephys_concept_map.ephys_prop.name == 'spike threshold':
        if not check_data_val_range(converted_value, ephys_prop):
            converted_value = -nedm.val
            if not check_data_val_range(converted_value, ephys_prop):
                return None
    # TODO deal with ratio percentage issue
    # elif ephys_prop_name == 'spike half-width':
    #     if data_value > 10 and data_value < 100:
    #         return None
    #     if data_value >= 100:
    #         data_value = data_value/1000;
    # elif ephys_prop_name == 'input resistance':
    #     if data_value < 2:
    #         data_value = data_value * 1000;
    # elif ephys_prop_name == 'spike width':
    #     if data_value > 20:
    #         return None
    # elif nedm.ephys_concept_map.ephys_prop.name == 'spike amplitude' or nedm.ephys_concept_map.ephys_prop.name == 'membrane time constant'\
    #     or nedm.ephys_concept_map.ephys_prop.name == 'spike width':
    #         if re.search(r'psp', nedm.source.data_table.table_text, re.IGNORECASE) != None \
    #         or re.search(r'psc', nedm.source.data_table.table_text, re.IGNORECASE) != None \
    #         and nedm.times_validated == 0:
    #             #print nedm.data_table.table_text
    #             return None
    elif ephys_prop_name == 'sag ratio' or ephys_prop_name == 'adaptation ratio':
        ref_text = nedm.ephys_concept_map.ref_text
        toks = nltk.word_tokenize(ref_text)
        not_match_flag = 0
        for tok in toks:
            if tok == '%':
                rep_val = nedm.val
                print '%', ref_text
                not_match_flag = 1
                data_value = rep_val/100.0
                break
    # elif ephys_prop_name == 'cell capacitance':
    #     ref_text = nedm.ephys_concept_map.ref_text
    #     toks = nltk.word_tokenize(ref_text)
    #     not_match_flag = 0
    #     for tok in toks:
    #         if tok.lower() == 'pf':
    #             data_value = data_value
    #             break
    #         elif tok.lower() == 'nf':
    #             rep_val = nedm.val
    #             not_match_flag = 1
    #             data_value = rep_val*1000
    #             break
    # elif ephys_prop_name == 'rheobase':
    #     ref_text = nedm.ephys_concept_map.ref_text
    #     toks = nltk.word_tokenize(ref_text)
    #     not_match_flag = 0
    #     for tok in toks:
    #         if tok.lower() == 'pa':
    #             data_value = data_value
    #             break
    #         elif tok.lower() == 'na':
    #             rep_val = nedm.val
    #             not_match_flag = 1
    #             data_value = rep_val*1000
    #             break
    return converted_value

def check_data_val_range(data_value, ephys_prop):
    """Assesses whether data value is in an appropriate range given the property type

    Args:
        data_value (float): the data value to be checked, in natural units of the ephys property
        ephys_prop (neuroelectro.models EphysProp object): ephys property of the data_value

    Returns:
        Boolean if data_value in appropriate range
    """
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

    }
    if ephys_prop.name in ephys_prop_range_dict:
        low_range, high_range = ephys_prop_range_dict[ephys_prop.name]
        if data_value > low_range and data_value < high_range:
            return True
        else:
            return False
    else:
        return True
