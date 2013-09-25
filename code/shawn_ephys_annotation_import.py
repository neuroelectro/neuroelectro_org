# -*- coding: utf-8 -*-
"""
Created on Sun Jun 02 12:33:54 2013

@author: Shreejoy
"""

# code to import shawn's annotation of OB data


from xml.etree.ElementTree import XML
from urllib import quote_plus, quote
from urllib2 import Request, urlopen, URLError, HTTPError
import neuroelectro.models as m

from metadata_annotation_import import *
from db_add import add_single_article_full
# get article

def load_annotated_article_ephys():
    print 'Updating ephys defs'
    print 'Loading ephys defs'
    #book = xlrd.open_workbook("data/shawn_ob_ephys_annotations.xlsx")
    #book = xlrd.open_workbook("data/ephys_annotations_sjt_7_27_13.xlsx")
    book = xlrd.open_workbook("data/ephys_annotations_sjt_9_25_13.xlsx")
    #os.chdir('C:\Python27\Scripts\Biophys')
    sheet = book.sheet_by_index(0)
    ncols = sheet.ncols
    nrows = sheet.nrows
    
    table= [ [ 0 for i in range(ncols) ] for j in range(nrows ) ]
    for i in range(nrows):
        for j in range(ncols):
            value = sheet.cell(i,j).value
            if isinstance(value, float) and i == 0:
                value = str(int(value))
            if not isinstance(value, float):
                value = value.strip()
            if value is None:
                value = ''
            table[i][j] = value
    return table, ncols, nrows


def process_table2(table, ncols, nrows):
    user = m.User.objects.get(username = 'ShreejoyTripathy') 
    table_norm = [ [ 0 for i in range(6) ] for j in range(nrows ) ]
    table_norm = np.zeros([nrows, 6], dtype='a16')
    for i in range(1,nrows):
        ref = table[i][0]
        pmid = table[i][1]
#        neuron_type = table[i][5]
#n = m.Neuron.objects.filter(name = neuron_type)[0]
        species = table[i][3]
        strain = table[i][4]
        age = table[i][5]
        electrode = table[i][7]
        prep_type = table[i][8]
        jxn_potential = table[i][9]
        temp = table[i][6]
        neuron_type = table[i][2]
        
        tm_mean = table[i][10]
        tm_sem = table[i][11]
        thresh_mean = table[i][12]
        thresh_sem = table[i][13]
        ir_mean = table[i][14]
        ir_sem = table[i][15]
        hw_mean = table[i][16]
        hw_sem = table[i][17]
        amp_mean = table[i][18]
        amp_sem = table[i][19]
        rmp_mean = table[i][20]
        rmp_sem = table[i][21]
        print ref
#        if isinstance(ref, float):
#            ref = str(int(ref))
#        pmidList = get_pmid_from_str(ref)
#        if len(pmidList) > 0:
#            pmid = pmidList[0]
#        else:
#            print "can't find %s" % ref
#            continue
        a = add_single_article_full(pmid)
        n = m.Neuron.objects.filter(name = neuron_type)[0]
        #print a
        
        m.ArticleMetaDataMap.objects.filter(article = a).delete()
        
#        print a
        temp_norm_dict = temp_resolve(unicode(temp))
        #print temp_norm_dict
#        temp_dict_fin = validate_temp_list([temp_norm_dict])
        add_continuous_metadata('RecTemp', temp_norm_dict, a)
        
        age_norm_dict = age_resolve(unicode(age))
        #print age_norm_dict
#        age_dict_fin = validate_age_list([age_norm_dict])
#        print temp_dict_fin
        add_continuous_metadata('AnimalAge', age_norm_dict, a)
        
        weight_norm = weight_resolve(unicode(age))
#        print temp_dict_fin
        add_continuous_metadata('AnimalWeight', weight_norm, a)
        
        jxn_norm = strain_resolve(unicode(jxn_potential))
        if jxn_norm is not '':
            add_nominal_metadata('JxnPotential', jxn_norm, a)
            
        strain_norm = strain_resolve(unicode(strain))
        if strain_norm is not '':
            add_nominal_metadata('Strain', strain_norm, a)
        prep_norm = preptype_resolve(unicode(prep_type)) 
        if prep_norm is not '':
            add_nominal_metadata('PrepType', prep_norm, a)
        electrode_norm = electrodetype_resolve(unicode(electrode))
        #print (electrode, electrode_norm)
        if electrode_norm is not '':
            add_nominal_metadata('ElectrodeType', electrode_norm, a)
        species_norm = species_resolve(unicode(species))
        if species_norm is not '':
            add_nominal_metadata('Species', species_norm, a)
        aft = m.ArticleFullText.objects.get_or_create(article = a)[0]
        afts = m.ArticleFullTextStat.objects.get_or_create(article_full_text = aft)[0]
        afts.metadata_human_assigned = True           
        afts.save()
            
        us_ob = m.UserSubmission.objects.get_or_create(user = user, article = a)[0]
        ds_ob = m.DataSource.objects.get_or_create(user_submission = us_ob)[0]
        ncm_ob = m.NeuronConceptMap.objects.get_or_create(source = ds_ob, added_by = user, neuron = n, 
                                                          times_validated = 1)[0]
        
        add_ephys_nedm(tm_mean, tm_sem, 4, ds_ob, ncm_ob, user)
        add_ephys_nedm(hw_mean, hw_sem, 6, ds_ob, ncm_ob, user)
        add_ephys_nedm(thresh_mean, thresh_sem, 7, ds_ob, ncm_ob, user)
        add_ephys_nedm(ir_mean, ir_sem, 2, ds_ob, ncm_ob, user)
        add_ephys_nedm(rmp_mean, rmp_sem, 3, ds_ob, ncm_ob, user)
        add_ephys_nedm(amp_mean, amp_sem, 5, ds_ob, ncm_ob, user)
        

anon_user = m.get_anon_user()
def process_table(table, ncols, nrows):
    user = m.User.objects.get(username = 'ShawnBurton') 
    table_norm = [ [ 0 for i in range(6) ] for j in range(nrows ) ]
    table_norm = np.zeros([nrows, 6], dtype='a16')
    for i in range(1,nrows):
        ref = table[i][0]
#        neuron_type = table[i][5]
#n = m.Neuron.objects.filter(name = neuron_type)[0]
        species = table[i][2]
        strain = table[i][3]
        age = table[i][4]
        electrode = table[i][6]
        prep_type = table[i][7]
        temp = table[i][5]
        neuron_type = table[i][1]
        
        tm_mean = table[i][8]
        tm_sem = table[i][9]
        thresh_mean = table[i][10]
        thresh_sem = table[i][11]
        ir_mean = table[i][12]
        ir_sem = table[i][13]
        hw_mean = table[i][14]
        hw_sem = table[i][15]
        amp_mean = table[i][16]
        amp_sem = table[i][17]
        rmp_mean = table[i][18]
        rmp_sem = table[i][19]
        print ref
        if isinstance(ref, float):
            ref = str(int(ref))
        pmidList = get_pmid_from_str(ref)
        if len(pmidList) > 0:
            pmid = pmidList[0]
        else:
            print "can't find %s" % ref
            continue
        a = add_single_article_full(pmid)
        n = m.Neuron.objects.filter(name = neuron_type)[0]
        #print a
        
        m.ArticleMetaDataMap.objects.filter(article = a).delete()
        
#        print a
        temp_norm_dict = temp_resolve(unicode(temp))
        #print temp_norm_dict
#        temp_dict_fin = validate_temp_list([temp_norm_dict])
        add_continuous_metadata('RecTemp', temp_norm_dict, a)
        
        age_norm_dict = age_resolve(unicode(age))
        #print age_norm_dict
#        age_dict_fin = validate_age_list([age_norm_dict])
#        print temp_dict_fin
        add_continuous_metadata('AnimalAge', age_norm_dict, a)
        
        weight_norm = weight_resolve(unicode(age))
#        print temp_dict_fin
        add_continuous_metadata('AnimalWeight', weight_norm, a)
        
        strain_norm = strain_resolve(unicode(strain))
        if strain_norm is not '':
            add_nominal_metadata('Strain', strain_norm, a)
        prep_norm = preptype_resolve(unicode(prep_type)) 
        if prep_norm is not '':
            add_nominal_metadata('PrepType', prep_norm, a)
        electrode_norm = electrodetype_resolve(unicode(electrode))
        #print (electrode, electrode_norm)
        if electrode_norm is not '':
            add_nominal_metadata('ElectrodeType', electrode_norm, a)
        species_norm = species_resolve(unicode(species))
        if species_norm is not '':
            add_nominal_metadata('Species', species_norm, a)
        aft = m.ArticleFullText.objects.get_or_create(article = a)[0]
        afts = m.ArticleFullTextStat.objects.get_or_create(article_full_text = aft)[0]
        afts.metadata_human_assigned = True           
        afts.save()
            
        us_ob = m.UserSubmission.objects.get_or_create(user = user, article = a)[0]
        ds_ob = m.DataSource.objects.get_or_create(user_submission = us_ob)[0]
        ncm_ob = m.NeuronConceptMap.objects.get_or_create(source = ds_ob, added_by = user, neuron = n, 
                                                          times_validated = 1)[0]
        
        add_ephys_nedm(tm_mean, tm_sem, 4, ds_ob, ncm_ob, user)
        add_ephys_nedm(hw_mean, hw_sem, 6, ds_ob, ncm_ob, user)
        add_ephys_nedm(thresh_mean, thresh_sem, 7, ds_ob, ncm_ob, user)
        add_ephys_nedm(ir_mean, ir_sem, 2, ds_ob, ncm_ob, user)
        add_ephys_nedm(rmp_mean, rmp_sem, 3, ds_ob, ncm_ob, user)
        add_ephys_nedm(amp_mean, amp_sem, 5, ds_ob, ncm_ob, user)

def add_ephys_nedm(mean_val, sem_val, ephys_pk, ds_ob, ncm_ob, user):
    if mean_val is '':
        return
    if sem_val is '':
        sem_val = None
    ephys_prop_ob = m.EphysProp.objects.get(pk = ephys_pk)
    ecm_ob = m.EphysConceptMap.objects.get_or_create(ephys_prop = ephys_prop_ob, source = ds_ob, added_by = user,
                                                     times_validated = 1)[0]
    ds_ob.save()
#    print ncm_ob.pk
#    print ephys_prop_ob
#    print ecm_ob.pk
#    print mean_val
#    print sem_val
#    print ds_ob.pk
    nedmOb = m.NeuronEphysDataMap.objects.get_or_create(source = ds_ob,
#                                                         ref_text = ref_text,
#                                                         dt_id = dataValIdTag,
                                                         added_by = user,
                                                         neuron_concept_map = ncm_ob,
                                                         ephys_concept_map = ecm_ob,
                                                         val = mean_val,
                                                         val_norm = mean_val,
                                                         err = sem_val,
                                                         times_validated = 1,
                                                         )[0]
#    nedm_ob = m.NeuronEphysDataMap.objects.get_or_create(neuron_concept_map = ncm_ob, 
#                                                         ephys_concept_map = ecm_ob)[0]

def add_data():
	pmidList = get_pmid_from_str(in_str)
	pmid = pmidList[0]

	# create article object with pmid
	a = add_single_article_full(pmid)
	neuron_type = table[i][5]
	n = m.Neuron.objects.filter(name = neuron_type)[0]
	user = m.User.objects.get(username = 'ShawnBurton') 

	# check if any data tables which include an ncm with this neuron?

	# create a user_submission object
	us_ob = m.UserSubmission.objects.get_or_create(article = a, user = user)

	# create a ncm object
	ncm_ob = m.NeuronConceptMap.objects.get_or_create(source = us_ob, neuron = n, added_by = user)
	
	# create an ecm object for each listed ephys prop
	ecm_ob = m.EphysConceptMap.objects.get_or_create(source = us_ob, ephys_prop = e, added_by = user)




def get_pmid_from_str(in_str):
    search_str = quote_plus(in_str)
    searchLink = 'http://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term=%s' % (search_str)
    try:
        handle = urlopen(searchLink)   
        data = handle.read() 
        xml = XML(data) # convert to an xml object so we can apply x-path search fxns to it
        pmidList = [x.text for x in xml.findall('.//Id')] # find xml "Id" elements
        if len(pmidList) > 1:
            pmidList = [pmidList[0]]
    except Exception, e:
        pmidList = []
    return pmidList
# 