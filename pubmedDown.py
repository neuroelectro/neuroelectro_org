#!/usr/bin/python 
#takes in a list of pubmed IDs, outputs a list of full text htmls or '' 
#if no full text is available
def pubmedDown(pmids):
    import urllib2
    import xml.etree.ElementTree as et
    
    if type(pmids) != type([]):
        pmids = [pmids]
        
    mainLink1 = 'http://eutils.ncbi.nlm.nih.gov/entrez/eutils/elink.fcgi?dbfrom=pubmed&id='
    mainLink2 = '&cmd=prlinks'
    pmidSt = str(pmids)[1:len(str(pmids))-1].replace(' ','').replace("'","")
    req = urllib2.Request(mainLink1+pmidSt+mainLink2)
    response = urllib2.urlopen(req)
    page = response.read()
    xml = et.fromstring(page)
    
    links = [None]*len(pmids)
    i = 0
    for urlSets in xml.iter('IdUrlSet'):
        try:
            links[i] = urlSets[1][0].text
        except IndexError:
            links[i] = ''
        i = i + 1
        
    htmls = [None]*len(links)
    j = 0
    for i in links:
        try:
            req = urllib2.Request(i)
            response = urllib2.urlopen(req)
            htmls[j] = response.read()
        except ValueError:
            htmls[j] = ''
        j = j + 1
    if len(htmls) == 1:
        htmls = htmls[0]    
    return htmls