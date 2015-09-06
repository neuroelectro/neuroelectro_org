# -*- coding: utf-8 -*-
"""
Created on Tue Mar 27 10:06:27 2012

@author: Shreejoy
"""

import string

from bs4 import BeautifulSoup
from django.core.exceptions import ObjectDoesNotExist

from article_text_mining.text_mining_util_fxns import get_tag_text, parens_resolver, comma_resolver
from article_text_mining.resolve_data_float import resolve_data_float

import neuroelectro.models as m


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

            cell_text = get_tag_text(th_html_tag)
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
                cell_text = get_tag_text(td_html_tag)
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
            pass

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
                                    nedm_ob.n = data_dict['num_obs']
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
                                                                             n = data_dict['num_obs'],
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


def check_if_table_header(inStr):
    """Returns True if any of the elements in the input string are an ascii character"""
    count = lambda l1, l2: len(list(filter(lambda c: c in l2, l1)))
    num_chars = count(inStr, string.ascii_letters)
    if num_chars > 0:
        return True
    else:
        return False


def resolve_table_header(inStr):
    """Return a lightly parsed version of a data table header cell string"""
    newStr, insideParens = parens_resolver(inStr)
    newStr, commaStr = comma_resolver(newStr)
    newStr = newStr.strip()
    return newStr, insideParens, commaStr


def printHtmlTable(tableTag):
    """Convenience function for printing a stringified html data table"""
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
            caption = get_tag_text(captionTag)
    #        caption = ''.join(captionTag.findAll(text=True))
            tableStr += caption + u'\n'
        rows = table.findAll('tr')
        for tr in rows:
            headers = tr.findAll('th')
            for th in headers:
                currText = get_tag_text(th)
    #            currText = ''.join(th.findAll(text=True))
    #            if currText is None:
    #                currText = '\t'
                text = u''.join(currText)
                tableStr += text +"|"
            cols = tr.findAll('td')
            for td in cols:
                currText = get_tag_text(td)
    #            currText = ''.join(td.findAll(text=True))
    #            if currText is None:
    #                currText = '\t'
                text = u''.join(currText)
                tableStr += text +"|"
            tableStr += u'\n'
        footnotesTag = soup.find('div', {'class':'table-foot'})
        footnotes = get_tag_text(footnotesTag)
        tableStr += footnotes

        print tableStr.encode("iso-8859-15", "replace")
        return tableStr
    except (UnicodeDecodeError, UnicodeEncodeError):
        print 'Unicode printing failed!'
        return