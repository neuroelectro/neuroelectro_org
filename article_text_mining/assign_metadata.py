# -*- coding: utf-8 -*-
"""
Created on Wed Apr 10 13:41:52 2013

@author: Shreejoy
Modified by: Dmitrii Tebaikin
"""
import neuroelectro.models as m
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from html_process_tools import getMethodsTag, strip_tags
import re
import nltk
from assign_table_ephys_data import resolve_data_float
import numpy as np
import string
import os

species_list = ['Rats', 'Mice', 'Guinea Pigs', 'Songbirds', 'Turtles', 'Cats', 'Zebrafish', 'Macaca mulatta', 'Goldfish', 'Aplysia', 'Xenopus']
strain_list = ['Rats, Inbred F344', 'Rats, Long-Evans', 'Rats, Sprague-Dawley', 'Rats, Wistar', 'Mice, Inbred C57BL', 'Mice, Inbred BALB C', 'Mice, Transgenic', 'Rats, Transgenic']

species_obj_list = m.MeshTerm.objects.filter(term__in=species_list)
strain_obj_list = m.MeshTerm.objects.filter(term__in=strain_list)
robot_user = m.get_robot_user()

patch_mesh = m.MeshTerm.objects.get(term = 'Patch-Clamp Techniques')
whole_re = re.compile(ur'whole\scell|whole-cell|patch\sclamp|patch-clamp' , flags=re.UNICODE|re.IGNORECASE)
sharp_re = re.compile(ur'sharp.+electro' , flags=re.UNICODE|re.IGNORECASE)

culture_mesh = m.MeshTerm.objects.get(term = 'Cell Culture Techniques')
in_silico_mesh = m.MeshTerm.objects.get(term = 'Computer Simulation')
culture_re = re.compile(ur'culture' , flags=re.UNICODE|re.IGNORECASE)
in_vitro_re = re.compile(ur'slice|in\svitro' , flags=re.UNICODE|re.IGNORECASE)
in_vivo_re = re.compile(ur'in\svivo' , flags=re.UNICODE|re.IGNORECASE)
model_re = re.compile(ur'model' , flags=re.UNICODE|re.IGNORECASE)

p_age_re = re.compile(ur'P(\d+)-P(\d+)|P(\d+)-(\d+)|P(\d+)–P(\d+)|P(\d+)–(\d+)', flags=re.UNICODE|re.IGNORECASE)
#p_age_re = re.compile(ur'P(\d+)', flags=re.UNICODE|re.IGNORECASE)
day_re = age_re = re.compile(ur'\sday\sold|\sday\sold|\sage.+\sday' , flags=re.UNICODE|re.IGNORECASE)
week_re = age_re = re.compile(ur'\sweek\sold|\sweek\sold|\sage.+\sweek' , flags=re.UNICODE|re.IGNORECASE)

celsius_re = re.compile(ur'record.+°C|experiment.+°C', flags=re.UNICODE|re.IGNORECASE)
room_temp_re = re.compile(ur'record.+room\stemperature|experiment.+room temperature', flags=re.UNICODE|re.IGNORECASE)

jxn_re = re.compile(ur'junction\spotential' , flags=re.UNICODE|re.IGNORECASE)
jxn_not_re = re.compile(ur'\snot\s.+junction\spotential|junction\spotential.+\snot\s|\sno\s.+junction\spotential|junction\spotential.+\sno\s' , flags=re.UNICODE|re.IGNORECASE)

conc_re = re.compile(ur'in\sMM|\sMM\s|\(MM\)', flags=re.UNICODE|re.IGNORECASE)
mgca_re = re.compile(ur'\s([Mm]agnesium|[Cc]alcium)|-(Mg|Ca)|(Ca|Mg)([A-Z]|-|\s)', flags=re.UNICODE)
na_re = re.compile(ur'\s(di)?[Ss]odium|-Na[^+]|Na([A-Z]|\d|-|gluc)', flags=re.UNICODE)
mg_re = re.compile(ur'\s[Mm]agnesium|-Mg[^\d+]|Mg([A-Z]|-|\d[^+])', flags=re.UNICODE)
ca_re = re.compile(ur'\s[Cc]alcium|-Ca[^\d+]|Ca([A-Z]|-|\d[^+])', flags=re.UNICODE)
k_re = re.compile(ur'\s(di)?[Pp]otassium|-K[^+]|K([A-Z]|\d|-|gluc)', flags=re.UNICODE)
cl_re = re.compile(ur'(di)?(Cl|[Cc]hlorine|[Cc]hloride)\d?', flags=re.UNICODE)
record_re = re.compile(ur'external|perfus|extracellular|superfuse|record.+(ACSF|[Aa]rtificial\s[Cc]erebrospinal\s[Ff]luid)|([Aa]rtificial\s[Cc]erebrospinal\s[Ff]luid|ACSF).+record|chamber.+(ACSF|record|[Aa]rtificial\s[Cc]erebrospinal\s[Ff]luid)|(ACSF|record|[Aa]rtificial\s[Cc]erebrospinal\s[Ff]luid).+chamber', flags=re.UNICODE|re.IGNORECASE)
pipette_re = re.compile(ur'internal|intracellular|pipette|electrode', flags=re.UNICODE|re.IGNORECASE)
cutstore_re = re.compile(ur'incubat|stor|slic|cut|dissect|remove|ACSF|\sbath\s', flags=re.UNICODE|re.IGNORECASE)
num_re = re.compile(ur'(\[|\{|\\|/|\s|\(|~|≈)((\d*\.\d+|\d+)\s*(-|‒|—|―|–)\s*(\d*\.\d+|\d+)|\d*\.\d+|\d+)', flags=re.UNICODE|re.IGNORECASE)
ph_re = re.compile(ur'[\s\(,;]pH', flags=re.UNICODE)
other_re = re.compile(ur'[Ss]ubstitut|[Jj]unction\spotential|PCR|\sgel\s|Gel\s|\sreplace|\sincrease|\sreduc|\sstimul|\somit', flags=re.UNICODE)

ltp_re = re.compile(ur'ltp|long\sterm\spotentiation', flags=re.UNICODE|re.IGNORECASE)
control_re = re.compile(ur'control|wild\s*.?\s*type|\+/\+|[\(\s;,\\{\[]wt', flags=re.UNICODE|re.IGNORECASE)
n_re = re.compile(ur'n\s*=\s*\d+', flags=re.UNICODE|re.IGNORECASE)
hippocampus_re = re.compile(ur'hippocamp|CA1', flags=re.UNICODE|re.IGNORECASE)

#find the related RE's to the Synaptic Plastisity:
plusMinus_re = re.compile(ur'±', re.UNICODE)
# EPSP_re=re.compile(ur'\sEPSP\s|\sEPSPs\s', re.UNICODE)
# fEPSP_re=re.compile(ur'\sfEPSP\s|\sfEPSPs\s',re.UNICODE)
# LPSP_re=re.compile(ur'\sLPSP\|\sLPSPs\s',re.UNICODE)
# L_LTP_re=re.compile(ur'\sL-LTP\s',re.UNICODE)
# E_LTP_re=re.compile(ur'\sE-LTP\s',re.UNICODE)
# potentiation_re=re.comple(ur'\spotentiation\s|\sPotentiation\s',re.UNICODE)
# mEPSC_re=re.compile(ur'\smEPSC\s', re.UNICODE)
units_re = re.compile(ur'm[sS]|mV|Hz|hz|hertz|min|pA|MΩ|mΩ|Ω|ohm|°C|(MΩ)|(mV)|(ms)|m[lL]', re.UNICODE)

BRAT_FILE_PATH = "/Users/dtebaykin/Documents/brat-v1.3_Crunchy_Frog/data/LTP temp/"

def update_amd_obj(article, metadata_ob, ref_text_ob = None, user = None, note = None):
    amdms = m.ArticleMetaDataMap.objects.filter(article = article)
    
    if not user:
        user = robot_user
    
    for amdm in amdms:
        if amdm.metadata.name == metadata_ob.name:
            amdm.metadata = metadata_ob
            amdm.times_validated += 1
            amdm.note = note
            amdm.ref_text_ob = ref_text_ob
            amdm.changed_by = user
            amdm.save()
            return
        
    m.ArticleMetaDataMap.objects.create(article = article, 
                                        metadata = metadata_ob, 
                                        ref_text = ref_text_ob,
                                        note = note,
                                        added_by = user)

def assign_species(article):
    terms = article.terms.all()
    for mesh in species_obj_list:
        if mesh in terms:
            metadata_ob = m.MetaData.objects.get_or_create(name='Species', value=mesh.term)[0]
            update_amd_obj(article, metadata_ob)

def assign_electrode_type(article):
    metadata_added = False
    if article.articlefulltext_set.all().count() > 0:
        full_text_ob = article.articlefulltext_set.all()[0]
        full_text = full_text_ob.get_content()
        methods_tag = getMethodsTag(full_text, article)
        if methods_tag is None:
            print (article.pmid, article.title, article.journal)
        else:
            text = re.sub('\s+', ' ', methods_tag.text)    
            sents = nltk.sent_tokenize(text)
            electrode_set = set()
            
            for s in sents:
                if whole_re.findall(s):
        #            wholeCellSet.add(art)
        #            print 'whole: ' + art.title
        #            print str(idx) + ' : ' + s.encode("iso-8859-15", "replace")
                    electrode_set.add('Patch-clamp')
        #            electrode_list.append('Whole-cell')
        #            electrode_list_text_mine.append('Whole-cell')
                if sharp_re.findall(s):
        #            sharpSet.add(art)
        #            print 'sharp: ' + art.title
        #            print str(idx) + ' : ' + s.encode("iso-8859-15", "replace")
                    electrode_set.add('Sharp')
            if 'Patch-clamp' in electrode_set:
                metadata_ob = m.MetaData.objects.get_or_create(name='ElectrodeType', value='Patch-clamp')[0]
                update_amd_obj(article, metadata_ob)
                metadata_added = True
            if 'Sharp' in electrode_set:
                metadata_ob = m.MetaData.objects.get_or_create(name='ElectrodeType', value='Sharp')[0]   
                update_amd_obj(article, metadata_ob)
                metadata_added = True
            aftStatOb = m.ArticleFullTextStat.objects.get_or_create(article_full_text = full_text_ob)[0]
            aftStatOb.methods_tag_found = True
            aftStatOb.save()
    if metadata_added == False:
        mesh_terms = article.terms.all()
        if patch_mesh in mesh_terms:
            metadata_ob = m.MetaData.objects.get_or_create(name='ElectrodeType', value='Patch-clamp')[0]
            update_amd_obj(article, metadata_ob)
            metadata_added = True
#    if metadata_added == True:
#        print article
#        mds = m.MetaData.objects.filter(article = article)
#        print [(md.name, md.value) for md in mds]

def assign_strain(article):
    terms = article.terms.all()
    for mesh in strain_obj_list:
        if mesh in terms:
            metadata_ob = m.MetaData.objects.get_or_create(name='Strain', value=mesh.term)[0]
            update_amd_obj(article, metadata_ob)

def assign_prep_type(article):
    metadata_added = False
    if article.articlefulltext_set.all().count() > 0:
        full_text_ob = article.articlefulltext_set.all()[0]
        full_text = full_text_ob.get_content()
        methods_tag = getMethodsTag(full_text, article)
        if methods_tag is None:
            print (article.pmid, article.title, article.journal)
        else:
            text = re.sub('\s+', ' ', methods_tag.text)    
            sents = nltk.sent_tokenize(text)
            prep_type_set = set()
            
            for s in sents:
                if culture_re.findall(s):
                    prep_type_set.add('cell culture')
                if in_vitro_re.findall(s):
                    prep_type_set.add('in vitro')
                if in_vivo_re.findall(s):
                    prep_type_set.add('in vivo')
                if model_re.findall(s):
                    prep_type_set.add('model')
            if 'cell culture' in prep_type_set:
                metadata_ob = m.MetaData.objects.get_or_create(name='PrepType', value='cell culture')[0]
                update_amd_obj(article, metadata_ob)
                metadata_added = True
            if 'in vitro' in prep_type_set:
                metadata_ob = m.MetaData.objects.get_or_create(name='PrepType', value='in vitro')[0]   
                update_amd_obj(article, metadata_ob)
                metadata_added = True
            if 'in vivo' in prep_type_set:
                metadata_ob = m.MetaData.objects.get_or_create(name='PrepType', value='in vivo')[0]   
                update_amd_obj(article, metadata_ob)
                metadata_added = True
#            if 'model' in prep_type_set:
#                metadata_ob = m.MetaData.objects.get_or_create(name='PrepType', value='model', added_by = robot_user)[0]   
#                article.metadata.add(metadata_ob)
#                metadata_added = True
            aftStatOb = m.ArticleFullTextStat.objects.get_or_create(article_full_text = full_text_ob)[0]
            aftStatOb.methods_tag_found = True
            aftStatOb.save()
    if metadata_added == False:
        mesh_terms = article.terms.all()
        if culture_mesh in mesh_terms:
            metadata_ob = m.MetaData.objects.get_or_create(name='PrepType', value='cell culture')[0]
            update_amd_obj(article, metadata_ob)
        if in_silico_mesh in mesh_terms:
            metadata_ob = m.MetaData.objects.get_or_create(name='PrepType', value='model')[0]
            update_amd_obj(article, metadata_ob)

def assign_rec_temp(article):
# find a sentence that mentions recording and temperature or degree celsius
    full_text_ob = article.articlefulltext_set.all()[0]
    ft = full_text_ob.get_content()
    methods_tag = getMethodsTag(ft, article)
    if methods_tag is None:
        print (article.pmid, article.title, article.journal)
    else:
        text = re.sub('\s+', ' ', methods_tag.text)
        temp_dict_list = []
        sents = nltk.sent_tokenize(text)
        for s in sents:
    #        print s.encode("iso-8859-15", "replace")
            if celsius_re.findall(s):
    #            print article.pk
    #            print s.encode("iso-8859-15", "replace")
                degree_ind = s.rfind(u'°C')
                min_sent_ind = 0
                max_sent_ind = len(s)
                degree_close_str = s[np.maximum(min_sent_ind, degree_ind-20):np.minimum(max_sent_ind, degree_ind+1)]
                retDict = resolve_data_float(degree_close_str)
                if 'value' in retDict:
                    temp_dict_list.append(retDict)
            elif room_temp_re.findall(s):
    #            print article.pk
    #            print s.encode("iso-8859-15", "replace")
                retDict = {'value':22.0, 'max_range' : 24.0, 'min_range': 20.0}
                temp_dict_list.append(retDict)
        if len(temp_dict_list) > 0:
    #        print temp_dict_list
            temp_dict_fin = validate_temp_list(temp_dict_list)
    #        print temp_dict_fin
            if temp_dict_fin:
                min_range = None
                max_range = None
                stderr = None
                if 'min_range' in temp_dict_fin:
                    min_range = temp_dict_fin['min_range']
                if 'max_range' in temp_dict_fin:
                    max_range = temp_dict_fin['max_range']
                if 'error' in temp_dict_fin:
                    stderr = temp_dict_fin['error']
                
                cont_value_ob = m.ContValue.objects.filter(mean = temp_dict_fin['value'], min_range = min_range, max_range = max_range, stderr = stderr)[0]
                if not cont_value_ob:
                    cont_value_ob = m.ContValue.objects.get_or_create(mean = temp_dict_fin['value'], min_range = min_range, max_range = max_range, stderr = stderr)[0]
                metadata_ob = m.MetaData.objects.get_or_create(name='RecTemp', cont_value=cont_value_ob)[0]
                update_amd_obj(article, metadata_ob)
                aftStatOb = m.ArticleFullTextStat.objects.get_or_create(article_full_text = full_text_ob)[0]
                aftStatOb.methods_tag_found = True
                aftStatOb.save()
            # TODO: assign metadata!
        
def validate_temp_list(temp_dict_list):
    if len(temp_dict_list) == 1:
        temp_dict_fin = temp_dict_list[0]
    else:
        value_list = [l['value'] for l in temp_dict_list]
        if max(value_list) - min(value_list) > 5:
            return None
        else:
            temp_dict_fin = dict()
            for l in temp_dict_list:
                temp_dict_fin = dict(temp_dict_fin.items() + l.items())
    if temp_dict_fin['value'] > 18 and temp_dict_fin['value'] < 42:
        return temp_dict_fin
    else:
        return None
        
def assign_animal_age(article):
# TODO: find a sentence that mentions recording and temperature or degree celsius
    full_text_ob = article.articlefulltext_set.all()[0]
    ft = full_text_ob.get_content()
    methods_tag = getMethodsTag(ft, article)
    if methods_tag is None:
        print (article.pmid, article.title, article.journal)
    else:
        text = re.sub('\s+', ' ', methods_tag.text)
        age_dict_list = []
        sents = nltk.sent_tokenize(text)
        for s in sents:
    #        print s.encode("iso-8859-15", "replace")
            if p_age_re.findall(s):
    #            print article.pk
#                print s.encode("iso-8859-15", "replace")
#                print 'Pnumber'
                p_iter = re.finditer(ur'P\d', s) 
                matches = [(match.start(0), match.end(0)) for match in p_iter]
                if len(matches) > 0:
                    p_ind = matches[-1][0]
        #            p_ind = s.rfind(ur'P\d')
                    min_sent_ind = 0
                    max_sent_ind = len(s)
                    p_close_str = s[np.maximum(min_sent_ind, p_ind-15):np.minimum(max_sent_ind, p_ind+15)]
        #            print p_close_str
                    p_close_str = p_close_str.translate(dict((ord(c), u'') for c in string.ascii_letters)).strip()
        #            print p_close_str
                    retDict = resolve_data_float(p_close_str)
        #            print retDict
                    if 'value' in retDict:
                        age_dict_list.append(retDict)
            elif day_re.findall(s):
    #            print article.pk
#                print s.encode("iso-8859-15", "replace")
#                print 'day'
                p_iter = re.finditer(ur'\sday', s) 
                matches = [(match.start(0), match.end(0)) for match in p_iter]
                if len(matches) > 0:
                    p_ind = matches[-1][0]
        #            p_ind = s.rfind(ur'P\d')
                    min_sent_ind = 0
                    max_sent_ind = len(s)
                    p_close_str = s[np.maximum(min_sent_ind, p_ind-15):np.minimum(max_sent_ind, p_ind+15)]
        #            print p_close_str
                    p_close_str = p_close_str.translate(dict((ord(c), u'') for c in string.ascii_letters)).strip()
        #            print p_close_str
                    retDict = resolve_data_float(p_close_str)
        #            print retDict
                    if 'value' in retDict:
                        age_dict_list.append(retDict)
        if len(age_dict_list) > 0:
    #        print temp_dict_list
    #        print age_dict_list
            age_dict_fin = validate_age_list(age_dict_list)
    #        print age_dict_fin
            if age_dict_fin:
                min_range = None
                max_range = None
                stderr = None
                if 'min_range' in age_dict_fin:
                    min_range = age_dict_fin['min_range']
                if 'max_range' in age_dict_fin:
                    max_range = age_dict_fin['max_range']
                if 'error' in age_dict_fin:
                    stderr = age_dict_fin['error']
                cont_value_ob = m.ContValue.objects.get_or_create(mean = age_dict_fin['value'], min_range = min_range,
                                                                  max_range = max_range, stderr = stderr)[0]
                metadata_ob = m.MetaData.objects.get_or_create(name='AnimalAge', cont_value=cont_value_ob)[0]
                update_amd_obj(article, metadata_ob)
                aftStatOb = m.ArticleFullTextStat.objects.get_or_create(article_full_text = full_text_ob)[0]
                aftStatOb.methods_tag_found = True
                aftStatOb.save()
    #            print metadata_ob

def validate_age_list(age_dict_list):
    if len(age_dict_list) == 1:
        age_dict_fin = age_dict_list[0]
    else:
        value_list = [l['value'] for l in age_dict_list]
        if max(value_list) - min(value_list) > 10:
            return None
        else:
            age_dict_fin = dict()
            for l in age_dict_list:
                age_dict_fin = dict(age_dict_fin.items() + l.items())
    if age_dict_fin['value'] > 0 :
        return age_dict_fin
    else:
        return None

def assign_jxn_potential(article):
    if article.articlefulltext_set.all().count() > 0:
        full_text_ob = article.articlefulltext_set.all()[0]
        full_text = full_text_ob.get_content()
        methods_tag = getMethodsTag(full_text, article)
        if methods_tag is None:
            print (article.pmid, article.title, article.journal)
        else:
            text = re.sub('\s+', ' ', methods_tag.text)    
            sents = nltk.sent_tokenize(text)
            jxn_pot_set = set()
            
            for s in sents:
                if jxn_not_re.findall(s):
                    jxn_pot_set.add('Not corrected')
                elif jxn_re.findall(s):
                    jxn_pot_set.add('Corrected')
            if 'Corrected' in jxn_pot_set:
                metadata_ob = m.MetaData.objects.get_or_create(name='JxnPotential', value='Corrected')[0]
                update_amd_obj(article, metadata_ob)
            if 'Not corrected' in jxn_pot_set:
                metadata_ob = m.MetaData.objects.get_or_create(name='JxnPotential', value='Not corrected')[0]   
                update_amd_obj(article, metadata_ob)
            aftStatOb = m.ArticleFullTextStat.objects.get_or_create(article_full_text = full_text_ob)[0]
            aftStatOb.methods_tag_found = True
            aftStatOb.save()

# find a number closest to the location defined by regex in the given fragment that has a space, a slash, a backslash or an opening bracket before it
def find_closest_num(fragment, regex):
    fragment = " " + fragment
    location = regex.search(fragment)
    frag_nums = [m.span() for m in re.finditer(num_re, fragment)]
    if frag_nums:
        closest_num = None
        closest_num_start = -10000
        for frag_num in frag_nums:
            if abs(location.start() - frag_num[0]) < abs(location.start() - closest_num_start):
                closest_num_start = frag_num[0]
                closest_num = fragment[frag_num[0] + 1 : frag_num[1]]
        return closest_num
    return None

# Convert a string representing a positive number (Ex: 31.2) or a range of positive numbers (Ex: 12.3 - 14.5) to a float
# WARNING: ignores negative signs
#
# num is a number or a range of numbers as a string
# Returns the number or the average of the range of numbers as a float
def get_num(num):
    if num:
        num_list = re.findall('\d*\.\d+|\d+', num)
        if len(num_list) == 0:
            return float('NaN')
        elif len(num_list) == 1:
            return float(num_list[0])
        else:
            sum_num = 0
            for num in num_list:
                sum_num += float(num)
                
            return sum_num / len(num_list)
        
# Find any occurrences of the element within the sentence and extract the number closest to each match
def extract_conc(sentence, text_wrap, elem_re, article, soln_name, user):
    # TODO: mine for full compounds, not just specific ions (maybe)
    total_conc = 0
    actual_pH_num = -1
    
    text_ob = m.ReferenceText.objects.get_or_create(text = (text_wrap[0] + " " + sentence + " " + text_wrap[3]).encode('utf8'))[0]
    
    # cut off the part of the sentence that is to the left of mention of millimoles by 10 or more characters to keep the solution sentence short
    # helps avoid unnecassary text mining errors
    mm_in_sent = conc_re.search(sentence)
    if mm_in_sent.start() >= 10:
        sentence = sentence[mm_in_sent.start() - 10:]
    
    # Split the sentence on ";" - if not enough pieces are generated, split by commas as well
    split_sent = sentence.split(";")
    if len(split_sent) <= 4:
        temp_sent = []
        for sent in split_sent:
            temp_sent.append(sent.split(","))
        split_sent = sum(temp_sent,[])
        
    # Split the sentence by "or" and "and"
    temp_sent = []
    for sent in split_sent:
        temp_sent.append(re.split("(\s+or\s+|\s+and\s+)", sent))
    split_sent = sum(temp_sent,[])
    
    for fragment in split_sent:
        pH_location = ph_re.search(fragment)
        if pH_location:
            actual_pH = find_closest_num(fragment[pH_location.start():], ph_re)
            actual_pH_num = get_num(actual_pH)
            pH_location = pH_location.start()
        else:
            pH_location = len(fragment)
        
        elem_location = elem_re.search(fragment)
        if elem_location and elem_location.start() < pH_location:
            actual_conc = find_closest_num(fragment, elem_re)
            if actual_conc:
                actual_conc_num = get_num(actual_conc)
                if len(fragment) > elem_location.end() - 1 and (fragment[elem_location.end() - 1]).isdigit(): 
                    total_conc += float(fragment[elem_location.end() - 1]) * actual_conc_num
                elif fragment[elem_location.start():elem_location.end()].startswith("di"):
                    total_conc += 2 * actual_conc_num
                else:
                    total_conc += actual_conc_num
                
    if 0 < actual_pH_num and actual_pH_num < 14:
        pH_ob = m.ContValue.objects.get_or_create(mean = actual_pH_num, stderr = 0, stdev = 0)[0]
        pH_meta_ob = m.MetaData.objects.get_or_create(name = "%s_pH" % soln_name, cont_value = pH_ob)[0]
        update_amd_obj(article, pH_meta_ob, text_ob, user)

    # if the ion is not present in the solution - leave that entry as NaN in the database
    if total_conc == 0:
        return
    
    total_conc_ob = m.ContValue.objects.get_or_create(mean = total_conc, stderr = 0, stdev = 0)[0]
    metadata_name = "%s_unassigned_compound" % soln_name
    
    if "Mg" in elem_re.pattern:
        metadata_name = "%s_Mg" % soln_name
    elif "Ca" in elem_re.pattern:
        metadata_name = "%s_Ca" % soln_name
    elif "Na" in elem_re.pattern:
        metadata_name = "%s_Na" % soln_name
    elif "Cl" in elem_re.pattern:
        metadata_name = "%s_Cl" % soln_name
    elif "K" in elem_re.pattern:
        metadata_name = "%s_K" % soln_name
        
    meta_ob = m.MetaData.objects.get_or_create(name = metadata_name, cont_value = total_conc_ob)[0]
    update_amd_obj(article, meta_ob, text_ob, user)

# Extract concentration for each ion of interest from the given solution
def record_compounds(article, soln_text, soln_text_wrap, soln_name, user = None):
    compounds = [mg_re, ca_re, na_re, cl_re, k_re]
    
    for compound in compounds:
        extract_conc(soln_text, soln_text_wrap, compound, article, soln_name, user)
        
# Finds preceeding sentences (up to 3) with respect to index i from the list of sentences
# Returns a list of wrapping sentences with the ordering: closest -> furthest on the left
def get_preceeding_text(sentences, i):
    text_wrap = []
    for j in range(i-1, i-4, -1):
        if j >= 0:
            text_wrap.append(sentences[j])
        else:
            text_wrap.append("")

    return text_wrap
    
# Mine for solution concentrations within the method section of the given article
# FlagSoln is the measure of certainty that the solutions have been extracted correctly: 0 - highest, 3 - lowest
def assign_solution_concs(article):
#     print "Textmining article: %s" % article.pk
    full_text_list = m.ArticleFullText.objects.filter(article = article.pk)
    
    if not full_text_list:
        return -1
    
    full_text = full_text_list[0].get_content()
    methods_tag = getMethodsTag(full_text, article)
    
    if methods_tag is None:
        print "No methods tag found article id: %s, pmid: %s" % (article.pk, article.pmid)
        return -2
    
    article_text = re.sub('\s+', ' ', methods_tag.text)
    
    if len(article_text) <= 100:
        print "Methods section is too small. Article id: %s, pmid: %s" % (article.pk, article.pmid)
        return -3
    
    sentences = nltk.sent_tokenize(article_text)
    list_of_solns = []
    wrap_soln_text = []
    
    # Consider a machine learning approach to get the weights, also assign higher score when compounds are in close proximity to avoid: 
    # "The calcium-free saline solution containing cobalt was composed of (in mM): 115 NaCl, 23 NaHCO3, 3.1 KCl, 1.15 CoCl2, 1.2 MgCl2, and 6 glucose."
    # "The extracellular solution to isolate calcium current utilizing Ba2+ as a charge carrier contained (mm): tetraethylammonium chloride 120, BaCl2 10, MgCl2 1, Hepes 10, and glucose 10, pH adjusted to 7.3 with Tris."
    
    for i, sentence in enumerate(sentences):
        matchScore = 0
        if conc_re.search(sentence):
            matchScore += 3
        if mgca_re.search(sentence):
            matchScore += 2
        if na_re.search(sentence):
            matchScore += 1
        if k_re.search(sentence):
            matchScore += 1
        if cl_re.search(sentence):
            matchScore += 2
            
        if matchScore >= 7:
            list_of_solns.append(sentence)
            if i < len(sentences) - 1:
                current_text_wrap = get_preceeding_text(sentences, i)
                current_text_wrap.append(sentences[i+1])
            else:
                current_text_wrap = get_preceeding_text(sentences, i)
                current_text_wrap.append("")
            wrap_soln_text.append(current_text_wrap)
    
    recording_solution_absent = True
    storage_solns = []
    unassigned_solns = []
    
    internalID = 0
    externalID = 0
    for i, soln in enumerate(list_of_solns):
        for j in range(-1, len(wrap_soln_text[i])):
            if j == -1:
                soln_id_text = soln
            else:
                soln_id_text = wrap_soln_text[i][j]
                
            if pipette_re.search(soln_id_text):
                if other_re.search(soln_id_text):
                    break
                record_compounds(article, soln, wrap_soln_text[i], "internal_%s" % internalID)
                internalID += 1
                break
                
            elif record_re.search(soln_id_text):
                if other_re.search(soln_id_text) and not recording_solution_absent:
                    break
                recording_solution_absent = False
                record_compounds(article, soln, wrap_soln_text[i], "external_%s" % externalID)
                externalID += 1
                break
                
            elif cutstore_re.search(soln_id_text):
                storage_solns.append([soln, wrap_soln_text[i]])
                break
            
            elif j == len(wrap_soln_text[i]) - 1:
                unassigned_solns.append([soln, wrap_soln_text[i]])
    
    if recording_solution_absent and storage_solns:
        recording_solution_absent = False
        soln = storage_solns.pop()
        record_compounds(article, soln[0], soln[1], "external_%s" % externalID)

#     if recording_solution_absent and unassigned_solns:
#         recording_solution_absent = False
#         for soln in unassigned_solns:
#             record_compounds(article, soln, wrap_soln_text[i], "unassigned_%s" % externalID)
#             externalID += 1
    
    def flagSolutions(soln_id, length, soln_name):
        if soln_id == 1 and length == 0:
            flag_soln = 4
        elif soln_id > 1 and length == 0:
            flag_soln = 3
        elif soln_id == 1 and length > 0:
            flag_soln = 2
        elif soln_id > 1 and length > 0:
            flag_soln = 1
        else:
            flag_soln = 0
            

        try:
            flag_ob = m.ContValue.objects.get_or_create(mean = flag_soln, stderr = 0, stdev = 0)[0]
            flag_soln_meta_ob = m.MetaData.objects.get_or_create(name = soln_name, cont_value = flag_ob)[0]
            
            flag_ob_zero = m.ContValue.objects.get_or_create(mean = 0, stderr = 0, stdev = 0)[0]
            flag_soln_meta_ob_zero = m.MetaData.objects.get(name = soln_name, cont_value = flag_ob_zero)[0]
            
            amd_ob = m.ArticleMetaDataMap.objects.get(article = article, metadata = flag_soln_meta_ob_zero)[0]
            amd_ob.metadata = flag_soln_meta_ob
            amd_ob.save()
        except ObjectDoesNotExist:
            # This solution already has a non-zero flag
            return

    
    
    return 1
    
def check_ltp_article(article):
    full_text_list = m.ArticleFullText.objects.filter(article = article.pk)
    
    if not full_text_list:
        return False
    
    full_text = full_text_list[0].get_content()
    article_text = re.sub('\s+', ' ', full_text)
    
    if len(article_text) <= 100:
        return False
    
    return ltp_re.search(article_text)
    
    
# Code to find the control LTP values, their standard errors and number of trials.
# Create text and annotation files for each LTP article for later curation in BRAT
#
# @Input: 
# TODO: last number from the left to +/- should be the LTP value, not first in the preplusminus, add multiple NumberOfTrials stacking rule to be allowed in the annotations.
def assign_ltp(article):
    full_text_list = m.ArticleFullText.objects.filter(article = article.pk)
    
    if not full_text_list:
        return False
    
    full_text = full_text_list[0].get_content()
    full_text = full_text.decode('UTF-8')
    
    articleText = re.sub('\s+', ' ', strip_tags(full_text))
    pubmed_link_str = 'http://www.ncbi.nlm.nih.gov/pubmed/%d/' % article.pmid
    
    hippocampus_mention = hippocampus_re.search(article.abstract.encode('UTF-8')) if article.abstract else hippocampus_re.search(articleText)
    
    if not hippocampus_mention:
        return False
    
    sentences = nltk.sent_tokenize(articleText) #tokenize the entire article for sentences
    
    # opening files to later save the LTP data
    ltpAnnoFilePath = BRAT_FILE_PATH + "ltp_data_%s.ann" % article.pmid
    ltpDataFilePath = BRAT_FILE_PATH + "ltp_data_%s.txt" % article.pmid
    
    ltpAnnoFile = open(ltpAnnoFilePath, "a+b")
    ltpDataFile = open(ltpDataFilePath, "a+b")

    # Various indeces to keep track of while writing data to the BRAT files
    ltpDataFileLength = 0 
    ltpEntityIndex = 1
    ltpRelationIndex = 1
    ltpAttributeIndex = 1
    last_ltp_mention_index = -6
    
    # Create header information for the BRAT files
    authors = []
    for author in article.authors.all():
        authors.append(author.last+ " " + author.initials) 
    ltp_header = "%s\n%s\n%s, %s\nPubmed link: %s\n" % (article.title, ", ".join(authors), article.journal, article.pub_year, pubmed_link_str)
    
    # find sentences that contain LTP and then find the first sentence that contains plusMinus 
    # for every sentence in article:
    for i, sentence in enumerate(sentences):
        # skip this loop iteration if we have already checked it
        if i < last_ltp_mention_index + 5:
            continue
        
        # if sentence contains LTP in it
        ltp_sent = ltp_re.search(sentence)
        writeDataSent = False
        
        if ltp_sent:
            last_ltp_mention_index = i
            
            # look at up to 5 sentences following the ltp_sent
            data_sent = "".join(sentences[i : min(i + 5, len(sentences))]) + "  "
          
            # Look for the control measurement keywords  
            LTPControlValue_locs = []
            LTPControl_locs = []

            for c_loc in control_re.finditer(data_sent):
                LTPControlValue_loc = -1000000
                for loc in plusMinus_re.finditer(data_sent):
                    if abs(loc.start() - c_loc.start()) < abs(c_loc.start() - LTPControlValue_loc):
                        LTPControlValue_loc = loc.start()
                        
                LTPControlValue_locs.append(LTPControlValue_loc)
                LTPControl_locs.append(c_loc)
            
            # Annotate LTP values    
            for plusMinus_loc in plusMinus_re.finditer(data_sent):
                # postPlusMinus stores up to 20 characters after the +/- symbol
                postPlusMinus = " " + data_sent[plusMinus_loc.end() : plusMinus_loc.end() + 50] if plusMinus_loc.end() + 50 < len(data_sent) else " " + data_sent[plusMinus_loc.end() :]
                postPlusMinus_units = postPlusMinus[:10]
                
                # num_re requires at least one whitespace before the number to function properly
                stderr_loc = num_re.search(postPlusMinus)
                n_loc = n_re.search(postPlusMinus)
                
                # prePlusMinus stores up to 20 characters before the +/- symbol
                prePlusMinus_text = data_sent[plusMinus_loc.start() - 20 : plusMinus_loc.end()] if plusMinus_loc.end() - 20 > 0 else data_sent[:plusMinus_loc.end()]
                prePlusMinus = find_closest_num(prePlusMinus_text.split('%').pop() + '%', plusMinus_re)
                        
                # check units of measurement post +\- sign
                # if matches any non-LTP unit, do not annotate it
                if prePlusMinus is not None and (units_re.search(postPlusMinus_units) is None or '%' in postPlusMinus_units):
                    # Looking for the correct occurrence of the prePlusMinus number in the data_sent. 
                    prePlusMinus_loc = None
                    for value_loc in re.finditer(prePlusMinus, data_sent):
                        if prePlusMinus_loc is None:
                            prePlusMinus_loc = data_sent.find(prePlusMinus)
                        elif abs(plusMinus_loc.start() - prePlusMinus_loc) > abs(plusMinus_loc.start() - value_loc.start()):
                            prePlusMinus_loc = value_loc.start()
                    
                    # Write the header to files
                    if ltpDataFileLength == 0:
                        ltpDataFile.write((ltp_header).encode('UTF-8'))   
                        ltpDataFileLength += len(ltp_header)
                        
                        ltpAnnoFile.write(("\t".join(["T%s" % ltpEntityIndex, "ArticleTitle 0 %s" % len(article.title), article.title]) + "\n").encode('UTF-8'))
                        ltpAnnoFile.write(("\t".join(["A%s" % ltpAttributeIndex, "Curation T%s Not_Curated" % ltpEntityIndex]) + "\n").encode('UTF-8'))
                        ltpAttributeIndex += 1
                        ltpAnnoFile.write(("\t".join(["A%s" % ltpAttributeIndex, "LTPArticle T%s LTP" % ltpEntityIndex]) + "\n").encode('UTF-8'))
                        ltpEntityIndex += 1
                        ltpAttributeIndex += 1
                    
                    if plusMinus_loc.start() in LTPControlValue_locs:
                        ltpTag = "LTPControlValue "
                        control_loc = LTPControl_locs[LTPControlValue_locs.index(plusMinus_loc.start())]
                        
                        # check whether this control mention is WT, adjust the indexes if so
                        wt_control = re.search("wt", data_sent[control_loc.start():control_loc.end()], flags=re.UNICODE|re.IGNORECASE)
                        control_start = control_loc.start() + 1 if wt_control else control_loc.start()
                            
                        ltpAnnoFile.write(("\t".join(["T%s" % ltpEntityIndex, "LTPControl %s %s" % (ltpDataFileLength + control_start, ltpDataFileLength + control_loc.end()), 
                                                      data_sent[control_start:control_loc.end()]]) + "\n").encode('UTF-8'))
                        ltpEntityIndex += 1
                    else:
                        ltpTag = "LTPValue "
                    
                    # if prePlusMinus contains a range - report the mean, otherwise just convert it to a number    
                    LTPVal = get_num(prePlusMinus)
                    if LTPVal < 0:
                        LTPValueType = "Additive"
                    elif LTPVal >= 0:
                        if LTPVal < 5:
                            LTPValueType = "Fold-change"
                        elif LTPVal < 80:
                            LTPValueType = "Additive"
                        else:
                            LTPValueType = "Relative"
                    else:
                        LTPValueType = "Unknown"
                    
                    ltpAnnoFile.write(("\t".join(["T%s" % ltpEntityIndex, ltpTag + str(ltpDataFileLength + prePlusMinus_loc) + " " + str(ltpDataFileLength + prePlusMinus_loc + len(prePlusMinus)), 
                              prePlusMinus]) + "\n").encode('UTF-8'))
                    ltpAnnoFile.write(("\t".join(["A%s" % ltpAttributeIndex, "Confidence T%s Certain" % ltpEntityIndex]) + "\n").encode('UTF-8'))
                    ltpAttributeIndex += 1
                    ltpAnnoFile.write(("\t".join(["A%s" % ltpAttributeIndex, "LTPValueType T%s %s" % (ltpEntityIndex, LTPValueType)]) + "\n").encode('UTF-8'))
                    ltpAttributeIndex += 1
                    ltpAnnoFile.write(("\t".join(["A%s" % ltpAttributeIndex, "Curation T%s Not_Curated" % ltpEntityIndex]) + "\n").encode('UTF-8'))
                    ltpAttributeIndex += 1
                    ltpEntityIndex += 1
                    
                    if stderr_loc:
                        ltpAnnoFile.write(("\t".join(["T%s" % ltpEntityIndex, "StandardError " + str(ltpDataFileLength + plusMinus_loc.end() + stderr_loc.start()) + " " + str(ltpDataFileLength + plusMinus_loc.end() + stderr_loc.end() - 1), 
                                  postPlusMinus[stderr_loc.start() + 1:stderr_loc.end()]]) + "\n").encode('UTF-8'))
                        ltpAnnoFile.write(("\t".join(["R%s" % ltpRelationIndex, "HasError Arg1:T%s Arg2:T%s" % (ltpEntityIndex - 1, ltpEntityIndex)]) + "\n").encode('UTF-8'))
                        ltpEntityIndex += 1
                        ltpRelationIndex += 1
                    
                    if n_loc:
                        # write annotation NumberOfTrials entity
                        ltpAnnoFile.write(("\t".join(["T%s" % ltpEntityIndex, "NumberOfTrials " + str(ltpDataFileLength + plusMinus_loc.end() + n_loc.start() - 1) + " " + str(ltpDataFileLength + plusMinus_loc.end() + n_loc.end() - 1), 
                              postPlusMinus[n_loc.start():n_loc.end()]]) + "\n").encode('UTF-8'))
                        # write annotation NumberOfTrials relation to LTP
                        ltpAnnoFile.write(("\t".join(["R%s" % ltpRelationIndex, "NumTrials Arg1:T%s Arg2:T%s" % (ltpEntityIndex - 2, ltpEntityIndex)]) + "\n").encode('UTF-8'))
                        ltpEntityIndex += 1
                        ltpRelationIndex += 1
                        
                    writeDataSent = True
            
            # If ltp values have been found within the fragment - write the data_sent and LTP mentions to files
            if writeDataSent: 
                print "Writing data to file for pmid: %s" % article.pmid
                for ltp_mention_loc in ltp_re.finditer(data_sent):
                        ltpAnnoFile.write(("\t".join(["T%s" % ltpEntityIndex, "LTPMention " + str(ltpDataFileLength + ltp_mention_loc.start()) + " " + str(ltpDataFileLength + ltp_mention_loc.end()), 
                                                      data_sent[ltp_mention_loc.start():ltp_mention_loc.end()]]) + "\n").encode('UTF-8'))
                        ltpEntityIndex += 1
                
                ltpDataFile.write((data_sent).encode('UTF-8'))       
                ltpDataFileLength += len(data_sent)
                
    ltpDataFile.close()
    ltpAnnoFile.close()
    
    if os.path.getsize(ltpAnnoFilePath) == 0:
        os.remove(ltpAnnoFilePath)
        os.remove(ltpDataFilePath)
