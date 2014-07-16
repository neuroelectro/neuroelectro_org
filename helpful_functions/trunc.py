'''
Created on Jul 16, 2014

@author: stripathy
'''
def trunc(f, n=3):
    '''Truncates/pads a float f to n decimal places without rounding'''
    slen = len('%.*f' % (n, f))
    return float(str(f)[:slen])