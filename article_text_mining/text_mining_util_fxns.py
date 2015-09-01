# -*- coding: utf-8 -*-
import re

__author__ = 'stripathy'


def get_tag_text(data_table_cell_tag):
    """Returns a sanitized string of a data table cell's content

    Args:
        data_table_cell_tag (beautiful soup object): the html tag corresponding to a data_table_cell

    Returns:
        string of the text contained in the cell

    """
    if data_table_cell_tag is None:
        return u''
    tag_text = u''.join(data_table_cell_tag.findAll(text=True))
    if tag_text is '':
        tag_text = u'    '
    tag_text = tag_text.replace('\s', u' ')
    return tag_text


def parens_resolver(in_str):
    """Checks for parenthesis within input string and returns string without parens and within-parens string

    Args:
        in_str: the string to be matched
        matching_list: the list of strings that you want matched against, typically a list of synonyms

    Returns:
        string 1 : the string without the term inside the parentheses
        string 2: the string inside the parens (if there is one)

    Examples:
        >>> print parens_resolver('23 (45)')
        ('23', '45')
    """
    parens_check = re.findall(u'\(.+\)', in_str)
    inside_parens = None
    if len(parens_check) > 0:
        inside_parens = parens_check[0].strip('()')
    new_str = re.sub(u'\(.+\)', '', in_str)
    return new_str.strip(), inside_parens


def comma_resolver(in_str):
    """Checks for a comma within input string and returns string to left and right of comma

    Args:
        in_str: the string to be matched

    Returns:
        string 1 : the string to the left of the comma (or original string if no comma)
        string 2: the string to the right of the comma (or None if no comma)

    Examples:
        >>> print comma_resolver('23, 45')
        ('23', '45')

        >>> print comma_resolver('RMP, mV')
        ('RMP', 'mV')
    """
    comma_check = in_str.split(',')
    new_str = comma_check[0]
    right_str = None
    if len(comma_check) > 1:
        right_str = comma_check[1].strip()
    return new_str.strip(), right_str