# -*- coding: utf-8 -*-
"""
Created on Thu Apr 11 11:32:15 2013

@author: Shreejoy
"""

import neuroelectro.models as m

e = m.EphysProp.objects.get(pk = 3)
#nedm_list = m.NeuronEphysDataMap.objects.filter(ephys_concept_map__ephys_prop = e, val_norm__isnull = False, neuron_concept_map__neuron__pk = 117).order_by('neuron_concept_map__neuron__name')
#d = [nedm_get_attribs(nedm) for nedm in nedm_list]
def nedm_get_attribs(nedm):
    value = nedm.val_norm
    x = 1
    neuron_type = nedm.neuron_concept_map.neuron.name
#    ephys_prop = nedm.ephys_concept_map.ephys_prop.name
#    a = nedm.get_article()
#    title = a.title
#    author_list_str = a.author_list_str
#    journal = a.journal.title
#    attrsDict = {'value' : value, 'neuron_type' : neuron_type, 'ephys_prop': ephys_prop,
#                 'title': title, 'author_list' : author_list_str, 'journal': journal}
    attrsDict = {'y' : value, "x" : neuron_type}
    return attrsDict