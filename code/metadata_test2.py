# -*- coding: utf-8 -*-
"""
Created on Fri Mar 08 19:04:27 2013

@author: Shreejoy
"""
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
Strigiformes
Crustacea
Gerbillinae
Sciuridae


patch_mesh = m.MeshTerm.objects.get(term = 'Patch-Clamp Techniques')

article_list = m.Article.objects.filter(datatable__datasource__neuronconceptmap__neuronephysdatamap__val_norm__isnull = False).distinct()
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
    if len(species_list) == 0:
        species_list.append('not specified')
    species_list_all.append(species_list)
    
patch_mesh_set = set()
electrode_list_mesh = []
for i,a in enumerate(article_list):
    mesh_terms = a.terms.all()
    if patch_mesh in mesh_terms:
        patch_mesh_set.add(a.pmid)
        electrode_list_mesh.append('Whole-cell')
        print a.pmid, a.pub_year, 'Whole-cell'
    else:
        electrode_list_mesh.append('sharp')
        
        
whole_re = re.compile(ur'whole\scell|whole-cell|patch\sclamp|patch-clamp' , flags=re.UNICODE|re.IGNORECASE)
sharp_re = re.compile(ur'sharp.+electro' , flags=re.UNICODE|re.IGNORECASE)

electrode_list_text_mine = []
for idx, art in enumerate(article_list):
    ft = art.articlefulltext_set.all()[0].full_text
    methods_tag = getSectionTag(ft, 'METHODS')
    text = re.sub('\s+', ' ', methods_tag.text)
#    soup = BeautifulSoup(''.join(ft))
#    text = soup.get_text()
    sents = nltk.sent_tokenize(text)
    electrode_set = set()
    electrode_list = []
    for s in sents:
        if whole_re.findall(s):
            wholeCellSet.add(art)
            print 'whole: ' + art.title
            print str(idx) + ' : ' + s.encode("iso-8859-15", "replace")
            electrode_set.add('Whole-cell')
            electrode_list.append('Whole-cell')
#            electrode_list_text_mine.append('Whole-cell')
        if sharp_re.findall(s):
            sharpSet.add(art)
            print 'sharp: ' + art.title
            print str(idx) + ' : ' + s.encode("iso-8859-15", "replace")
            electrode_set.add('sharp')
            electrode_list.append('sharp')
#            electrode_list_text_mine.append('sharp')
    electrode_list_text_mine.append(list(electrode_list))

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
