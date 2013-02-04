# -*- coding: utf-8 -*-
"""
Created on Tue Jan 29 17:29:56 2013

@author: Shreejoy
"""

from sparql_methods import sparql_get
neurons = m.Neuron.objects.all()
queryTerm = 'Label'
usingTermMethod = 'Id'

neurons_with_new_names = []
neurons_with_no_nlex = []
neurons_no_names = []
for n in neurons:
    if n.nlex_id:
        if n.nlex_id != u'0':
            #print n.nlex_id
            newName = sparql_get(queryTerm, n.nlex_id, usingTermMethod)
            if len(newName) > 1:
                matching = [s for s in newName if "cell" in s]
                if len(matching) == 0:
                    matching = [s for s in newName if "neuron" in s]
                newName = matching
                if len(newName) > 1:
                    print (n.nlex_id), newName
            if len(newName) == 0:
                neurons_no_names.append((n.nlex_id, n.name))
                continue
            #print n.name, newName[0]
            if n.name != newName[0]:
                neurons_with_new_names.append((n.nlex_id, newName[0], n.name))
        else:
            neurons_with_no_nlex.append(n.name)        
    else:
        neurons_with_no_nlex.append(n.name)
        
a = []
for t in neurons_with_new_names:
    a.append([t[0], t[1]])
    
a = [n[2] for n in neurons_with_new_names]

a = []
queryTerm = 'Id'
usingTermMethod = 'Label'
for n in neurons_with_no_nlex:
    newId = sparql_get(queryTerm, n, usingTermMethod)
    print n, newId 
    
            
