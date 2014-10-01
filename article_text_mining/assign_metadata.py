# -*- coding: utf-8 -*-
"""
Created on Wed Apr 10 13:41:52 2013

@author: Shreejoy
"""

import neuroelectro.models as m
from html_process_tools import getMethodsTag
import re
import nltk
from html_table_decode import resolveDataFloat
import numpy as np
import string

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

jxn_re = re.compile(ur'junction\s\potential' , flags=re.UNICODE|re.IGNORECASE)
jxn_not_re = re.compile(ur'\snot\s.+junction\spotential|junction\spotential.+\snot\s|\sno\s.+junction\spotential|junction\spotential.+\sno\s' , flags=re.UNICODE|re.IGNORECASE)

conc_re = re.compile(ur'in\sMM|\sMM\s|\(MM\)', flags=re.UNICODE|re.IGNORECASE)
mgca_re = re.compile(ur'\s([Mm]agnesium|[Cc]alcium)|-(Mg|Ca)|(Ca|Mg)([A-Z]|\d|-|\s)', flags=re.UNICODE)
na_re = re.compile(ur'\s(di)?[Ss]odium|-Na|Na([A-Z]|\d|-|\s|\+|gluc)', flags=re.UNICODE)
mg_re = re.compile(ur'\s[Mm]agnesium|-Mg|Mg([A-Z]|\d|-|\s)', flags=re.UNICODE)
ca_re = re.compile(ur'\s[Cc]alcium|-Ca|Ca([A-Z]|\d|-|\s)', flags=re.UNICODE)
k_re = re.compile(ur'\s(di)?[Pp]otassium|-K|K([A-Z]|\d|-|\s|\+|gluc)', flags=re.UNICODE)
cl_re = re.compile(ur'Cl|[Cc]hlorine|[Cc]loride', flags=re.UNICODE)
record_re = re.compile(ur'external|perfus|extracellular|superfuse|record.+ACSF|ACSF.+record|chamber.+(ACSF|record)|(ACSF|record).+chamber', flags=re.UNICODE|re.IGNORECASE)
pipette_re = re.compile(ur'internal|intracellular|pipette|electrode', flags=re.UNICODE|re.IGNORECASE)
cutstore_re = re.compile(ur'incubat|stor|slic|cut|dissect|remove|ACSF|\sbath\s', flags=re.UNICODE|re.IGNORECASE)
num_re = re.compile(ur'(\\|/|\s|\()(\d*\.\d+|\d+|(\d*\.\d+|\d+)\s*-\s*(\d*\.\d+|\d+))', flags=re.UNICODE|re.IGNORECASE)
ph_re = re.compile(ur'[\s\(,;]pH', flags=re.UNICODE)
other_re = re.compile(ur'[Ss]ubstitut|[Jj]unction\spotential|PCR|\sgel\s|Gel\s|\sreplace|\sincrease|\sreduc|\sstimul|\somit', flags=re.UNICODE)

def update_amd_obj(article, metadata_ob):
    amd_ob = m.ArticleMetaDataMap.objects.get_or_create(article=article, metadata = metadata_ob)[0]
    amd_ob.added_by = robot_user
    amd_ob.save()

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
                retDict = resolveDataFloat(degree_close_str)
                if 'value' in retDict:
                    temp_dict_list.append(retDict)
            elif room_temp_re.findall(s):
    #            print article.pk
    #            print s.encode("iso-8859-15", "replace")
                retDict = {'value':22.0, 'maxRange' : 24.0, 'minRange': 20.0}
                temp_dict_list.append(retDict)
        if len(temp_dict_list) > 0:
    #        print temp_dict_list
            temp_dict_fin = validate_temp_list(temp_dict_list)
    #        print temp_dict_fin
            if temp_dict_fin:
                min_range = None
                max_range = None
                stderr = None
                if 'minRange' in temp_dict_fin:
                    min_range = temp_dict_fin['minRange']
                if 'maxRange' in temp_dict_fin:
                    max_range = temp_dict_fin['maxRange']
                if 'error' in temp_dict_fin:
                    stderr = temp_dict_fin['error']
                cont_value_ob = m.ContValue.objects.get_or_create(mean = temp_dict_fin['value'], min_range = min_range,
                                                                  max_range = max_range, stderr = stderr)[0]
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
                    retDict = resolveDataFloat(p_close_str)
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
                    retDict = resolveDataFloat(p_close_str)
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
                if 'minRange' in age_dict_fin:
                    min_range = age_dict_fin['minRange']
                if 'maxRange' in age_dict_fin:
                    max_range = age_dict_fin['maxRange']
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

# find a number closest to the location in the given fragment that has a space, a slash or a backslash before it
def find_closest_num(fragment, location):
    frag_nums = [m.span() for m in re.finditer(num_re, fragment)]
    if frag_nums:
        closest_num = -1
        closest_num_start = -10000
        for frag_num in frag_nums:
            if abs(location.start() - frag_num[0]) < abs(location.start() - closest_num_start):
                closest_num_start = frag_num[0]
                closest_num = fragment[frag_num[0] + 1 : frag_num[1]]
        return closest_num
    return None

# Find any occurrences of the element within the sentence and extract the number closest to each match
def extract_conc(sentence, elem_re, article, soln_name):
    # TODO: mine for full compounds, not just specific ions (maybe)
    total_conc = 0
    
    split_sent = sentence.split(";")
    if len(split_sent) <= 4:
        temp_sent = []
        for sent in split_sent:
            temp_sent.append(sent.split(","))
        split_sent = sum(temp_sent,[])
        
    f.write(("Attempting to mine %s for total_conc: %s\n" %(elem_re.pattern, sentence)).encode('utf8'))
    
    for fragment in split_sent:
        pH_location = ph_re.search(fragment)
        if pH_location:
            actual_pH = find_closest_num(fragment, pH_location)
            if actual_pH:
                f.write(("Mined pH is: %s\n" % actual_pH).encode('utf8'))
            else:
                f.write(("Failed to mine pH within fragment: %s\n" % fragment).encode('utf8'))
            pH_location = pH_location.start()
        else:
            pH_location = len(fragment)
        
        elem_location = elem_re.search(fragment)
        if elem_location and elem_location.start() < pH_location:
            actual_conc = find_closest_num(fragment, elem_location)
            if actual_conc:
                f.write(("Mined concentration for %s is %s\n" % (fragment, actual_conc)).encode('utf8'))
                f.write(("checking for molarity: %s\n" % fragment[elem_location.end() - 1]).encode('utf8'))
                if "-" in actual_conc:
                    conc_range = actual_conc.split("-")
                    actual_conc = (float(conc_range[0]) + float(conc_range[1])) / 2
                if len(fragment) > elem_location.end() - 1 and (fragment[elem_location.end() - 1]).isdigit():
                    total_conc += float(fragment[elem_location.end() - 1]) * float(actual_conc)
                else:
                    total_conc += float(actual_conc)
                
            else:
                f.write(("No number was found within fragment: %s\n" % fragment).encode('utf8'))
    f.write(("Total conc: %s\n" % total_conc).encode('utf8'))
    
    total_conc_ob = m.ContValue.objects.get_or_create(mean = total_conc, stderr = 0, stdev = 0)[0]
    if "Mg" in elem_re.pattern:
        meta_ob = m.MetaData.objects.get_or_create(name = "%s_Mg" % soln_name, cont_value = total_conc_ob)[0]
    elif "Ca" in elem_re.pattern:
        meta_ob = m.MetaData.objects.get_or_create(name = "%s_Ca" % soln_name, cont_value = total_conc_ob)[0]
    elif "Na" in elem_re.pattern:
        meta_ob = m.MetaData.objects.get_or_create(name = "%s_Na" % soln_name, cont_value = total_conc_ob)[0]
    update_amd_obj(article, meta_ob)
    
    return total_conc

# Extract concentration for each ion of interest from the given solution
def record_compounds(article, soln_text, soln_name):
    # TODO: account for dissociation constants for compounds
    extract_conc(soln_text, mg_re, article, soln_name)
    extract_conc(soln_text, ca_re, article, soln_name)
    extract_conc(soln_text, na_re, article, soln_name)
    
# Mine for solution concentrations within the method section of the given article
def assign_solution_concs(article):
    global f
    f = open('/Users/dtebaykin/Desktop/output1.txt', 'a')
    f.write(("starting textmining article id: %s for soln concs\n" % article.id).encode('utf8'))
    if not article.articlefulltext_set.all():
        f.write(("No full text is associated with the article id: %s, pmid: %s\n" % (article.pk, article.pmid)).encode('utf8') )
        return False
    full_text = article.articlefulltext_set.all()[0].get_content()
    methods_tag = getMethodsTag(full_text, article)
    
    if methods_tag is None:
        f.write(("No methods tag found in the article pmid: %s, title: %s, journal: %s\n" % (article.pmid, article.title, article.journal)).encode('utf8') )
        return False
    
    article_text = re.sub('\s+', ' ', methods_tag.text)
    sentences = nltk.sent_tokenize(article_text)
    list_of_solns = []
    
    
    for sentence in sentences:
        #metadata_ob = m.MetaData.objects.get_or_create(name='', value=sentence)[0]
        #update_amd_obj(article, metadata_ob)
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
    
    recording_solution_absent = True
    storage_solns = []
    unassigned_solns = []
    
    # TODO: if unable to determine which solution type the sentence contains - check previous and then the following sentences for keywords.
    internalID = 0
    externalID = 0
    for soln in list_of_solns:
        if pipette_re.search(soln):
            if other_re.search(soln):
                f.write(("Other solution found: length %s, article id %s, pmid %s: %s\n" % (len(soln), article.pk, article.pmid, soln)).encode('utf8') )
                continue
            f.write(("Internal/pipette soln found length %s, article id %s, pmid %s: %s\n" % (len(soln), article.pk, article.pmid, soln)).encode('utf8') )
            record_compounds(article, soln, "internal_%s" % internalID)
            internalID += 1
        elif record_re.search(soln):
            if other_re.search(soln) and not recording_solution_absent:
                f.write(("Other solution found: length %s, article id %s, pmid %s: %s\n" % (len(soln), article.pk, article.pmid, soln)).encode('utf8') )
                continue
            f.write(("External/recording soln found length %s, article id %s, pmid %s: %s\n" % (len(soln), article.pk, article.pmid, soln)).encode('utf8') )
            recording_solution_absent = False
            record_compounds(article, soln, "external_%s" % externalID)
            externalID += 1
        elif cutstore_re.search(soln):
            storage_solns.append(soln)
            f.write(("Cutting/Storage/Incubation soln found length %s, article id %s, pmid %s: %s\n" % (len(soln), article.pk, article.pmid, soln)).encode('utf8') )
        else:
            unassigned_solns.append(soln)
            f.write(("Unassigned soln found length %s, article id %s, pmid %s: %s\n" % (len(soln), article.pk, article.pmid, soln)).encode('utf8') )
    
    if recording_solution_absent and storage_solns:
        recording_solution_absent = False
        soln = storage_solns.pop()
        f.write(("External/recording soln not found, using last storage solution: length %s, article id %s, pmid %s: %s\n" % (len(soln), article.pk, article.pmid, soln)).encode('utf8') )
        record_compounds(article, soln, "external_%s" % externalID)
        externalID += 1

    if recording_solution_absent and unassigned_solns:
        recording_solution_absent = False
        for soln in unassigned_solns:
            f.write(("Definitive external/recording soln not found, possible solution: length %s, article id %s, pmid %s: %s\n" % (len(soln), article.pk, article.pmid, soln)).encode('utf8') )
#             record_compounds(soln)
        
    if list_of_solns.__len__() == 0:
        f.write(("Nothing was found. Article id: %s, pmid: %s\n" % (article.pk, article.pmid)).encode('utf8'))
    
    f.write(("\n\n").encode('utf8'))    
    f.close()
    