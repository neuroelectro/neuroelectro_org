# -*- coding: utf-8 -*-
"""
Created on Tue Mar 27 10:06:27 2012

@author: Shreejoy
"""

from bs4 import BeautifulSoup
from django.core.exceptions import ObjectDoesNotExist

from article_text_mining.rep_html_table_struct import rep_html_table_struct
from article_text_mining.resolve_data_float import resolve_data_float
import neuroelectro.models as m


def find_data_vals_in_table(data_table_object, user = None):
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
        table_soup = BeautifulSoup(data_table_object.table_html, 'lxml')
        ds = m.DataSource.objects.get(data_table = data_table_object)
        ecm_obs = ds.ephysconceptmap_set.all()
        ncm_obs = ds.neuronconceptmap_set.all()
        efcm_obs = ds.expfactconceptmap_set.all()
        # first check if there are ephys and neuron concept maps assigned to table
        if ecm_obs.count() > 0 and ncm_obs.count() > 0:

            # returns a flattened, parsed form of table where data table cells can be easily checked for associated concept maps
            dataTable, numHeaderRows, html_tag_id_table = rep_html_table_struct(data_table_object.table_html)

            # if dataTable or idTable is none, parsing table failed, so return
            if dataTable is None or html_tag_id_table is None:
                return

            # for each neuron concept map
            for ncm in ncm_obs:
                ncm_html_tag_id = ncm.dt_id

                # the same ncm may be linked to multiple data table value cells due to rowspan/colspan issues
                matching_neuron_cells = get_matching_inds(ncm_html_tag_id, html_tag_id_table)
                for ecm in ecm_obs:
                    ecm_html_tag_id = ecm.dt_id
                    if ecm_html_tag_id == '-1' or len(html_tag_id_table) == 0:
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
                            data_tag = table_soup.find(id=table_cell_html_tag_id)
                            if data_tag is None:
                                continue
                            ref_text = data_tag.get_text()

                            # regex out the floating point values of data value string
                            data_dict = resolve_data_float(ref_text, True)

                            if data_dict['value']:

                                # check for experimental factor concept maps
                                if efcm_obs is not None:
                                    # get efcm and add it to nedm
                                    efcm_pk_list = []
                                    for efcm in efcm_obs:

                                        efcm_html_tag_id = efcm.dt_id

                                        # get table cells for this efcm
                                        matching_efcm_cells = get_matching_inds(efcm_html_tag_id, html_tag_id_table)

                                        # if any of the efcm cells match up with the current cell, add it to the list
                                        matching_rows = [e[0] for e in matching_efcm_cells]
                                        matching_cols = [e[1] for e in matching_efcm_cells]
                                        if table_cell_row_ind in matching_rows or table_cell_col_ind in matching_cols:
                                            efcm_pk_list.append(efcm.pk)

                                temp_return_dict = dict()
                                temp_return_dict['ncm_pk'] = ncm.pk
                                temp_return_dict['ecm_pk'] = ecm.pk
                                temp_return_dict['data_value_dict'] = data_dict
                                temp_return_dict['efcm_pk_list'] = efcm_pk_list

                                return_dict[table_cell_html_tag_id] = temp_return_dict


        return return_dict
    except (TypeError):
        print TypeError
        return
                    #print nedmOb
                #print nRowInd, nColInd, eRowInd, eColInd


def assignDataValsToNeuronEphys(data_table_object, user = None):
    # pass
    # assign_table_ephys_to_database(neuron_ephys_data_dict)
    # for k in neuron_ephys_data_dict.keys():
    #     pass
        # # check if nedm already exists
        # try:
        #     nedm_ob = m.NeuronEphysDataMap.objects.get(source = ds, dt_id = table_cell_html_tag_id)
        #     nedm_ob.changed_by = user
        #     nedm_ob.neuron_concept_map = ncm
        #     nedm_ob.ephys_concept_map = ecm
        #     nedm_ob.val = data_dict['value']
        #     nedm_ob.err = data_dict['error']
        #     nedm_ob.n = data_dict['num_obs']
        #     nedm_ob.times_validated = nedm_ob.times_validated + 1
        #     nedm_ob.save()
        # except ObjectDoesNotExist:
        #     nedm_ob = m.NeuronEphysDataMap.objects.create(source = ds,
        #                                              ref_text = ref_text,
        #                                              dt_id = table_cell_html_tag_id,
        #                                              changed_by = user,
        #                                              neuron_concept_map = ncm,
        #                                              ephys_concept_map = ecm,
        #                                              val = data_dict['value'],
        #                                              err = data_dict['error'],
        #                                              n = data_dict['num_obs'],
        #                                              times_validated = 0,
        #                                              )
        #
        # # assign experimental factor concept maps
        # if efcm_obs is not None:
        #     # get efcm and add it to nedm
        #     for efcm in efcm_obs:
        #         efcm_html_tag_id = efcm.dt_id
        #         efcmRowInd, efcmColInd = getInd(efcm_html_tag_id, html_tag_id_table)
        #         if efcmRowInd > efcmColInd:
        #             if table_cell_row_ind == efcmRowInd:
        #                 nedm_ob.exp_fact_concept_maps.add(efcm)
        #         else:
        #             if table_cell_col_ind == efcmColInd:
        #                 nedm_ob.exp_fact_concept_maps.add(efcm)
        # nedm_ob.save()
    return None

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