
import urllib2
import json
import requests
import os
import glob

# import helpful_functions.prog as prog


# get the id's of all the adult mouse ISH datasets
def get_aba_ish_ids():
    """Queries the ABA adult mouse API and returns the image series identifiers for all ISH datasets
    which pass internal quality controls"""
    dataset_search_url = "http://api.brain-map.org/api/v2/data/query.json?criteria=model::SectionDataSet,rma::criteria,[failed$eqfalse],products[abbreviation$eq'Mouse'],treatments[name$eq'ISH'],rma::include,genes,specimen(donor(age)),plane_of_section&num_rows=%d&start_row=%d"
    start_row_index = 0
    num_rows_per_query = 50
    s_query = dataset_search_url % (num_rows_per_query, start_row_index)

    returned_json = json.loads(urllib2.urlopen(s_query).read())
    num_total_expts = returned_json['total_rows']
    print num_total_expts

    ise_id_list = []
    loop_counter = 0
    while start_row_index < num_total_expts:
        print 'start_row_index: %s, num_total_expts: %s' % (start_row_index, num_total_expts)
        s_query = dataset_search_url % (num_rows_per_query, start_row_index)
        returned_json = json.loads(urllib2.urlopen(s_query).read())

        experiment_list = returned_json['msg']
        for expt in experiment_list:
            ise_id_list.append(expt['id'])
        start_row_index += num_rows_per_query
        loop_counter += 1
    return ise_id_list

# get the id's of all the adult mouse ISH datasets
# currently queries for MOB and AOB target voxels
def get_aba_conn_ids():
    """Queries the ABA API and returns the experiment identifiers for all Mouse Connectivity datasets
    which have a projection output or target in either Main Olfactory Bulb or Accessory Olfactory Bulb"""
    dataset_search_url = "http://api.brain-map.org/api/v2/data/query.json?criteria=service::mouse_connectivity_injection_structure[injection_structures$eqgrey][primary_structure_only$eqtrue][target_domain$eqAOB][target_domain$eqMOB]"

    # sets the minimum volumn to consider as a "target hit": .01 seems reasonable to my eye
    target_volumn_thr = .01

    s_query = dataset_search_url
    returned_json = returned_json = json.loads(urllib2.urlopen(s_query).read())
    experiment_list = returned_json['msg']
    num_total_expts = returned_json['num_rows']

    keep_expt_id_list = []

    for expt in experiment_list:
        if float(expt['sum']) > target_volumn_thr:
            keep_expt_id_list.append(expt['id'])
    return keep_expt_id_list

# download ise datasets at the voxel-level
# inputs are ABA dataset ids, i.e., image series ids
def get_aba_voxel_data(dataset_ids, data_type="expr"):
    """Downloads Allen Brain Atlas voxel datasets from API
    Input a list of image series identifiers for specific experiments to download
    see documentation for how to make use of downloaded data files
    Documentation link: http://help.brain-map.org/display/mousebrain/API"""
    # make directory for voxel data files
    if data_type is "conn":
   	    dir_name = "ABA_conn_voxel_data"
    else:
       file_dir = "ABA_ise_voxel_data"
    if not os.path.exists(dir_name):
   	os.makedirs(dir_name)
    os.chdir(dir_name)
    
    exp_grid_url = "http://api.brain-map.org/grid_data/download/%d?include=intensity,density,energy"
     
    os.chdir(file_dir)
    downloaded_files = [f for f in glob.glob("*.zip")]
    num_ises = len(dataset_ids)
    
    for i, ise in enumerate(dataset_ids):
        # prog.prog(i, num_ises)
        filename = '%d.zip' % ise
    
        # if filename exists in list of downloaded files
        if filename in downloaded_files:
            continue
    
        # try downloading file
        s_query = exp_grid_url % (ise)
    
        numFails = 0
        successFlag = False
        while numFails < 5 and successFlag == False:
            try:
                handle = urllib2.urlopen(s_query)
                data = handle.read()
                with open(filename, 'w') as f:
                    f.write(data)
                successFlag = True
            except Exception:
                print ise
                numFails += 1
    
        # try downloading file
        if data_type is "expr":
            metadata_url = "http://api.brain-map.org/api/v2/data/query.xml?criteria=model::SectionDataSet,rma::criteria,[id$eq%d],rma::include,genes,probes,specimen(donor(age)),plane_of_section"
            s_query = metadata_url % (ise)
            filename = '%d_metadata.xml' % ise
    
            numFails = 0
            successFlag = False
            while numFails < 5 and successFlag == False:
                try:
                    handle = urllib2.urlopen(s_query)
                    data = handle.read()
                    with open(filename, 'w') as f:
                        f.write(data)
                    successFlag = True
                except Exception:
                    print ise
                    numFails += 1

