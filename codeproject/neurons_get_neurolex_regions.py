# -*- coding: utf-8 -*-
"""
Created on Mon Jan 23 13:56:16 2012

@author: Shreejoy
"""

# get neuron brain regions from neurolex

from SPARQLWrapper import SPARQLWrapper, JSON, XML, N3, RDF
import re
import os
import django_startup
os.chdir('C:\Python27\Scripts\Biophys\pubdb\pubdir')
from pubapp.models import Neuron, Article, IonChannel, NeuronSyn
from pubapp.models import ArticleNeuronTag, IonChannelSyn, ArticleIonChannelTag
os.chdir('C:\Python27\Scripts\Biophys')

from pubapp.models import Neuron, NeuronSyn
from sparql_methods import sparql_get
from urllib import quote_plus

queryTerm = 'Located#x20in'
usingTermMethod = 'Label'
neurons = Neuron.objects.all()
sparql = SPARQLWrapper("http://api.talis.com/stores/neurolex/services/sparql")
sparql.setReturnFormat(JSON)    
neuronRegion1 = []
for i in range(len(neurons)):
    
    neuronName = neurons[i].name
    
    queryStr = ("""
    prefix xsd: <http://www.w3.org/2001/XMLSchema#>
    prefix property: <http://neurolex.org/wiki/Special:URIResolver/Property-3A>
    select distinct ?lo
    where {
        ?x property:Label ?label.
        ?x property:Located_in ?lo.
        filter regex(?label, "%s", "i").
        }
    """ % (neuronName))
#    print queryStr
    
    sparql.setQuery(queryStr)
    results = sparql.query().convert()
    queryResults = []
    for result in results["results"]["bindings"]:
        outStr = unicode(result['lo']["value"])
        loc =  re.sub(r'http://neurolex.org/wiki/Special:URIResolver/Category-3A', '', outStr)
        print neuronName + ' : ' + loc        
        neuronRegion1.append(loc)
    if len(result) is 0:
        neuronRegion1.append('')

neuronNameList = load_neuron_names()
queryTerm = 'Id'
usingTermMethod = 'Label'
for neuronName in neuronNameList:
    ## get all nlex id of neuron name
    nlex =  sparql_get(queryTerm, neuronName, usingTermMethod)
    if nlex:
        print neuronName, nlex[0]
        n = Neuron.objects.get_or_create(nlexID = nlex[0], name = neuronName)[0]
        n.save()
    else:
        print neuronName + " not found in nlex"
        n = Neuron.objects.get_or_create(nlexID = 0, name = neuronName)[0]
        n.save()