import numpy as np
import re

def resolve_data_float(data_str, initialize_dict = False):
    """Given an string containing numerical data, return a dictionary of text-mined assertions of
        mean value, error term, number of observations, and min and max range

    Args:
        data_str (str): string from a data table cell, corresponding to form
                    XX +/- YY (ZZ) where XX refers the mean value, YY is the error term, and ZZ reflects count
        initialize_dict (bool) : indicates whether dict keys should all be initialized with None values
    Returns:
        a dictionary of text-mined data attributes and their values

        example:
        {'value' : 46.5,
         'error' : 3.4,
         'numCells' : 5,
         'minRange', 20.4,
         'maxRange', 50.4,
        }

    """
    # TODO: consider adding an extracted SI unit as well

    key_list = ['value', 'error', 'numCells', 'minRange', 'maxRange']

    # initialize dict with None values if requested
    if initialize_dict :
        data_dict = dict.fromkeys(key_list)
    else:
        data_dict = {}

    # check if input string is mostly characters - then its probably not a data cont string
    if digit_pct(data_str) < .05:
        print 'Too many elems of string are not digits: %.2f' % digit_pct(data_str)
        print  data_str.encode("iso-8859-15", "replace")
        return data_dict
    
    # first map unicode negative values
    new_str = re.sub(u'\u2212', '-',data_str)
    new_str = re.sub(u'\u2013', '-', new_str)

    # look for string like '(XX)'
    num_obs_check = re.findall(u'\(\d+\)', new_str)
    if len(num_obs_check) > 0:
        num_obs_str = re.search('\d+', num_obs_check[0]).group()
        try:
            num_obs = int(num_obs_str)
            data_dict['numCells'] = num_obs
        except ValueError:
            pass

        #remove parens instances
        new_str = re.sub('\(\d+\)', '', new_str)

    #range_string_test = re.search('\d+(\s+)?-(\s+)?\d+',new_str)
    range_string_test = re.search('\([\d\.]+(\s+)?-(\s+)?[\d\.]+\)',new_str)
    if not range_string_test:
        range_string_test = re.search('[\d\.]+(\s+)?-(\s+)?[\d\.]+',new_str)
    if range_string_test
        range_split_list = re.split('-', new_str)
        print range_split_list
        min_range = str_to_float(range_split_list[0])
        max_range = str_to_float(range_split_list[1])

        if min_range and max_range:
            # check that min_range is less than max_range
            if min_range < max_range:
                data_dict['minRange'] = min_range
                data_dict['maxRange'] = max_range
                # prematurely assign a value as the mean of min and max ranges
                data_dict['value'] = np.mean([min_range, max_range])

    # try to split string based on unicode +/-
    split_str_list = re.split('\xb1', new_str)

    # try to split string based on +/-
    if len(split_str_list) == 1:
        split_str_list = re.split('\+\/\-', new_str)

    # parse 'mean' data value as first element
    value_str = split_str_list[0]
    value_float = str_to_float(value_str)
    if value_float:
        data_dict['value'] = value_float

    # parse 'error' value as second element after +/- sign
    if len(split_str_list) == 2:
        error_str = split_str_list[1]
        error_float = str_to_float(error_str)
        if error_float:
            # error_float must be greater than 0
            if error_float > 0:
                data_dict['error'] = error_float

    return data_dict


def str_to_float(in_str):
    """Converts an input string into a float
    Args:
        in_str (str): mostly santized string corresponding to numerical data of type XX.YY
    Returns:
        float or None, if string can't be parsed into a float or no numerical data found

    """
    matched_digits = re.search(u'[\-\+]?[\d\.]+', in_str)
    if matched_digits:
        try:
            digit_str = matched_digits.group()
            return float(digit_str)
        except ValueError:
            return None
    else:
        return None


def digit_pct(in_str):
    """Returns the fraction of digits in the input string"""
    digit_search = re.findall('\d', in_str)
    num_digits = len(digit_search)
    if num_digits == 0:
        return 0.0
    tot_chars = max(len(in_str.encode("iso-8859-15", "replace")),1)
    fract_digits = float(num_digits)/tot_chars
    return fract_digits