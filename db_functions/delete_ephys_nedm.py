"""
Created on Wed Sep 03 14:14:14 2014

@author: Dmitry

Given a neuronephysdatamap entry ID - delete that entry and its relatives from UserSubmission, DataSource and NeuronEphysDataMap, EphysConceptMap and NeuronConceptMap tables in neuroelectro database
"""
from neuroelectro_org.neuroelectro import models as m
from neuroelectro_org.article_text_mining import pubmed_functions 
import article_text_mining.resolve_data_float as resolve
from django.core.exceptions import ObjectDoesNotExist
#
# Ephys property name
# Ephys property value
# Pubmed article id
# Neuron type for this ephys property
# User who submitted the property/value pair
def delete_ephys_nedm(nedm_id):
    #go through datasource id
    # delete: 
    #    usersubmission
    #    datasource
    #    nedm object
    #    ephys_concept_map
    #    neuron_concept_map
    
    
    if nedm_id is '':
        print "Invalid nedm_id: %s" % nedm_id
        return False
    
    nedm_ob = m.NeuronEphysDataMap.objects.filter(id = nedm_id)[0]
    
    if not nedm_ob:
        print "NEDM object with id %s does not exist" % nedm_id
        return False
    
    ds_ob_list = m.NeuronEphysDataMap.objects.filter(source_id = nedm_ob.source_id)
    delete_neuron_entry = m.EphysConceptMap.objects.filter(id = nedm_ob.ephys_concept_map_id).count() == 1
    
    # TODO: both conceptmap entries are being deleted. 
    if m.NeuronConceptMap.objects.filter(id = nedm_ob.neuron_concept_map_id).count() == 1:
        m.EphysConceptMap.objects.filter(id = nedm_ob.ephys_concept_map_id).delete()
        
    if delete_neuron_entry:
        m.NeuronConceptMap.objects.filter(id = nedm_ob.neuron_concept_map_id).delete()
        
    if ds_ob_list.count() == 1:
        m.DataSource.objects.filter(id = nedm_ob.source_id).delete()
        m.UserSubmission.objects.filter(id = ds_ob_list[0].user_submission_id).delete()
     
    m.NeuronEphysDataMap.objects.filter(id = nedm_id).delete()
    
   
#     
#     ephys_value_list = resolve.resolve_data_float(ephys_value)
#     
#     if not 'error' in ephys_value_list:
#         ephys_value_list['error'] = None
#         
#     if not 'numCells' in ephys_value_list:
#         ephys_value_list['numCells'] = None
#     
#     a = pubmed_functions.add_single_article_full(pmid)
# 
#     n = m.Neuron.objects.filter(name = neuron_type)[0]
#     us_ob = m.UserSubmission.objects.get_or_create(user = user, article = a)[0]
#     ds_ob = m.DataSource.objects.get_or_create(user_submission = us_ob)[0]
#     ncm_ob = m.NeuronConceptMap.objects.get_or_create(source = ds_ob, added_by = user, neuron = n, 
#                                                         times_validated = 1)[0]
#     
#     ephys_prop_ob = m.EphysProp.objects.get(name = ephys_name)
#     ecm_ob = m.EphysConceptMap.objects.get_or_create(ephys_prop = ephys_prop_ob, source = ds_ob, added_by = user,
#                                                         times_validated = 1)[0]
#     ds_ob.save()
# 
#     try:
#         nedm = m.NeuronEphysDataMap.objects.get(source = ds_ob,
#                                          added_by = user,
#                                          neuron_concept_map = ncm_ob,
#                                          ephys_concept_map = ecm_ob)
#         if overwrite is True:
#             nedm.delete()
#     except ObjectDoesNotExist:
#         pass
#     # if overwrite is false, just make a new nedm, otherwise find the old nedm (if it exists) and then overwrite it
# 
#     m.NeuronEphysDataMap.objects.get_or_create(source = ds_ob,
#                                                added_by = user,
#                                                neuron_concept_map = ncm_ob,
#                                                ephys_concept_map = ecm_ob,
#                                                val = ephys_value_list['value'],
#                                                val_norm = ephys_value_list['value'],
#                                                err = ephys_value_list['error'],
#                                                times_validated = 1,
#                                                n = ephys_value_list['numCells'],
#                                              )[0]
