# -*- coding: utf-8 -*-
"""
Created on Tue Mar 12 17:55:18 2013

@author: Shreejoy
"""
from bs4 import BeautifulSoup
import re
import nltk
import neuroelectro.models as m

def get_electrode_type(article_list):
    patch_mesh = m.MeshTerm.objects.get(term = 'Patch-Clamp Techniques')
    electrode_list_text_mine = []
    electrode_list = []
    for idx, art in enumerate(article_list):
        ft = art.articlefulltext_set.all()[0].full_text
        methods_tag = getSectionTag(ft, 'METHODS')
        text = re.sub('\s+', ' ', methods_tag.text)
    #    soup = BeautifulSoup(''.join(ft))
    #    text = soup.get_text()
        sents = nltk.sent_tokenize(text)
        electrode_set = set()
    #    electrode_list = []
        for s in sents:
            if whole_re.findall(s):
                wholeCellSet.add(art)
    #            print 'whole: ' + art.title
    #            print str(idx) + ' : ' + s.encode("iso-8859-15", "replace")
                electrode_set.add('Whole-cell')
    #            electrode_list.append('Whole-cell')
    #            electrode_list_text_mine.append('Whole-cell')
            if sharp_re.findall(s):
                sharpSet.add(art)
    #            print 'sharp: ' + art.title
    #            print str(idx) + ' : ' + s.encode("iso-8859-15", "replace")
                electrode_set.add('sharp')
    #            electrode_list.append('sharp')
        if 'Whole-cell' in electrode_set and 'sharp' in electrode_set:
            electrode_list.append('both')
        elif 'Whole-cell' in electrode_set:
            electrode_list.append('Whole-cell')
        elif 'sharp' in electrode_set:
            electrode_list.append('sharp')
        else:
            # textmining dind't work, check mesh terms for patch-clamp
            mesh_terms = art.terms.all()
            if patch_mesh in mesh_terms:
                electrode_list.append('Whole-cell')
            else:
                electrode_list.append('not specified')
        methods_tag = ''
    return electrode_list
    
def get_species(article_list):
    rat_mesh = m.MeshTerm.objects.get(term = 'Rats')
    mouse_mesh = m.MeshTerm.objects.get(term = 'Mice')
    guinea_mesh = m.MeshTerm.objects.get(term = 'Guinea Pigs') 
    bird_mesh = m.MeshTerm.objects.get(term = 'Songbirds') 
    turtle_mesh = m.MeshTerm.objects.get(term = 'Turtles') 
    cat_mesh = m.MeshTerm.objects.get(term = 'Cats') 
    zebrafish_mesh = m.MeshTerm.objects.get(term = 'Zebrafish')
    monkey_mesh = m.MeshTerm.objects.get(term = 'Macaca mulatta')
    goldfish_mesh = m.MeshTerm.objects.get(term = 'Goldfish')
    aplysia_mesh = m.MeshTerm.objects.get(term = 'Aplysia')
    xenopus_mesh = m.MeshTerm.objects.get(term = 'Xenopus')
    gerbil_mesh = m.MeshTerm.objects.get(term = 'Gerbillinae')
    
    species_list_all = []
    for a in article_list:
        mesh_terms = a.terms.all()
        species_list = []
        if rat_mesh in mesh_terms:
            print a.pmid, 'rat'
            species_list.append('rat')
        if mouse_mesh in mesh_terms:
            print a.pmid, 'mouse'
            species_list.append('mouse')
        if bird_mesh in mesh_terms:
            print a.pmid, 'bird'
            species_list.append('bird')
        if guinea_mesh in mesh_terms:
            print a.pmid, 'guinea pig'
            species_list.append('guinea pig')
        if turtle_mesh in mesh_terms:
            print a.pmid, 'turtle'
            species_list.append('turtle')
        if cat_mesh in mesh_terms:
            print a.pmid, 'cat'
            species_list.append('cat')
        if zebrafish_mesh in mesh_terms:
            print a.pmid, 'zebrafish'
            species_list.append('zebrafish')
        if monkey_mesh in mesh_terms:
            print a.pmid, 'monkey'
            species_list.append('monkey')
        if goldfish_mesh in mesh_terms:
    #        print a.pmid, 'monkey'
            species_list.append('goldfish')
        if aplysia_mesh in mesh_terms:
    #        print a.pmid, 'monkey'
            species_list.append('aplysia')
        if xenopus_mesh in mesh_terms:
    #        print a.pmid, 'monkey'
            species_list.append('xenopus')
        if gerbil_mesh in mesh_terms:
    #        print a.pmid, 'monkey'
            species_list.append('gerbil')
            
        if len(species_list) == 0:
            species_list.append('not specified')
        species_list_all.append(species_list)
    return species_list_all