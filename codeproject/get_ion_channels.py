# -*- coding: utf-8 -*-
"""
Created on Sun Nov 27 14:03:34 2011

@author: Shreejoy
"""


#!/usr/bin/python
# -*- coding: utf-8 -*-

from SPARQLWrapper import SPARQLWrapper, JSON, XML, N3, RDF
import re
import os
os.chdir('C:/Python27/Scripts/biophys/pubdb/pubdir')
from pubapp.models import Neuron, IonChannel
from sparql_methods import sparql_get

# get all nlex entries with label containing "channel"
sparql = SPARQLWrapper("http://api.talis.com/stores/neurolex-dev1/services/sparql")
sparql.setQuery("""
prefix xsd: <http://www.w3.org/2001/XMLSchema#>
prefix property: <http://neurolex.org/wiki/Special:URIResolver/Property-3A>
prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>
prefix nm: <http://ontology.neuinfo.org/NIF/BiomaterialEntities/NIF-Molecule.owl#>

select distinct ?label ?id
where {
    ?x property:Label ?label
    filter regex(?label, "receptor")
}
""")



sparql.setReturnFormat(JSON)
results = sparql.query().convert()

queryTerm = 'Id'
usingTermMethod = 'Label'
nlex = sparql_get(queryTerm, 'channel', usingTermMethod)

channelCats = [];
for result in results["results"]["bindings"]:
    category = result["label"]["value"]
    if re.search('protocol', category):
        continue
    elif re.search('resource', category, re.IGNORECASE):
        continue
    elif re.search('meric', category, re.IGNORECASE):
        continue    
    channelCats.append(category)
    #print category

channelSet = set(channelCats)
# remove supercategories
for i in range(1,len(channelCats)):
    for j in range(i+1,len(channelCats)):
        if re.search(channelCats[i], channelCats[j]) is not None:
            channelSet.discard(channelCats[i])                        
            continue

finalChannelSet = []
for category in channelSet:
    # get all sub-categories of everything in channelSet
    sparql = SPARQLWrapper("http://api.talis.com/stores/neurolex-dev1/services/sparql")
    sparql.setQuery("""
    prefix xsd: <http://www.w3.org/2001/XMLSchema#>
    prefix property: <http://neurolex.org/wiki/Special:URIResolver/Property-3A>
    prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    
    select distinct ?label ?id
    where {
        ?x property:Label "%s"^^xsd:string .
        ?y rdfs:subClassOf ?x.      
        ?y property:Label ?label.
        ?y property:Id ?id.
    }
    """ % category)
    
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    for result in results["results"]["bindings"]:
        category = result["label"]["value"]
        finalChannelSet.append(category)
#        if re.search(r'[\_\-]+', category) is None:
#            nlexID = result["id"]["value"]
#            c = IonChannel.objects.get_or_create(nlexID = nlexID, name = category)[0]
#            c.save()

