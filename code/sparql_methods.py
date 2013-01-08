# -*- coding: utf-8 -*-
"""
Created on Thu Dec 08 13:21:49 2011

@author: Shreejoy
"""

from SPARQLWrapper import SPARQLWrapper, JSON, XML

def sparql_get(getTerm, usingTermString, usingTermMethod):
    sparql = SPARQLWrapper("http://api.talis.com/stores/neurolex/services/sparql")
    sparql.setReturnFormat(JSON)
    outStr = getTerm.lower()
    inStr = usingTermMethod.lower()
    queryStr = ("""
    prefix xsd: <http://www.w3.org/2001/XMLSchema#>
    prefix property: <http://neurolex.org/wiki/Special:URIResolver/Property-3A>
    select distinct ?%s
    where {
        ?x property:%s ?%s.
        ?x property:%s ?%s.
        filter regex(?%s, "%s", "i").
        }
    """ % (outStr, usingTermMethod, inStr, getTerm, outStr, inStr, usingTermString))        
#    
#    """ % (outStr, usingTermMethod, usingTermString, getTerm, outStr))
#    #       id,         Label           ChannelName     Id      id
#    
#    print queryStr    
    sparql.setQuery(queryStr)
    results = sparql.query().convert()
    queryResults = []
    for result in results["results"]["bindings"]:
        queryResults.append(unicode(result[outStr]["value"]))
    
#    if len(queryResults) is 1:
#        queryResults = queryResults[0]
#    print list(queryResults)
    return queryResults
    
## get all categories with role Ion Channel
#sparql = SPARQLWrapper("http://api.talis.com/stores/neurolex-dev1/services/sparql")
#sparql.setQuery("""
#prefix xsd: <http://www.w3.org/2001/XMLSchema#>
#prefix property: <http://neurolex.org/wiki/Special:URIResolver/Property-3A>
#select distinct ?id
#where {
#    ?x property:Label ?label.
#    ?x property:Id ?id.
#    filter regex(?label, "KCa1.1", "i").
#}
#""")
    
#    queryStr = ("""
#    prefix xsd: <http://www.w3.org/2001/XMLSchema#>
#    prefix property: <http://neurolex.org/wiki/Special:URIResolver/Property-3A>
#    select distinct ?%s
#    where {
#        ?x property:%s "%s" ^^xsd:string .   
#        ?x property:%s ?%s.
#    }
#    
#    """ % (outStr, usingTermMethod, usingTermString, getTerm, outStr))
    
    
    
#    
#    queryTerm = 'Id'
#usingTermMethod = 'Label'
#for channelName in channelNameList:
#    ## get all synonyms of nlex
#    nlex =  sparql_get(queryTerm, channelName, usingTermMethod)
#    
#    
#    # get all categories with role Ion Channel
#sparql = SPARQLWrapper("http://api.talis.com/stores/neurolex-dev1/services/sparql")
#sparql.setQuery("""
#prefix xsd: <http://www.w3.org/2001/XMLSchema#>
#prefix property: <http://neurolex.org/wiki/Special:URIResolver/Property-3A>
#prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>
#prefix nm: <http://ontology.neuinfo.org/NIF/BiomaterialEntities/NIF-Molecule.owl#>
#
#select distinct ?label ?id
#where {
#    ?x property:Label ?label
#    filter regex(?label, "channel")
#}
#""")
#
## get all synonyms of kv1.1
#sparql = SPARQLWrapper("http://api.talis.com/stores/neurolex-dev1/services/sparql")
#sparql.setQuery("""
#prefix xsd: <http://www.w3.org/2001/XMLSchema#>
#prefix property: <http://neurolex.org/wiki/Special:URIResolver/Property-3A>
#
#select distinct ?label ?syn
#where {
#    ?x property:Id "nifext_2674"^^xsd:string .   
#    ?x property:Label ?label.
#    ?x property:Synonym ?syn.
#}
#
#""")
#
#    queryStr = ("""
#    prefix xsd: <http://www.w3.org/2001/XMLSchema#>
#    prefix property: <http://neurolex.org/wiki/Special:URIResolver/Property-3A>
#    select distinct ?%s
#    where {  
#        ?x property:%s ?%s.
#        filter regex(?%s, "^%s", "i")
#    }
#    
#    """ % (outStr, getTerm, outStr, outStr, usingTermString) )