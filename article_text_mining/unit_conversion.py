import re
from pint import UnitRegistry, UndefinedUnitError

__author__ = 'shreejoy'


def match_units_from_str(input_str):
    """Matches an input string to the closest matching scientific unit using Pint Package
    """
    unit_reg = UnitRegistry()

    if input_str:
        cleaned_str = re.sub('\*', '', input_str)
        cleaned_str = re.sub('μ', 'u', cleaned_str) # weird issue with Pint Package choking on mu signs
        cleaned_str = re.sub('\%', 'ratio', cleaned_str) # weird issue with Pint Package choking on percent signs
        try:
            matched_unit = unit_reg.parse_expression(cleaned_str)
            if hasattr(matched_unit, 'u'):
                return input_str, matched_unit
        except UndefinedUnitError:
            return None
        except AttributeError:
            print u'Attribute Error during unit conversion : %s' % cleaned_str
            return None
        except Exception:
            print 'unit conversion failed for some unexplained reason: %s' % cleaned_str
            return None
    else:
        return None