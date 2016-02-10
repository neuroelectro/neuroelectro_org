# -*- coding: utf-8 -*-

import re
from pint import UnitRegistry, UndefinedUnitError, DimensionalityError

__author__ = 'shreejoy'


def parse_units_from_str(input_str):
    """Matches an input string to the closest matching scientific unit using Pint Package
    """
    unit_reg = UnitRegistry()
    
    if input_str:
        cleaned_str = re.sub('\*', '', input_str)
        cleaned_str = re.sub(u'μ', 'u', cleaned_str) # weird issue with Pint Package choking on mu signs
        cleaned_str = re.sub(u'Ω', 'ohm', cleaned_str) # weird issue with Pint Package choking on Omega signs
        cleaned_str = re.sub(u'\u2126', 'ohm', cleaned_str) # converting unicode sign for Omega
        cleaned_str = re.sub(u'\u03a9', 'ohm', cleaned_str) # converting unicode sign for Omega
        cleaned_str = re.sub(u'mohm', 'Mohm', cleaned_str) # deals with mOhm not being MOhm
        cleaned_str = re.sub('\%', 'ratio', cleaned_str) # weird issue with Pint Package choking on percent signs
        cleaned_str = re.sub('\s+', '', cleaned_str) # removing all whitespace in string
        # TODO: make below code more robust
        # check whether last character in string is capital M, if so assume it means mole
        if input_str[-1] == 'M':
            cleaned_str = re.sub(r'(\w)+M$', 'mole', cleaned_str) # adding M as synonym for mole

        try:
            matched_unit = unit_reg.parse_expression(cleaned_str)
            if hasattr(matched_unit, 'units'):
                return input_str, matched_unit
        except UndefinedUnitError:
            #print u'UndefinedUnitError during unit parsing : %s' % cleaned_str
            return None
        except AttributeError:
            #print u'Attribute Error during unit parsing : %s' % cleaned_str
            return None
        except Exception:
            #print u'unit parsing failed for some unexplained reason: %s' % cleaned_str
            return None
    else:
        return None

def convert_units(from_unit_str, to_units_str, value):
    """Perfoms unit conversion"""

    if from_unit_str == to_units_str:
        return value

    from_units = parse_units_from_str(from_unit_str)
    to_units = parse_units_from_str(to_units_str)

    if from_units and to_units:
        try:
            conversion_factor = from_units[1].to(to_units[1].units)
            converted_value = conversion_factor * value

            return converted_value.magnitude
        except DimensionalityError:
            print u'unable to convert units from %s to %s' % (from_unit_str.encode('ascii', 'ignore') ,
                                                              to_units_str.encode('ascii', 'ignore') )
            return None
    else:
        return None


