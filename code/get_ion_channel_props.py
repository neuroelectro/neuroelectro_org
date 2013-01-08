# -*- coding: utf-8 -*-
"""
Created on Mon Nov 28 21:59:25 2011

@author: Shreejoy
"""

# -*- coding: utf-8 -*-
"""
Created on Mon Nov 28 14:26:44 2011

@author: Shreejoy
"""

from SPARQLWrapper import SPARQLWrapper, JSON, XML, N3, RDF
import re
dir('C:\Python27\Scripts\biophys\pubdb\pubdir')
from pubapp.models import IonChannel, Synonym

channels = IonChannel.objects.all()
for channel in channels:
    nlex = channel.nlexID
    ## get all synonyms of nlex
    sparql = SPARQLWrapper("http://api.talis.com/stores/neurolex-dev1/services/sparql")
    sparql.setQuery("""
    prefix xsd: <http://www.w3.org/2001/XMLSchema#>
    prefix property: <http://neurolex.org/wiki/Special:URIResolver/Property-3A>
    
    select distinct ?syn
    where {
        ?x property:Id "%s" ^^xsd:string .   
        ?x property:Synonym ?syn.    
    }
    
    """ % nlex)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    
    for result in results["results"]["bindings"]:
        synonym = result["syn"]["value"]
        # if synonym list contains semi colons or underscores - seperate
        if re.search(r'[\;\_]', synonym) is not None:
            #first replace underscores with white spaces
            synonym = re.sub(r'\_', r' ', synonym)
            
            splitList = synonym.split(';')
            for term in splitList:
               s = Synonym.objects.get_or_create(term = term)[0] 
            continue
        s = Synonym.objects.get_or_create(term = synonym)[0]
        channel.synonyms.add(s)
    channel.save()   
