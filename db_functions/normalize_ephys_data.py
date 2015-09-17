import re
import nltk

__author__ = 'shreejoy'


def normalize_nedm_val(nedm):
    # TODO: refactor this into its own function
#    if nedm.source.data_table.needs_expert == True:
#        return None
    val = nedm.val
    ephys_prop_name = nedm.ephys_concept_map.ephys_prop.name
    if ephys_prop_name == 'resting membrane potential' or nedm.ephys_concept_map.ephys_prop.name == 'spike threshold':
        if val > 0:
            val = -nedm.val
    elif ephys_prop_name == 'spike half-width':
        if val > 10 and val < 100:
            return None
        if val >= 100:
            val = val/1000;
    elif ephys_prop_name == 'input resistance':
        if val < 2:
            val = val * 1000;
    elif ephys_prop_name == 'spike width':
        if val > 20:
            return None
    elif nedm.ephys_concept_map.ephys_prop.name == 'spike amplitude' or nedm.ephys_concept_map.ephys_prop.name == 'membrane time constant'\
        or nedm.ephys_concept_map.ephys_prop.name == 'spike width':
            if re.search(r'psp', nedm.source.data_table.table_text, re.IGNORECASE) != None \
            or re.search(r'psc', nedm.source.data_table.table_text, re.IGNORECASE) != None \
            and nedm.times_validated == 0:
                #print nedm.data_table.table_text
                return None
    elif ephys_prop_name == 'sag ratio' or ephys_prop_name == 'adaptation ratio':
        ref_text = nedm.ephys_concept_map.ref_text
        toks = nltk.word_tokenize(ref_text)
        not_match_flag = 0
        for tok in toks:
            if tok == '%':
                rep_val = nedm.val
                print '%', ref_text
                not_match_flag = 1
                val = rep_val/100.0
                break
    elif ephys_prop_name == 'cell capacitance':
        ref_text = nedm.ephys_concept_map.ref_text
        toks = nltk.word_tokenize(ref_text)
        not_match_flag = 0
        for tok in toks:
            if tok.lower() == 'pf':
                val = val
                break
            elif tok.lower() == 'nf':
                rep_val = nedm.val
                not_match_flag = 1
                val = rep_val*1000
                break
    elif ephys_prop_name == 'rheobase':
        ref_text = nedm.ephys_concept_map.ref_text
        toks = nltk.word_tokenize(ref_text)
        not_match_flag = 0
        for tok in toks:
            if tok.lower() == 'pa':
                val = val
                break
            elif tok.lower() == 'na':
                rep_val = nedm.val
                not_match_flag = 1
                val = rep_val*1000
                break
    return val