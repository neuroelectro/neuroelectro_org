# -*- coding: utf-8 -*-
import article_text_mining.mine_ephys_prop_in_table
import neuroelectro.models as m
import xlrd
import re
import article_text_mining.assign_table_ephys_data as decode
from django.core.exceptions import ObjectDoesNotExist

def update_ephys_defs():
    """Reads in a ephys prop definition file and synonyms file and updates EphysProp objects"""
    print 'Updating ephys defs'
    table, nrows, ncols = load_ephys_defs()
    for i in range(1,nrows):
        ephysProp = table[i][0]
        
        ephysDef = table[i][1]
        ephys_norm_criteria = table[i][2]
        
        rawSyns = table[i][4]
        unit = table[i][5]
        unit_main = table[i][6]
        unit_sub = table[i][7]
        nlex_id = table[i][9]
        ephysOb = m.EphysProp.objects.get_or_create(name = ephysProp)[0]
        if unit_main != '':
            u = m.Unit.objects.get_or_create(name = '%s' % unit_main, prefix = '%s' % unit_sub)[0]
            ephysOb.units = u
        if ephysDef != '':
            ephysOb.definition = ephysDef
        if ephys_norm_criteria != '':
            ephysOb.norm_criteria = ephys_norm_criteria
        if nlex_id != '':
            ephysOb.nlex_id
        ephysOb.save()
        
        # need to parse and sanitize ephys synonym list
        synList = [ephysProp]
        for s in rawSyns.split(','):
            s = re.sub('<[\w/]+>', '', s)
            s = s.strip()
            synList.append(s)
        synList= list(set(synList))
        
        # add new ephys synonym objects and assign to ephys prop
        oldEphysSynObList = ephysOb.synonyms.all()
        newEphysSynObList = []
        for s in synList:
            print s
            ephysSynOb = m.EphysPropSyn.objects.get_or_create(term = s)[0]
            newEphysSynObList.append(ephysSynOb)
            ephysOb.synonyms.add(ephysSynOb)
            
        # now remove stale ephys synonyms
        staleEphysSynObs = list(set(oldEphysSynObList).difference(newEphysSynObList))
        [s.delete() for s in staleEphysSynObs]
    
    # delete any ephys syn objects not connected to an ephys prop
    for synOb in m.EphysPropSyn.objects.all():
        if synOb.ephysprop_set.all().count() == 0: # synonym not associated with any ephys props
            synOb.delete() # delete unconnected ephys prop syn
            
    # lastly, check for any ephys synonyms which share 2 ephys prop terms, indicating a conflict
    for synOb in m.EphysPropSyn.objects.all():
#         if synOb.ephysprop_set.all().count() > 1:
        print synOb
        print synOb.ephysprop_set.all()
        assert synOb.ephysprop_set.all().count() == 1
        
def load_ephys_defs():
    print 'Loading ephys defs'
    book = xlrd.open_workbook("data/Ephys_prop_definitions_8.xlsx")

    sheet = book.sheet_by_index(0)
    ncols = sheet.ncols
    nrows = sheet.nrows

    table= [ [ 0 for i in range(ncols) ] for j in range(nrows ) ]
    for i in range(nrows):
        for j in range(ncols):
            table[i][j] = sheet.cell(i,j).value
    return table, nrows, ncols

def update_ephys_props_and_concept_maps():
    update_spike_overshoot_ecms()
    # remove duplicate Unit fields
    try:
        u = m.Unit.objects.get(pk = 10)
        u.delete()
    except ObjectDoesNotExist:
        print 'Erroneous unit, ratio no longer exists'
        pass
    update_ephys_defs()
    update_firing_rate_ecms()
    update_medium_AHPs()
    clean_robo_mined_ecms()
    #update_other_defined_ecms()
    
def update_spike_overshoot_ecms():
    spike_overshoot_ecms = m.EphysConceptMap.objects.filter(ephys_prop__name = 'spike overshoot')
    spike_peak_prop = m.EphysProp.objects.get(name = 'spike peak')

    for ecm in spike_overshoot_ecms:
        ecm.ephys_prop = spike_peak_prop
        ecm.save()
    try:
        spike_overshoot_prop = m.EphysProp.objects.get(name = 'spike overshoot')
        [syn.delete() for syn in spike_overshoot_prop.synonyms.all()]
        spike_overshoot_prop.delete()
    except ObjectDoesNotExist:
        print 'Spike overshoot object does not exist'
        pass
    
def update_medium_AHPs():
    medium_AHP_amp_ep = m.EphysProp.objects.get_or_create(name = 'medium AHP amplitude')[0]
    medium_AHP_duration_ep = m.EphysProp.objects.get_or_create(name = 'medium AHP duration')[0]
        
    medium_list = ['medium', 'mAHP', 'm AHP']
    save_prop_flag = True
    
    ahp_amp_ecms = m.EphysConceptMap.objects.filter(ephys_prop__name__icontains = 'AHP amplitude')
    ahp_duration_ecms = m.EphysConceptMap.objects.filter(ephys_prop__name__icontains = 'AHP duration')
    
    update_ephys_props_from_list(ahp_amp_ecms, medium_list, medium_AHP_amp_ep, save_prop_flag)
    update_ephys_props_from_list(ahp_duration_ecms, medium_list, medium_AHP_duration_ep, save_prop_flag)

def update_firing_rate_ecms():
    max_ep = m.EphysProp.objects.get(name = 'maximum firing rate')
    spont_ep = m.EphysProp.objects.get(name = 'spontaneous firing rate')
    firing_freq_ep = m.EphysProp.objects.get(name = 'firing frequency')
    
    max_list = ['max', 'peak', 'instant']
    spont_list = ['spont', 'rest']
    save_prop_flag = True
    
    firing_freq_ecms = m.EphysConceptMap.objects.filter(ephys_prop__in = [firing_freq_ep])
    
    update_ephys_props_from_list(firing_freq_ecms, max_list, max_ep, save_prop_flag)
    update_ephys_props_from_list(firing_freq_ecms, spont_list, spont_ep, save_prop_flag)

def update_ephys_props_from_list(ecms_to_check, match_string_list, target_ephys_prop_object, save_prop_flag=False):
    for ecm in ecms_to_check:
        flag = False
        
        ref_text = ecm.ref_text
        note = ecm.note
        if ref_text and any(substring in ref_text.lower() for substring in match_string_list):
            flag = True
        elif note and any(substring in note.lower() for substring in match_string_list):
            flag = True
        if flag:
            # update ecm object
            if save_prop_flag:
                ecm.ephys_prop = target_ephys_prop_object
                ecm.save()
            else:
                print (ecm.ref_text, ecm.note, target_ephys_prop_object)

def clean_robo_mined_ecms():
    """Removes poorly mined EphysConceptMap objects based on updated ephys synonyms"""
    ecm_list = m.EphysConceptMap.objects.all()
    ephysSyns = m.EphysPropSyn.objects.all()
    ephysSynList = [e.term.lower() for e in ephysSyns]
    for ecm in ecm_list:
        # check if ecm is validated, if so, leave it alone
        if ecm.times_validated > 0:
            continue
        else:
            article_text_mining.mine_ephys_prop_in_table.update_ecm_using_text_mining(ecm, ephysSynList)
                
def update_other_defined_ecms():
    """Updates ephys prop assigned to previously defined ecm's tagged as 'other'"""
    
    other_ephys_prop = m.EphysProp.objects.get(name = 'other')
    ecm_list = m.EphysConceptMap.objects.filter(ephys_prop = other_ephys_prop)
    
    ephysSyns = m.EphysPropSyn.objects.all()
    ephysSynList = [e.term.lower() for e in ephysSyns]
    for ecm in ecm_list:
        
        # get the closest matching ephys prop given the table header reference text
        matched_ephys_prop = article_text_mining.mine_ephys_prop_in_table.match_ephys_header(ecm.ref_text, ephysSynList)
        if matched_ephys_prop is None: # no ephys props matched 
            continue
        if matched_ephys_prop != ecm.ephys_prop: # different found prop than existing one
            print 'changing %s, to prop: %s, from prop: %s' %(ecm.ref_text, matched_ephys_prop, ecm.ephys_prop)
            
        ecm.ephys_prop = matched_ephys_prop # update the ecm
        ecm.changed_by = m.get_robot_user()
        ecm.save()