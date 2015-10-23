import numpy as np
import re

def resolve_data_float(data_str, initialize_dict = False):
    """Given a string containing numerical data, return a dictionary of text-mined assertions of
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
         'num_obs' : 5,
         'min_range', 20.4,
         'max_range', 50.4,
        }

    """
    # TODO: consider adding an extracted SI unit as well

    key_list = ['value', 'error', 'num_obs', 'min_range', 'max_range']

    # initialize dict with None values if requested
    if initialize_dict :
        data_dict = dict.fromkeys(key_list)
    else:
        data_dict = {}

    # check if input string is mostly characters - then its probably not a data cont string
    if digit_pct(data_str) < .05:
        print 'Too many elems of string %s are not digits: %.2f' % (data_str.encode("iso-8859-15", "replace"), digit_pct(data_str))
        return data_dict
    
    # first map unicode negative values
    new_str = re.sub(u'\u2212', '-', data_str)
    new_str = re.sub(u'\u2013', '-', new_str)
    new_str = re.sub(u'\+/-', u'\xb1',  new_str)
    new_str = re.sub(u'\+\\-', u'\xb1',  new_str)
    
    # remove whitespace from the data string as it serves no purpose
    new_str = re.sub('\s', '', new_str)

    # look for string like '(XX)'
    num_obs_check = re.findall(u'\([Nn]?=?\d+\)', new_str)
    if len(num_obs_check) > 0:
        data_dict['num_obs'] = int(re.search('\d+', num_obs_check[0]).group(0))

        # remove number of observations instance from the string
        new_str = new_str.replace(num_obs_check[0], '')
    
    # try to split string based on unicode +/-
    split_str_list = re.split('\xb1', new_str) if re.search('\xb1', new_str) else re.split('\+/-', new_str)

    # parse 'error' value as second element after +/- sign
    if len(split_str_list) == 2:
        error_float = str_to_float(split_str_list[1])
        
        # error_float must be greater than 0
        if error_float and error_float > 0:
            data_dict['error'] = error_float
        
        # remove the part of the string defined as error
        new_str = split_str_list[0]

    # Check the remaining string for range (it has to start with a range)
    range_str_check = re.search(r'-?\.?\d+\.?\d*--?\.?\d+\.?\d*', new_str)
    if range_str_check:
        range_str = range_str_check.group(0)
        minus_count = len(re.findall('-', range_str))
        range_split_list = re.split('-', range_str)
        
        if minus_count == 1:
            min_range = str_to_float(range_split_list[0])
            max_range = str_to_float(range_split_list[1])
        elif minus_count == 2:
            if re.search('^\-', range_str):
                min_range = str_to_float("-" + range_split_list[1])
                max_range = str_to_float(range_split_list[2])
            else:
                min_range = str_to_float(range_split_list[0])
                max_range = str_to_float("-" + range_split_list[2])
        elif minus_count == 3:
            min_range = str_to_float("-" + range_split_list[1])
            max_range = str_to_float("-" + range_split_list[3])
        else:
            print "Unparsable data range detected in String: '" + range_str + "'. Too many '-' signs."
            
        if min_range and max_range:
            if min_range < max_range:
                data_dict['min_range'] = min_range
                data_dict['max_range'] = max_range
            else:
                data_dict['min_range'] = max_range
                data_dict['max_range'] = min_range

            # prematurely assign a value as the mean of min and max ranges
            data_dict['value'] = np.mean([min_range, max_range])
            new_str = re.sub(range_str, "", new_str)

    # parse 'mean' data value as first element
    new_str = re.search(r'-?\.?\d+\.?\d*', new_str)
    if new_str:
        data_dict['value'] = str_to_float(new_str.group(0))

    return data_dict

def str_to_float(in_str):
    """Converts an input string into a float
    Args:
        in_str (str): mostly santized string corresponding to numerical data of type XX.YY
    Returns:
        first found float or None, if string can't be parsed into a float or no numerical data found

    """
    in_str = re.sub('\s', '', in_str)
    # This matches just '-' alone, figure out a way to enforce at least 1 digit somewhere in the string.
    matched_digits = re.search(r'-?\.?\d+\.?\d*', in_str)
    if matched_digits:
        try:
            return (float)(matched_digits.group(0))
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