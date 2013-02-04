# -*- coding: utf-8 -*-
"""
Created on Tue Mar 27 10:06:27 2012

@author: Shreejoy
"""

import os
#import django_startup
import re
import struct
import gc
#import nltk
import tempfile
os.environ['MPLCONFIGDIR'] = tempfile.mkdtemp()
from matplotlib.pylab import *
#os.chdir('C:\Users\Shreejoy\Desktop\Biophysiome')
from neuroelectro.models import Article, MeshTerm, Substance, Journal
from neuroelectro.models import Neuron, NeuronSyn, Unit, DataSource
from neuroelectro.models import BrainRegion, InSituExpt, Protein, RegionExpr
from neuroelectro.models import DataTable, ArticleFullText, EphysConceptMap
from neuroelectro.models import EphysProp, EphysPropSyn, NeuronArticleMap
from neuroelectro.models import NeuronConceptMap, NeuronArticleMap, NeuronEphysDataMap
from neuroelectro.models import get_robot_user
#os.chdir('C:\Python27\Scripts\Biophys')

from django.db import transaction
from django.db.models import Count, Min
from xml.etree.ElementTree import XML
from urllib import quote_plus, quote
from urllib2 import Request, urlopen, URLError, HTTPError
from xml.etree.ElementTree import XML
import json
from pprint import pprint
from bs4 import BeautifulSoup
import types
import itertools
from fuzzywuzzy import fuzz, process
from django.db.models import Count
#from ExtractAbbrev import ExtractAbbrev
#from find_neurons_in_text import findNeuronsInText, getMostLikelyNeuron
#from html_process_tools import getSectionTag
MIN_NEURON_MENTIONS_AUTO = 5

#os.chdir('C:\Users\Shreejoy\Desktop\Biophysiome\Code')
def printHtmlTable(tableTag):
    soup = BeautifulSoup(''.join(tableTag))
    tableStr = u''
    try: 
        # print title
        #title = dt.article.title
        #tableStr += title + u'\n'
        # print 'Title: ' + title.encode('utf-8')
        
        table = soup.find('table')
        captionTag = soup.find('div', {'class':'table-caption'})
        if captionTag is None:
            captionTag = soup.find('div', {'class':'auto-clean'})
        if captionTag is not None:
            caption = findTextInTag(captionTag)
    #        caption = ''.join(captionTag.findAll(text=True))
            tableStr += caption + u'\n'
        rows = table.findAll('tr')
        for tr in rows:
            headers = tr.findAll('th')
            for th in headers:
                currText = findTextInTag(th)
    #            currText = ''.join(th.findAll(text=True))
    #            if currText is None: 
    #                currText = '\t'
                text = u''.join(currText)
                tableStr += text +"|"
            cols = tr.findAll('td')
            for td in cols:
                currText = findTextInTag(td)
    #            currText = ''.join(td.findAll(text=True))
    #            if currText is None: 
    #                currText = '\t'
                text = u''.join(currText)
                tableStr += text +"|"
            tableStr += u'\n'
           #print
        footnotesTag = soup.find('div', {'class':'table-foot'})
        footnotes = findTextInTag(footnotesTag)
        tableStr += footnotes

        print tableStr.encode("iso-8859-15", "replace")
        return tableStr
    except (UnicodeDecodeError, UnicodeEncodeError):
        print 'Unicode printing failed!'
        return 

def findTextInTag(tag):
#    print tag  
#    print type(tag)
#    if tag is list:
#        tag  = tag[0]
    if tag is None:
        return u''
    textInTag = u''.join(tag.findAll(text=True))
    if textInTag is '':
        textInTag = u'    '
    textInTag = textInTag.replace('\n', u' ')
    #print textInTag
    return textInTag
# process dataTables

def unicodeToIso(inStr):
    return inStr.encode("iso-8859-15", "replace")

def getTableHeaders(tableTag):
    soup = BeautifulSoup(''.join(tableTag))
    rowHeaders = []
    columnHeaders = []
    table = soup.find('table')
    if table == None:
        return rowHeaders, columnHeaders
    rows = table.findAll('tr')
    for tr in rows:
        headers = tr.findAll('th')
        for th in headers:
            currText = findTextInTag(th)
            captionTag = th.find('div', {'class':'table-caption'})
    #            currText = ''.join(th.findAll(text=True))
    #            if currText is None: 
    #                currText = '\t'
            columnHeaders.append(currText)
        cols = tr.findAll('td')
        if len(cols)>0:
            currText = findTextInTag(cols[0])
            rowHeaders.append(currText)
    return rowHeaders, columnHeaders
    
def getTableData(tableTag):
    soup = BeautifulSoup(''.join(tableTag))
    
    table = soup.find('table')
    rows = table.findAll('tr')
    ncols = len(rows[-1].findAll('td'))
#    print 'numRows = %d numCols = %d' % (len(rows), ncols)
    dataTable = [ [ 0 for i in range(ncols) ] for j in range(len(rows) ) ]
    idTable = [ [ 0 for i in range(ncols) ] for j in range(len(rows) ) ]
#    print dataTable
#    datarunTable = [ [ '' for i in range(20) ] for j in range(20 ) ]
    rowCnt = 0
    numHeaderRows = 0
    for tr in rows:
        headers = tr.findAll('th')
        if len(headers)> 0:
            numHeaderRows += 1
        colCnt = 0
        for th in headers:
            # set colCnt by finding first non-zero element in table
            try:
                colCnt = dataTable[rowCnt].index(0)
            except ValueError:
                print 'Table is likely fucked up!!!'
                dataTable = None
                idTable = None
                return dataTable, 0, idTable
                
            currText = findTextInTag(th)
            colspan = int(th['colspan'])
            rowspan = int(th['rowspan'])
            # print currText.encode("iso-8859-15", "replace"), rowspan, colspan
            
            for i in range(rowCnt, rowCnt+rowspan):
                for j in range(colCnt, colCnt+colspan):
                    try:
                        dataTable[i][j] = currText
                        idTable[i][j] = th['id']
                    except (IndexError):
                        continue
#            if rowspan > 1:
#                print 'UH OH rowspan > 1!!'
#            insertHeaders = [ [ currText for i in range(colspan) ] for j in range(rowspan)]
#            print insertHeaders
##            currText = ''.join(th.findAll(text=True))
##            if currText is None: 
##                currText = '\t'
##            print 'row Ind = %d colInd = %d'% (rowCnt, colCnt)
##            dataTable[rowCnt][colCnt] = currText
#            dataTable[rowCnt:(rowCnt+rowspan)][colCnt:(colCnt+colspan)] = insertHeaders
#            if colspan > 1:
#                dataTable[rowCnt][colCnt:(colCnt+colspan)] = itertools.repeat(currText,colspan)
            colCnt += colspan
        cols = tr.findAll('td')
        try:
            for td in cols:
                #print rowCnt, colCnt-1
                currText = findTextInTag(td)
                dataTable[rowCnt][colCnt] = currText
                idTable[rowCnt][colCnt] = td['id']
                colCnt += 1
        except IndexError:
            print 'Table is likely fucked up!!!'
            return dataTable, 0, idTable            
            
        rowCnt += 1
        #print dataTable
    return dataTable, numHeaderRows, idTable
    
#
#dts = DataTable.objects.filter(table_text__icontains = 'resistance')
#dt = dts[0]
#tableTag = dt.table_html
#soup = BeautifulSoup(u''.join(tableTag))
#
#cnt = 0
#for dt in dts:#[0:min(dts.count(), 10)]:
#    tableTag = dt.table_html
#    tableText = dt.table_text + ' ' + dt.article.title
##    printHtmlTable(tableTag)
#    #print dt.article.title.encode('utf-8')
#    #print 'Table Body'
#    neurons = findNeuronsInText(tableText)
#    if neurons != []:
#        printHtmlTable(tableTag)
##        dt.neurons = neurons
##        dt.save()
#        print neurons
#        print '\n'
#        cnt += 1
##    tiab = u'%s %s ' % (dt.article.title, dt.article.abstract)
##    print 'Title+Abstract'
##    findNeuronsInText(tiab)
##    print 'Full Text'
##    fulltextTagStr = dt.article.articlefulltext_set.get().full_text
##    fulltextTag = BeautifulSoup(''.join(fulltextTagStr))
##    fulltext = findTextInTag(fulltextTag)
##    findNeuronsInText(fulltext)
##    
#    #print '\n'
#print 'found fraction: %.2f' % (float(cnt)/dts.count())

def resolveDataFloat(inStr):
    retDict = {}
    # check if input string is mostly characters - then its probably not a data cont string
    if digitPct(inStr) < .05:
        print 'Too many elems of string are not digits: %.2f' % digitPct(inStr)
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
            retDict['numCells'] =numCells
        except ValueError:
            pass
    #remove parens instances
    newStr = re.sub('\(\d+\)', '', newStr)
    # try to split string based on +\-
    splitStrList = re.split('\xb1', newStr)
    valueStr = splitStrList[0]
    valueStr = re.search(u'[\d\-\+\.]+', valueStr)
    if valueStr is not None:
        valueStr = valueStr.group()
        try:
            value = float(valueStr)
            retDict['value'] = value
        except ValueError:
            return retDict
    if len(splitStrList)==2:
        errorStr = splitStrList[1]
        errorStr = re.search(u'[\d\-\+\.]+', errorStr).group() 
        try:
            error = float(errorStr)
            retDict['error'] =error
        except ValueError:
            return retDict
    return retDict

def parensResolver(inStr):
    parensCheck = re.findall(u'\(.+\)', inStr)
    insideParens = None
    if len(parensCheck) > 0:
        insideParens = parensCheck[0].strip('()')
    newStr = re.sub(u'\(.+\)', '', inStr)
    return newStr, insideParens
    
def commaResolver(inStr):
    commaCheck = inStr.split(',')
    newStr = commaCheck[0]
    rightStr = None
    if len(commaCheck) > 1:
        rightStr = commaCheck[1]
    return newStr, rightStr
        
    
def digitPct(inStr):
    # count fraction of digit characters in string
    digitSearch = re.findall('\d', inStr)
    numDigits = len(digitSearch)
    if numDigits == 0:
        return 0.0
    totChars = max(len(inStr.encode("iso-8859-15", "replace")),1)
    fractDigits = float(numDigits)/totChars
    return fractDigits

def isHeader(inStr):
    fractDigits = digitPct(inStr)
    if fractDigits < .25:
        return True
    else:
        return False
    
def resolveHeader(inStr):
    newStr, insideParens = parensResolver(inStr)
    newStr, commaStr = commaResolver(newStr)
    newStr = newStr.strip()
    return newStr

ephysSyns = EphysPropSyn.objects.all()
ephysSynList = [e.term.lower() for e in ephysSyns]
matchThresh = 90    
def matchEphysHeader(headerStr):  
    h = headerStr
    normHeader = resolveHeader(h)
    if len(normHeader) == 0:
        return ''
    elif normHeader in ephysSynList: # try to match exactly
        bestMatch = normHeader
        matchVal = 100
    else: #try to fuzzy match
        processOut = process.extractOne(normHeader, ephysSynList)
        if processOut is not None:
            bestMatch, matchVal = processOut
        else:
            return ''
    if matchVal > matchThresh:
        ephysSynOb = EphysPropSyn.objects.get(term = bestMatch)
        ephysPropOb = ephysSynOb.ephys_prop        
        return ephysPropOb
        
def getEphysObHeaderList(headerList):
    ephysObList = []
    for h in headerList:
        ephysMatch = matchEphysHeader(h)
        if ephysMatch == '':
            ephysObList.append(None)
        else:
            ephysObList.append(ephysMatch)
    return ephysObList

def assocNeuronEphysVals(neuronOb, ephysOb, dataTableOb, dataDict):
    try:
        value = dataDict['value']
    except(KeyError): # if no value - just return
        return
    nel = NeuronEphysLink.objects.get_or_create(neuron = neuronOb, ephys_prop = ephysOb, 
                                          data_table = dataTableOb, val = value)[0]    
    for key,value in dataDict.items():
        setattr(nel,key,value)
    nel.save()

    print neuronOb, ephysOb, nel.value

# tag tables if they contain ephys props in their headers
matchThresh = 80
matchThreshShort = 95 # threshold for short terms
shortLim = 4 # number of characters for short distinction
def assocDataTableEphysVal(dataTableOb):
    dt = dataTableOb
    ds = DataSource.objects.get(data_table = dt)
    robot_user = get_robot_user()
    if dt.table_text is None:
        return
        
    tableTag = dt.table_html
    soup = BeautifulSoup(''.join(tableTag))
    headerTags = soup.findAll('th')
    #print headerTags
    tdTags = soup.findAll('td')
    allTags = headerTags + tdTags
    
    for tag in allTags:
        origTagText = tag.get_text()
        tagText = origTagText .strip()

        if 'id' in tag.attrs.keys():
            tag_id = str(tag['id'])
        else:
            tag_id = -1
        if len(tagText) == 0:
            continue
        if isHeader(tagText) is True:
            normHeader = resolveHeader(tagText)
            if len(normHeader) == 0:
                continue
            elif normHeader in ephysSynList: # try to match exactly
                bestMatch = normHeader
                matchVal = 100
            else: #try to fuzzy match
                processOut = process.extractOne(normHeader, ephysSynList)
                if processOut is not None:
                    bestMatch, matchVal = processOut
                else:
                    continue
            if matchVal > matchThresh:
                ephysSynOb = EphysPropSyn.objects.get(term = bestMatch)
                ephysPropOb = ephysSynOb.ephysprop_set.all()[0]             
                # further check that if either header or syn is really short, 
                # match needs to be really fucking good
                if len(normHeader) <= shortLim or len(ephysSynOb.term) <= shortLim:
                    if matchVal < matchThreshShort:
                        continue
                 
                # create EphysConceptMap object
                save_ref_text = origTagText[0:min(len(origTagText),199)]
                #print save_ref_text.encode("iso-8859-15", "replace")
                #print ephysPropOb.name
#                print ephysSynOb.term
                #print matchVal    
                ephysConceptMapOb = EphysConceptMap.objects.get_or_create(ref_text = save_ref_text,
                                                                          ephys_prop = ephysPropOb,
                                                                          source = ds,
                                                                          dt_id = tag_id,
                                                                          match_quality = matchVal,
                                                                          added_by = robot_user,
                                                                          times_validated = 0)[0]                                                                          

def assocDataTableEphysValMult(dataTableObs):
    cnt = 0
    for dt in dataTableObs:
        cnt = cnt + 1
        if cnt % 100 == 0:
            print '%d of %d tables' % (cnt, dataTableObs.count())   
        assocDataTableEphysVal(dt)


def assignNeuronToTableTag(neuronOb, dataTableOb, tableTag):
    tag_id = tableTag['id']
    headerText = tableTag.text.strip()
    successBool = False
    if headerText is None:
        return successBool
    # check that there isn't already a ncm here
    if NeuronConceptMap.objects.filter(dt_id = tag_id, data_table = dataTableOb).exclude(added_by = 'robot').distinct().count() > 0:
        successBool = True        
        return successBool
    save_ref_text = headerText[0:min(len(headerText),199)]
    neuronConceptMapOb = NeuronConceptMap.objects.get_or_create(ref_text = save_ref_text,
                                                              neuron = neuronOb,
                                                              data_table = dataTableOb,
                                                              dt_id = tag_id,
                                                              added_by = 'robot')[0]    
    successBool = True        
    return successBool                                                              
# use a simple heuristic to tag data table headers for neuron concepts
def assocDataTableNeuronAuto(dataTableOb):
    soup = BeautifulSoup(dataTableOb.table_html)
    ecmObs = EphysConceptMap.objects.filter(data_table = dataTableOb)
    ecmTableIds = [ecmOb.dt_id for ecmOb in ecmObs]    
    namObs = NeuronArticleMap.objects.filter(article__datatable = dataTableOb).order_by('-num_mentions')
    if namObs[0].num_mentions < MIN_NEURON_MENTIONS_AUTO:
        return
    topNeuronOb = namObs[0].neuron
    
#    numTH = len(soup.findAll('th'))
#    numTR = len(soup.findAll('tr'))
#    numTD = len(soup.findAll('td'))
    ecmAllTD = True
    for e in ecmTableIds:
        if 'td' in e:
            continue
        else:
            ecmAllTD = False
            break
    # if all ephys entities are td, then call first nonblank header element top neuron
    successBool = False
    if ecmAllTD == True:
        headerTags = soup.findAll('th')
        if len(headerTags) >= 2:
            # assign neuron to header tag in 1th position
            firstHeaderTag = headerTags[1]            
            successBool = assignNeuronToTableTag(topNeuronOb, dataTableOb, firstHeaderTag)
            # call first nonblank header element top neuron
            if successBool == False:
                firstHeaderTag = soup.findAll('th', text != None)
                successBool = assignNeuronToTableTag(topNeuronOb, dataTableOb, firstHeaderTag) 
    print dataTableOb.pk, successBool                                                                      
               
def assocDataTableNeuronAutoMult(dataTableObs):
    cnt = 0
    for dt in dataTableObs:
        cnt = cnt + 1
        if cnt % 100 == 0:
            print '%d of %d tables' % (cnt, dataTableObs.count())   
        assocDataTableNeuronAuto(dt)    
               
           
def countDataTableMethods():
    dts = DataTable.objects.annotate(num_ecms=Count('ephysconceptmap__ephys_prop', distinct = True))
    dts = dts.order_by('-num_ecms')
    dts.filter()

# def assignDataValsToNeuronEphys(dt):
#     # check that dt has both ephys obs and neuron concept obs
#     try:
#         tableSoup = BeautifulSoup(dt.table_html)
#         if dt.ephysconceptmap_set.all().count() > 0 and dt.neuronconceptmap_set.all().count() > 0:
#             dataTable, numHeaderRows, idTable = getTableData(dt.table_html)
#             if dataTable is None or idTable is None:
#                 return
#     #        nRows = len(idTable)
#     #        nCols = len(idTable[0])
#     #        for rInd in range(1,nRows):
#     #            for cInd in range(1,nCols):
#     #                # get possible concepts for this entry
#     #                idTable[0][cInd]
#             ecmObs = dt.ephysconceptmap_set.all()
#             ncmObs = dt.neuronconceptmap_set.all()
#             for n in ncmObs:
#                 nId = n.dt_id
#                 nRowInd, nColInd = getInd(nId, idTable)
#                 for e in ecmObs:
#                     eId = e.dt_id
#                     if eId =='-1' or len(idTable) == 0:
#                         continue
#                     eRowInd, eColInd = getInd(eId, idTable)
#                     dataValRowInd = max(nRowInd, eRowInd)
#                     dataValColInd = max(nColInd, eColInd)
#                     dataValIdTag = idTable[dataValRowInd][dataValColInd]
#                     data_tag = tableSoup.find(id = dataValIdTag)
#                     if data_tag is None:
#                         continue
#                     ref_text = data_tag.get_text()
#                     retDict = resolveDataFloat(ref_text)
#                     #print retDict
#                     if 'value' in retDict.keys():
#                         val = retDict['value']
#                         nedmOb = NeuronEphysDataMap.objects.get_or_create(data_table = dt,
#                                                                  ref_text = ref_text,
#                                                                  dt_id = dataValIdTag,
#                                                                  added_by = 'robot',
#                                                                  neuron_concept_map = n,
#                                                                  ephys_concept_map = e,
#                                                                  val = val,
#                                                                  times_validated = 0,
#                                                                  )[0]
#                         if 'error' in retDict.keys():
#                             err = retDict['error']
#                             nedmOb.err = err
#                         if 'numCells' in retDict.keys():
#                             num_reps = retDict['numCells']    
#                             nedmOb.n = num_reps
#                         nedmOb.save()
#     except (TypeError):
#         return
                    #print nedmOb
                #print nRowInd, nColInd, eRowInd, eColInd
                
def assignDataValsToNeuronEphys(dt, user = None):
    # check that dt has both ephys obs and neuron concept obs
    try:
        tableSoup = BeautifulSoup(dt.table_html)
        ds = DataSource.objects.get(data_table = dt)
        if ds.ephysconceptmap_set.all().count() > 0 and ds.neuronconceptmap_set.all().count() > 0:
            dataTable, numHeaderRows, idTable = getTableData(dt.table_html)
            if dataTable is None or idTable is None:
                return
            ecmObs = ds.ephysconceptmap_set.all()
            ncmObs = ds.neuronconceptmap_set.all()
            for n in ncmObs:
                nId = n.dt_id
                nRowInd, nColInd = getInd(nId, idTable)
                for e in ecmObs:
                    eId = e.dt_id
                    if eId =='-1' or len(idTable) == 0:
                        continue
                    eRowInd, eColInd = getInd(eId, idTable)
                    dataValRowInd = max(nRowInd, eRowInd)
                    dataValColInd = max(nColInd, eColInd)
                    dataValIdTag = idTable[dataValRowInd][dataValColInd]
                    data_tag = tableSoup.find(id = dataValIdTag)
                    if data_tag is None:
                        continue
                    ref_text = data_tag.get_text()
                    retDict = resolveDataFloat(ref_text)
                    #print retDict
                    if 'value' in retDict.keys():
                        val = retDict['value']
                        nedmOb = NeuronEphysDataMap.objects.get_or_create(source = ds,
                                                                 ref_text = ref_text,
                                                                 dt_id = dataValIdTag,
                                                                 #added_by = 'robot',
                                                                 neuron_concept_map = n,
                                                                 ephys_concept_map = e,
                                                                 val = val,
                                                                 times_validated = 0,
                                                                 )[0]
                        if user:
                        	nedmOb.added_by = user
                        if 'error' in retDict.keys():
                            err = retDict['error']
                            nedmOb.err = err
                        if 'numCells' in retDict.keys():
                            num_reps = retDict['numCells']    
                            nedmOb.n = num_reps
                        nedmOb.save()
    except (TypeError):
        return
                    #print nedmOb
                #print nRowInd, nColInd, eRowInd, eColInd

def assignDataValsToNeuronEphysMult(dataTableObs):
    cnt = 0
    for dt in dataTableObs:
        cnt = cnt + 1
        if cnt % 10 == 0:
            print '%d of %d tables' % (cnt, dataTableObs.count())   
        assignDataValsToNeuronEphys(dt)  

def getInd(elem, mat):
    for i in range(len(mat)):
        for j in range(len(mat[0])):
            if mat[i][j] == elem:
                return i, j                
                # get data entries corresponding to this pair
#def check    
#    if rowEphysFlag is True and colEphysFlag is False:
#        rowHeaderInd = 0
#        for i in range(numHeaderRows, nrows):
#            if ephysObListRows[rowHeaderInd] is not None:
#                # find all values in this row
#                #for j in range(1,nDataCols):
#                for j in range(1,2):
#                    tableEntry = dataTable[i][j]
#                    if isinstance(tableEntry, unicode):
#                        dataDict = resolveDataFloat(tableEntry)
#                        neuronOb = tableNeurons[0]
#                        assocNeuronEphysVals(neuronOb, ephysObListRows[rowHeaderInd], dt, dataDict)
#                        # associate data values to ephys prop and neurons
#                    
#    #                print rowHeaders[rowHeaderInd].encode("iso-8859-15", "replace")
#    #                print tableEntry.encode("iso-8859-15", "replace")
#            rowHeaderInd += 1
#    cnt += 1    

    
    
#    print '%d of %d data tables' % (cnt, dts.count())
#    tableTag = dataTableOb.table_html
#    dataTable, numHeaderRows = getTableData(tableTag)
#    if dataTable is None:
#        cnt += 1
#        return
#    nrows = len(dataTable)
#    ncols = len(dataTable[-1])
#    
#    nDataRows = nrows - numHeaderRows
#    nDataCols = ncols
#    rowHeaders, colHeaders = getTableHeaders(tableTag)
#    
#    ephysObListRows = getEphysObHeaderList(rowHeaders)
#    ephysObListCols = getEphysObHeaderList(colHeaders)
#    
#    # check if either rows or column headers contain ephys terms
#    rowEphysFlag = ephysObListRows != [None]*len(ephysObListRows)
#    colEphysFlag = ephysObListCols != [None]*len(ephysObListCols)
#    
#    tableNeurons = dt.neurons.all() 
#    if len(tableNeurons) == 0: # can't find neurons in table text - look at art full text
#        fullTextHtml = dt.article.articlefulltext_set.all()[0].full_text
#        fullText = BeautifulSoup(fullTextHtml).text
#        neuron = getMostLikelyNeuron(fullText)
#    #    if neuron is None:
#    #        cnt += 1
#    #        print "can't resolve neuron in \n %s" % (unicodeToIso(dt.article.title))
#    #        return   
#        tableNeurons = [neuron]
#        
#    if rowEphysFlag is True and colEphysFlag is False:
#        rowHeaderInd = 0
#        for i in range(numHeaderRows, nrows):
#            if ephysObListRows[rowHeaderInd] is not None:
#                # find all values in this row
#                #for j in range(1,nDataCols):
#                for j in range(1,2):
#                    tableEntry = dataTable[i][j]
#                    if isinstance(tableEntry, unicode):
#                        dataDict = resolveDataFloat(tableEntry)
#                        neuronOb = tableNeurons[0]
#                        assocNeuronEphysVals(neuronOb, ephysObListRows[rowHeaderInd], dt, dataDict)
#                        # associate data values to ephys prop and neurons
#                    
#    #                print rowHeaders[rowHeaderInd].encode("iso-8859-15", "replace")
#    #                print tableEntry.encode("iso-8859-15", "replace")
#            rowHeaderInd += 1
#    cnt += 1    


# print tables that have both neurons and ephys_props
#dts = DataTable.objects.filter(ephys_props__isnull = False, neurons__isnull = False).distinct()
#dts = list(set(dts))
#for dt in dts[0:20]:
#    tableTag = dt.table_html
#    dataTable = getTableData(tableTag)
#    printHtmlTable(tableTag)
#    print dataTable
#    print dt.neurons.all()
#    print dt.ephys_props.all()
#    print '\n'
#    
#really simple heuristic - if there's only a single tagged neuron, 
# look for something like control or wild type and associate those props with the neuron

#cnt = 0
#for dt in dts[60:dts.count()]:
#    print '%d of %d data tables' % (cnt, dts.count())
#    tableTag = dt.table_html
#    dataTable, numHeaderRows = getTableData(tableTag)
#    if dataTable is None:
#        cnt += 1
#        continue
#    nrows = len(dataTable)
#    ncols = len(dataTable[-1])
#    
#    nDataRows = nrows - numHeaderRows
#    nDataCols = ncols
#    rowHeaders, colHeaders = getTableHeaders(tableTag)
#    
#    ephysObListRows = getEphysObHeaderList(rowHeaders)
#    ephysObListCols = getEphysObHeaderList(colHeaders)
#    
#    # check if either rows or column headers contain ephys terms
#    rowEphysFlag = ephysObListRows != [None]*len(ephysObListRows)
#    colEphysFlag = ephysObListCols != [None]*len(ephysObListCols)
#    
#    tableNeurons = dt.neurons.all() 
#    if len(tableNeurons) == 0: # can't find neurons in table text - look at art full text
#        fullTextHtml = dt.article.articlefulltext_set.all()[0].full_text
#        fullText = BeautifulSoup(fullTextHtml).text
#        neuron = getMostLikelyNeuron(fullText)
#        if neuron is None:
#            cnt += 1
#            print "can't resolve neuron in \n %s" % (unicodeToIso(dt.article.title))
#            continue      
#        tableNeurons = [neuron]
#        
#    if rowEphysFlag is True and colEphysFlag is False:
#        rowHeaderInd = 0
#        for i in range(numHeaderRows, nrows):
#            if ephysObListRows[rowHeaderInd] is not None:
#                # find all values in this row
#                #for j in range(1,nDataCols):
#                for j in range(1,2):
#                    tableEntry = dataTable[i][j]
#                    if isinstance(tableEntry, unicode):
#                        dataDict = resolveDataFloat(tableEntry)
#                        neuronOb = tableNeurons[0]
#                        assocNeuronEphysVals(neuronOb, ephysObListRows[rowHeaderInd], dt, dataDict)
#                        # associate data values to ephys prop and neurons
#                    
#    #                print rowHeaders[rowHeaderInd].encode("iso-8859-15", "replace")
#    #                print tableEntry.encode("iso-8859-15", "replace")
#            rowHeaderInd += 1
#    cnt += 1
##            tableRow = dataTable[i,1:]
##    S
##    
##    for j in range(ncols):
##        if rowHeaders[rowCnt] == 'Control':
##            neuronOb = dt.neurons.all()[0]
#

#nels = NeuronEphysLink.objects.all()
#neuronObList = list(set([n.neuron for n in nels]))
#ephysObList= list(set([n.ephys_prop for n in nels]))
#dataTableObList = list(set([n.data_table for n in nels]))
#neuronList = [n.name for n in neuronObList]
#ephysList = [n.name for n in ephysObList]
##neurons = Neuron.objects.filter(neuron_ephys_link) 
##nels = NeuronEphysLink.objects.filter(neuron__name = 'Hippocampus CA3 pyramidal cell', ephys_prop__name = 'input resistance')
#
#table = np.zeros([len(dataTableObList),len(ephysObList)])
#rowCnt = 0
#dtCnt = 0
#neuronList = ['' for i in range(len(dataTableObList))]
#linkList = ['' for i in range(len(dataTableObList))]
#regionIndList = [0 for i in range(len(dataTableObList))]
#
#ephysCnt = 0
#for i in ephysObList:
#    for j in neuronObList:
#        dtCnt = 0
#        for k in dataTableObList:
#            nel = NeuronEphysLink.objects.filter(neuron = j, ephys_prop = i, data_table = k)
#            if nel.count() == 0:
#                dtCnt += 1
#                continue
#            value = nel[0].val
#            table[dtCnt, ephysCnt]= value
#            print j, dtCnt
#            neuronList[dtCnt] = j.name
#            linkList[dtCnt] = k.link
#            if j.regions.count() > 0:
#                r = j.regions.all()[0]
#                regionIndList[dtCnt] = int(r.pk)
#            dtCnt += 1
#    ephysCnt += 1
#


            

            
    
    
    
                                        


# just associate every neuron seen in a table to all ephys props in that table


#rowHeaders = dataTable[]
#colHeaders = dataTable[0]
#
#rowCnt = 0
#for i in range(numHeaderRows+1, nrows):
#    for j in range(ncols):
#        if rowHeaders[rowCnt] == 'Control':
#            neuronOb = dt.neurons.all()[0]
            

        
        




# 

        
#        matchList = []
#        
#        #print normHeader
#        for s in ephysSyns:
#            syn = s.term.lower()
#            matchRatio = fuzz.ratio(syn, normHeader.lower())
#            #if syn == normHeader.lower():
#            if  matchRatio > 80:
#                tempMatch = (syn, normHeader, matchRatio)
#                matchList.append(tempMatch)
#        if len(matchList) > 0:
#            print matchList
#            finalMatch = 
#    dataTable = getTableData(tableTag, len(rowHeaders), len(colHeaders))
#    printHtmlTable(tableTag)
#    print dataTable
#    print '\n'
    
    

