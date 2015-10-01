# -*- coding: utf-8 -*-

import re
from pint import UnitRegistry, UndefinedUnitError

__author__ = 'shreejoy'


def parse_units_from_str(input_str):
    """Matches an input string to the closest matching scientific unit using Pint Package
    """
    unit_reg = UnitRegistry()

    if input_str:
        cleaned_str = re.sub('\*', '', input_str)
        cleaned_str = re.sub('μ', 'u', cleaned_str) # weird issue with Pint Package choking on mu signs
        cleaned_str = re.sub(u'Ω', 'Ohm', cleaned_str) # weird issue with Pint Package choking on Omega signs
        cleaned_str = re.sub('\%', 'ratio', cleaned_str) # weird issue with Pint Package choking on percent signs
        try:
            matched_unit = unit_reg.parse_expression(cleaned_str)
            if hasattr(matched_unit, 'u'):
                return input_str, matched_unit
        except UndefinedUnitError:
            return None
        except AttributeError:
            print u'Attribute Error during unit parsing : %s' % cleaned_str
            return None
        except Exception:
            print 'unit parsing failed for some unexplained reason: %s' % cleaned_str
            return None
    else:
        return None

def convert_units(from_unit_str, to_units_str, value):
    """Perfoms unit conversion"""

    if from_unit_str == to_units_str:
        return value

    from_units = parse_units_from_str(from_unit_str)
    to_units = parse_units_from_str(to_units_str)
    # unit_reg = UnitRegistry()
    # Q_ = unit_reg.Quantity

    if from_units and to_units:
        conversion_factor = from_units[1].to(to_units[1])
        converted_value = conversion_factor * value

        return converted_value.magnitude
    else:
        return None


