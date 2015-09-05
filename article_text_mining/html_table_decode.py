# -*- coding: utf-8 -*-
"""
Created on Tue Mar 27 10:06:27 2012

@author: Shreejoy
"""

import re

import neuroelectro.models as m
from resolve_data_float import resolve_data_float

from django.db.models import Count
from bs4 import BeautifulSoup
from fuzzywuzzy import process
import string
from django.core.exceptions import ObjectDoesNotExist


MIN_NEURON_MENTIONS_AUTO = 5

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
    
def resolveDataFloat(inStr):
    return resolve_data_float.resolve_data_float(inStr)
    
def getDigits(inStr):
    return resolve_data_float.get_digits(inStr)

def digitPct(inStr):
    return resolve_data_float.digit_pct(inStr)

def parensResolver(inStr):
    parensCheck = re.findall(u'\(.+\)', inStr)
    insideParens = None
    if len(parensCheck) > 0:
        insideParens = parensCheck[0].strip('()')
    newStr = re.sub(u'\(.+\)', '', inStr)
    if insideParens:
        insideParens.strip()
    return newStr, insideParens
    
def commaResolver(inStr):
    commaCheck = inStr.split(',')
    newStr = commaCheck[0]
    rightStr = None
    if len(commaCheck) > 1:
        rightStr = commaCheck[1]
    if rightStr:
        rightStr = rightStr.strip()
    return newStr, rightStr

count = lambda l1, l2: len(list(filter(lambda c: c in l2, l1)))
def isHeader(inStr):
    num_chars = count(inStr, string.ascii_letters)
    if num_chars > 0:
        return True
    else:
        return False
    
def resolveHeader(inStr):
    newStr, insideParens = parensResolver(inStr)
    newStr, commaStr = commaResolver(newStr)
    newStr = newStr.strip()
    return newStr, insideParens, commaStr

def fuzzy_match_term_to_list(target_term, matching_list):
    """Finds best fuzzy-matching term in list to a given target term
    
    Args:
        target_term: the string that you want to be matched
        matching_list: the list of strings that you want matched against, typically a list of synonyms
        
    Returns: 
        the best matching element in matching_list to the target_term
        if fuzzy-match is higher than a threshold, or None otherwise
        
    """  
    
    # settings for hard thresholds governing fuzzy matching
    MATCH_THRESHOLD = 80
    MATCH_THRESHOLD_SHORT = 95 # threshold for short terms
    SHORT_LIMIT = 4 # number of characters for short distinction
        
    if len(target_term) == 0:
        return None
    elif target_term in matching_list: # try to match exactly
        bestMatch = target_term
        matchVal = 100
    else: #try to fuzzy match
        try:
            processOut = process.extractOne(target_term, matching_list)
            if processOut is not None:
                bestMatch, matchVal = processOut
            else:
                return None
        except ZeroDivisionError:
            return None
    if matchVal > MATCH_THRESHOLD:
        if len(target_term) <= SHORT_LIMIT or len(bestMatch) <= SHORT_LIMIT:
            if matchVal < MATCH_THRESHOLD_SHORT:
                return None
        # now find the ephys prop corresponding to the matching synonym term
        return bestMatch


def match_ephys_header(header_str, ephys_synonym_list):  
    """Given a data table header string, returns closest matching ephys prop object
        or None if no ephys synonym has a high match
    
    Args:
        header_str: header string from a data table 
        ephys_synonym_list: the list of strings representing ephys synonyms
        
    Returns: 
        An EphysProp neuroelectro.models object whose Ephys Synonym 
        best matches the header_str if match is higher than threshold, 
        or None otherwise
        example:
        
        <EphysProp: Input resistance>
        
    """  
    synapse_stop_words = get_synapse_stop_words()  # a list of stop words relating to synapse terms
    
    (normHeader, insideParens, commaStr) = resolveHeader(header_str)
    best_matching_ephys_syn = fuzzy_match_term_to_list(normHeader, ephys_synonym_list)
    if best_matching_ephys_syn: # if it's not None
        if any(substring in normHeader for substring in synapse_stop_words):
            # if header contains a synaptic plasticity term, then dont associate it to anything
            return None
        
        # find ephys prop matching synonym term
        ephysPropQuerySet = m.EphysProp.objects.filter(synonyms__term = best_matching_ephys_syn)
        if ephysPropQuerySet.count() > 0:
            ephysPropOb = ephysPropQuerySet[0] 
            if ephysPropQuerySet.count() > 1:
                print 'Multiple ephys properties found matching synonym: %s' % best_matching_ephys_syn  
            return ephysPropOb
        else:
            return None
    else:
        return None
    
def update_ecm_using_text_mining(ecm, ephys_synonym_list=None, verbose_output=True):
    """Updates an EphysConceptMap object using text mining rules
    
    Args:
        ecm: an EphysConceptMap object for the object to be updated
        ephys_synonym_list: the list of strings representing ephys synonyms
        verbose_output: a bool indicating whether function should print statements
    """
    if not ephys_synonym_list:
        ephysSyns = m.EphysPropSyn.objects.all()
        ephys_synonym_list = [e.term.lower() for e in ephysSyns]
    
    if not ecm.ref_text: # some light error checking to make sure there's some text for the ecm object
        return
    
    # get the closest matching ephys prop given the table header reference text
    matched_ephys_prop = match_ephys_header(ecm.ref_text, ephys_synonym_list)
    
    if matched_ephys_prop is None: # no ephys props matched 
        if verbose_output:
            print 'deleting %s, prop: %s' % (ecm.ref_text, ecm.ephys_prop)
        ecm.delete() # remove the EphysConceptMap since none of the updated EphysProps matched it
        
    elif matched_ephys_prop != ecm.ephys_prop: # different found prop than existing one
        if verbose_output:
            print 'changing %s, to prop: %s, from prop: %s' %(ecm.ref_text, matched_ephys_prop, ecm.ephys_prop)
            
        ecm.ephys_prop = matched_ephys_prop # update the ecm
        ecm.changed_by = m.get_robot_user()
        ecm.save()

def get_synapse_stop_words():
    """Return a list of words which are common in synapse ephys terms"""
    synapse_stop_words = ['EPSP', 'IPSP', 'IPSC', 'EPSC', 'PSP', 'PSC']
    synapse_stop_words.extend([w.lower() for w in synapse_stop_words])
    return synapse_stop_words

# tag tables if they contain ephys props in their headers

def assocDataTableEphysVal(dataTableOb):
    """Associates a data table object with ephys concept map objects 
    """
    dt = dataTableOb
    ds = m.DataSource.objects.get(data_table = dt)
    robot_user = m.get_robot_user()
    if dt.table_text is None:
        return
    
    ephysSyns = m.EphysPropSyn.objects.all()
    ephysSynList = [e.term.lower() for e in ephysSyns]
    
    tableTag = dt.table_html
    soup = BeautifulSoup(''.join(tableTag))
    headerTags = soup.findAll('th')
    tdTags = soup.findAll('td')
    allTags = headerTags + tdTags
    
    for tag in allTags:
        origTagText = tag.get_text()
        tagText = origTagText.strip()

        if 'id' in tag.attrs.keys():
            tag_id = str(tag['id'])
        else:
            tag_id = -1
        if len(tagText) == 0:
            continue
        if isHeader(tagText) is True:
            # SJT Note - Currently doesn't mine terms in synapse stop words list 
            matched_ephys_ob = match_ephys_header(tagText, ephysSynList)
            if matched_ephys_ob:
                
                save_ref_text = origTagText[0:min(len(origTagText),199)]
                # create EphysConceptMap object
                ephysConceptMapOb = m.EphysConceptMap.objects.get_or_create(ref_text = save_ref_text,
                                                                          ephys_prop = matched_ephys_ob,
                                                                          source = ds,
                                                                          dt_id = tag_id,
                                                                          #match_quality = matchVal,
                                                                          changed_by = robot_user,
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
    if m.NeuronConceptMap.objects.filter(dt_id = tag_id, data_table = dataTableOb).exclude(added_by = 'robot').distinct().count() > 0:
        successBool = True        
        return successBool
    save_ref_text = headerText[0:min(len(headerText),199)]
    neuronConceptMapOb = m.NeuronConceptMap.objects.get_or_create(ref_text = save_ref_text,
                                                              neuron = neuronOb,
                                                              data_table = dataTableOb,
                                                              dt_id = tag_id,
                                                              added_by = 'robot')[0]    
    successBool = True        
    return successBool                                                              
# use a simple heuristic to tag data table headers for neuron concepts
def assocDataTableNeuronAuto(dataTableOb):
    soup = BeautifulSoup(dataTableOb.table_html)
    ecmObs = m.EphysConceptMap.objects.filter(data_table = dataTableOb)
    ecmTableIds = [ecmOb.dt_id for ecmOb in ecmObs]    
    namObs = m.NeuronArticleMap.objects.filter(article__datatable = dataTableOb).order_by('-num_mentions')
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
#             if successBool == False:
#                 firstHeaderTag = soup.findAll('th', text != None)
#                 successBool = assignNeuronToTableTag(topNeuronOb, dataTableOb, firstHeaderTag) 
    print dataTableOb.pk, successBool                                                                      
               
def assocDataTableNeuronAutoMult(dataTableObs):
    cnt = 0
    for dt in dataTableObs:
        cnt = cnt + 1
        if cnt % 100 == 0:
            print '%d of %d tables' % (cnt, dataTableObs.count())   
        assocDataTableNeuronAuto(dt)    
               
           
def countDataTableMethods():
    dts = m.DataTable.objects.annotate(num_ecms=Count('ephysconceptmap__ephys_prop', distinct = True))
    dts = dts.order_by('-num_ecms')
    dts.filter()


def getTableData(html_table_tag):
    """Returns a 2D table row-column representation of an input html data table

    Args:
        html_table_tag: the html table tag of a data table object,
                            something that can be beautiful soupified
    Returns:
        data_table_rep: a 2D python table representation of the table text
        num_header_rows: number of rows in the table header
        id_table_rep: a 2D python table representation of the table where each cell element
                        is the 'id' tag of the table cell

    Comments:
        function is lightly tested but should be robust to most ugly html tables provided by publishers

    """

    soup = BeautifulSoup(''.join(html_table_tag))

    html_table = soup.find('table')
    row_tags = html_table.findAll('tr')

    # line of code could be more robust - ideally it'd be the max number of columns in any row
    n_cols = len(row_tags[-1].findAll('td'))

    # initialize representation of data table as 2D python table
    data_table_rep = [ [ 0 for i in range(n_cols) ] for j in range(len(row_tags) ) ]

    # initialize representation of data table as 2D python table composed of html id elements
    id_table_rep = [ [ 0 for i in range(n_cols) ] for j in range(len(row_tags) ) ]

    row_cnt = 0
    num_header_rows = 0

    # iterate through all table rows
    for tr_html_tag in row_tags:
        header_tags = tr_html_tag.findAll('th')
        if len(header_tags)> 0:
            num_header_rows += 1
        col_cnt = 0

        # counts the number of columns - I think??
        # set colCnt by finding first non-zero element in table
        try:
            col_cnt = data_table_rep[row_cnt].index(0)
        except ValueError:
            print 'Table is likely fucked up!!!'
            data_table_rep = None
            id_table_rep = None
            return data_table_rep, 0, id_table_rep

        for th_html_tag in header_tags:

            cell_text = findTextInTag(th_html_tag)
            try:
                column_width = int(th_html_tag['colspan'])
            except KeyError:
                column_width = 1
            try:
                row_width = int(th_html_tag['rowspan'])
            except KeyError:
                row_width = 1

            for i in range(row_cnt, row_cnt+row_width):
                while data_table_rep[i][col_cnt] != 0:
                    col_cnt += 1
                for j in range(col_cnt, col_cnt+column_width):
                    try:
                        data_table_rep[i][j] = cell_text
                        id_table_rep[i][j] = th_html_tag['id']
                    except IndexError:
                        continue
            col_cnt += column_width
        col_tags = tr_html_tag.findAll('td')
        try:
            for td_html_tag in col_tags:
                #print rowCnt, colCnt-1
                cell_text = findTextInTag(td_html_tag)
                try:
                    column_width = int(td_html_tag['colspan'])
                except KeyError:
                    column_width = 1
                try:
                    row_width = int(td_html_tag['rowspan'])
                except KeyError:
                    row_width = 1

                for i in range(row_cnt, row_cnt+row_width):
                    # need to check if current row and col already has an element
                    while data_table_rep[i][col_cnt] != 0:
                        col_cnt += 1
                    for j in range(col_cnt, col_cnt + column_width):
                        data_table_rep[i][j] = cell_text
                        id_table_rep[i][j] = td_html_tag['id']
                col_cnt += column_width
        except IndexError:
            #print 'Table is likely fucked up!!!'
            pass
            #return dataTable, 0, idTable

        row_cnt += 1
    return data_table_rep, num_header_rows, id_table_rep

def assignDataValsToNeuronEphys(data_table_object, user = None):
    """Assigns neuroelectro.models NeuronEphysDataMap objects to a given DataTable
        object based on presence of NeuronConceptMaps and EphysConceptMaps

    Args:
        data_table_object: neuroelectro.models DataTable object
    Returns:
        Nothing - (the method merely assigns database objects)

    """

    # check that data_table_object has both ephys obs and neuron concept obs
    return_dict = dict()
    try:
        tableSoup = BeautifulSoup(data_table_object.table_html)
        ds = m.DataSource.objects.get(data_table = data_table_object)
        ecm_obs = ds.ephysconceptmap_set.all()
        ncm_obs = ds.neuronconceptmap_set.all()
        efcm_obs = ds.expfactconceptmap_set.all()
        # first check if there are ephys and neuron concept maps assigned to table
        if ecm_obs.count() > 0 and ncm_obs.count() > 0:

            # returns a flattened, parsed form of table where data table cells can be easily checked for associated concept maps
            dataTable, numHeaderRows, html_tag_id_table = getTableData(data_table_object.table_html)

            # if dataTable or idTable is none, parsing table failed, so return
            if dataTable is None or html_tag_id_table is None:
                return

            # for each
            for ncm in ncm_obs:
                ncm_html_tag_id = ncm.dt_id

                # the same ncm may be linked to multiple data table cells
                matching_neuron_cells = get_matching_inds(ncm_html_tag_id, html_tag_id_table)
                for ecm in ecm_obs:
                    ecm_html_tag_id = ecm.dt_id
                    if ecm_html_tag_id =='-1' or len(html_tag_id_table) == 0:
                        continue

                    # the same ecm may be linked to multiple data table cells
                    matching_ephys_cells = get_matching_inds(ecm_html_tag_id, html_tag_id_table)

                    # iterate through all matched cells, finding corresponding data value cells at their intersection
                    for c1 in matching_neuron_cells:
                        ncm_row_ind = c1[0]
                        ncm_col_ind = c1[1]
                        for c2 in matching_ephys_cells:
                            ecm_row_ind = c2[0]
                            ecm_col_ind = c2[1]

                            # the max below is saying data cells are usually to the right and bottom of header cells
                            table_cell_row_ind = max(ncm_row_ind, ecm_row_ind)
                            table_cell_col_ind = max(ncm_col_ind, ecm_col_ind)
                            table_cell_html_tag_id = html_tag_id_table[table_cell_row_ind][table_cell_col_ind]
                            data_tag = tableSoup.find(id = table_cell_html_tag_id)
                            if data_tag is None:
                                continue
                            ref_text = data_tag.get_text()

                            # regex out the floating point values of data value string
                            data_dict = resolve_data_float(ref_text, True)

                            if data_dict['value']:


                                # check for experimental factor concept maps
                                if efcm_obs is not None:
                                    # get efcm and add it to nedm
                                    efcm_ob_list = []
                                    for efcm in efcm_obs:

                                        efcm_html_tag_id = efcm.dt_id

                                        # get table cells for this efcm
                                        matching_efcm_cells = get_matching_inds(efcm_html_tag_id, html_tag_id_table)

                                        # if any of the efcm cells match up with the current cell, add the efcm to the list
                                        matching_rows = [e[0] for e in matching_efcm_cells]
                                        matching_cols = [e[1] for e in matching_efcm_cells]
                                        if table_cell_row_ind in matching_rows or table_cell_col_ind in matching_cols:
                                            efcm_ob_list.append(efcm)

                                # TODO : refactor this to just return a list of dicts with fields including, ncm, ecm, and efcms
                                temp_return_dict = dict()
                                temp_return_dict['ncm'] = ncm
                                temp_return_dict['ecm'] = ecm
                                temp_return_dict['data_value_dict'] = data_dict
                                temp_return_dict['efcm_list'] = efcm_ob_list

                                return_dict[table_cell_html_tag_id] = temp_return_dict

                                # check if nedm already exists
                                try:
                                    nedm_ob = m.NeuronEphysDataMap.objects.get(source = ds, dt_id = table_cell_html_tag_id)
                                    nedm_ob.changed_by = user
                                    nedm_ob.neuron_concept_map = ncm
                                    nedm_ob.ephys_concept_map = ecm
                                    nedm_ob.val = data_dict['value']
                                    nedm_ob.err = data_dict['error']
                                    nedm_ob.n = data_dict['numCells']
                                    nedm_ob.times_validated = nedm_ob.times_validated + 1
                                    nedm_ob.save()
                                except ObjectDoesNotExist:
                                    nedm_ob = m.NeuronEphysDataMap.objects.create(source = ds,
                                                                             ref_text = ref_text,
                                                                             dt_id = table_cell_html_tag_id,
                                                                             changed_by = user,
                                                                             neuron_concept_map = ncm,
                                                                             ephys_concept_map = ecm,
                                                                             val = data_dict['value'],
                                                                             err = data_dict['error'],
                                                                             n = data_dict['numCells'],
                                                                             times_validated = 0,
                                                                             )

                                # assign experimental factor concept maps
                                if efcm_obs is not None:
                                    # get efcm and add it to nedm
                                    for efcm in efcm_obs:
                                        efcm_html_tag_id = efcm.dt_id
                                        efcmRowInd, efcmColInd = getInd(efcm_html_tag_id, html_tag_id_table)
                                        if efcmRowInd > efcmColInd:
                                            if table_cell_row_ind == efcmRowInd:
                                                nedm_ob.exp_fact_concept_maps.add(efcm)
                                        else:
                                            if table_cell_col_ind == efcmColInd:
                                                nedm_ob.exp_fact_concept_maps.add(efcm)
                                nedm_ob.save()
        return return_dict
    except (TypeError):
        print TypeError
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

def get_matching_inds(elem, mat):
    matches = []
    for i in range(len(mat)):
        for j in range(len(mat[0])):
            if mat[i][j] == elem:
                matches.append( (i, j ))
    return matches