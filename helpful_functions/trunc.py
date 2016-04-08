'''
Created on Jul 16, 2014

@author: stripathy
'''

# copied shamelessly from this StackOverflow answer: http://stackoverflow.com/questions/783897/truncating-floats-in-python/783927
def trunc(f, n=3):
    '''Truncates/pads a float f to n decimal places without rounding'''
    s = '{}'.format(f)
    if 'e' in s or 'E' in s:
        return '{0:.{1}f}'.format(f, n)
    i, p, d = s.partition('.')
    return float('.'.join([i, (d+'0'*n)[:n]]))
