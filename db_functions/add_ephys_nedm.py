from neuroelectro_org.neuroelectro import models as m
from neuroelectro_org.article_text_mining import pubmed_functions 
import article_text_mining.resolve_data_float as resolve
from django.core.exceptions import ObjectDoesNotExist
# Add a String ephys value of the form 'value +/- error(num iterations)' to the database
#
# Ephys property name
# Ephys property value
# Pubmed article id
# Neuron type for this ephys property
# User who submitted the property/value pair
def add_ephys_nedm(ephys_name, ephys_value, pmid, neuron_type, user, overwrite=True):
    if ephys_value is '':
        return
    
    ephys_value_list = resolve.resolve_data_float(ephys_value)
    
    if not 'error' in ephys_value_list:
        ephys_value_list['error'] = None
        
    if not 'numCells' in ephys_value_list:
        ephys_value_list['numCells'] = None
    
    a = pubmed_functions.add_single_article_full(pmid)

    n = m.Neuron.objects.filter(name = neuron_type)[0]
    us_ob = m.UserSubmission.objects.get_or_create(user = user, article = a)[0]
    ds_ob = m.DataSource.objects.get_or_create(user_submission = us_ob)[0]
    ncm_ob = m.NeuronConceptMap.objects.get_or_create(source = ds_ob, added_by = user, neuron = n, 
                                                        times_validated = 1)[0]
    
    ephys_prop_ob = m.EphysProp.objects.get(name = ephys_name)
    ecm_ob = m.EphysConceptMap.objects.get_or_create(ephys_prop = ephys_prop_ob, source = ds_ob, added_by = user,
                                                        times_validated = 1)[0]
    ds_ob.save()

    try:
        nedm = m.NeuronEphysDataMap.objects.get(source = ds_ob,
                                         added_by = user,
                                         neuron_concept_map = ncm_ob,
                                         ephys_concept_map = ecm_ob)
        if overwrite is True:
            nedm.delete()
    except ObjectDoesNotExist:
        pass
    # if overwrite is false, just make a new nedm, otherwise find the old nedm (if it exists) and then overwrite it

    m.NeuronEphysDataMap.objects.get_or_create(source = ds_ob,
                                               added_by = user,
                                               neuron_concept_map = ncm_ob,
                                               ephys_concept_map = ecm_ob,
                                               val = ephys_value_list['value'],
                                               val_norm = ephys_value_list['value'],
                                               err = ephys_value_list['error'],
                                               times_validated = 1,
                                               n = ephys_value_list['numCells'],
                                             )[0]
