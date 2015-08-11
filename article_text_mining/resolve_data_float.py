import numpy as np
import re

# Resolves an ephys value entry given as String into a map of 'value', 'error' and 'numCells'
#
# value is the mean of the given ephys value range
# error is the given error
# numCells is the number of iterations of the experiment which was used to determine this ephys value
def resolve_data_float(inStr):
    retDict = {}
    # check if input string is mostly characters - then its probably not a data cont string
    if digit_pct(inStr) < .05:
        print 'Too many elems of string are not digits: %.2f' % digit_pct(inStr)
        print  inStr.encode("iso-8859-15", "replace")
        return retDict
    
    # first map unicode negative values
    #print unicodeToIso(newStr)
    newStr = re.sub(u'\u2212', '-',inStr)
    newStr = re.sub(u'\u2013', '-', newStr)
    #print unicodeToIso(newStr)
    # look for string like '(XX)'    
    numCellsCheck = re.findall(u'\(\d+\)', newStr)
    if len(numCellsCheck) > 0:
        numCellsStr = re.search('\d+', numCellsCheck[0]).group()
        try:
            numCells = int(numCellsStr)
            retDict['numCells'] = numCells
        except ValueError:
            pass
    #remove parens instances
    newStr = re.sub('\(\d+\)', '', newStr)
    # try to split string based on +\-
    
    # TODO: checking for floats in ranges?
    rangeTest = re.search('\d+(\s+)?-(\s+)?\d+',newStr)
    if rangeTest:
        rangeSplitList = re.split('-', newStr)
        minRange = get_digits(rangeSplitList[0])
        maxRange = get_digits(rangeSplitList[1])
        if minRange is None or maxRange is None:
            return retDict
        else:
            retDict['minRange'] = minRange
            retDict['maxRange'] = maxRange
            retDict['value'] = np.mean([minRange, maxRange])
            #return retDict
    splitStrList = re.split('\xb1', newStr)
    if len(splitStrList) == 1:
        splitStrList = re.split('\+\/\-', newStr)
    
    valueStr = splitStrList[0]
    valueStr = re.search(u'[\-\+]?[\d\.]+', valueStr)
    if valueStr is not None:
        valueStr = valueStr.group()
        try:
            value = float(valueStr)
            retDict['value'] = value
        except ValueError:
            return retDict
    if len(splitStrList)==2:
        errorStr = splitStrList[1]
        errorStr = re.search(u'[\-\+]?[\d\.]+', errorStr).group() 
        try:
            error = float(errorStr)
            retDict['error'] =error
        except ValueError:
            return retDict
    return retDict

def get_digits(inStr):
    digitSearch = re.search(u'\d+', inStr) 
    if digitSearch:
        digitStr = re.search(u'\d+', inStr).group()
        return float(digitStr)
    else:
        return None

def digit_pct(inStr):
    # count fraction of digit characters in string
    digitSearch = re.findall('\d', inStr)
    numDigits = len(digitSearch)
    if numDigits == 0:
        return 0.0
    totChars = max(len(inStr.encode("iso-8859-15", "replace")),1)
    fractDigits = float(numDigits)/totChars
    return fractDigits