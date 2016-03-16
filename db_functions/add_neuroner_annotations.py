import neuroelectro.models as m

from sherlok import Sherlok
from neuroner.normalize import clean_annotations, normalize_annots

import json
from scripts.dbrestore import prog
from neuroner.similarity import similarity2, similarity


def get_neuroner_annotations(neuron_long_name):

    sherlok_instance = Sherlok('neuroner')
    r = sherlok_instance.annotate(neuron_long_name)
    annot_dict = clean_annotations(r.annotations, neuron_long_name, return_dict = False)

    return annot_dict

def calculate_neuroner_similarity(query_annotations, target_annotations, symmetric = False, use_inter_similarity = False):
    # merely a wrapper around similarity2 similarity function in neuroner similarity
    sim = similarity2(query_annotations, target_annotations, symmetric, use_inter_similarity)
    return sim[0]


def assign_neuroner_ids():
    """Iterate through all neuron concept maps and assign neuroner ontology ids"""

    ncms = m.NeuronConceptMap.objects.filter(times_validated__gt = 0)

    # actually update objects
    cm_expert_list_len = len(ncms)
    for i,cm in enumerate(ncms):
        prog(i,cm_expert_list_len)
        if cm.neuron_long_name:
            neuron_pref_name = cm.neuron_long_name
        else:
            neuron_pref_name = cm.neuron.name
        neuroner_ids = get_neuroner_annotations(neuron_pref_name)

        json_neuroner_ids = json.dumps(neuroner_ids)
        # if annotations are unchanged, then don't save and continue
        if neuroner_ids is cm.neuroner_ids:
            continue

        cm.neuroner_ids = json_neuroner_ids

        # don't actually update the changed date
        hcm = cm.history.all()[0]
        cm._history_date = hcm.history_date
        cm.save(new_history_time = True)