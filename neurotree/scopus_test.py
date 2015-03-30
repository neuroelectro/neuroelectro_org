# -*- coding: utf-8 -*-
"""
Created on Thu Dec 19 09:14:34 2013

@author: Shreejoy
"""

queryStr = "input resistance resting membrane potential neuron"
def get_full_text_links(queryStr):
    NUMHITS = 200
    maxURLTries = 5
    waitTime = 60
    
    queryStrQuoted = re.sub(' ', '+', queryStr)
    testYears = list(range(1996,2013))
    #testYears = [2000]
    queryStrBase = "http://api.elsevier.com/content/search/index:AUTHOR?query=authlast(%s)&authfirst(%s)&subjarea(NEUR)"
    queryStr = queryStrBase % ('Karten', 'Harvey')
    query = re.sub('&', '%20AND%20', queryStr)    
    
    #queryStr = "http://api.elsevier.com/content/search/index:AUTHOR?query=AUTHOR-NAME(%s)"    
    queryStrQuoted = re.sub(' ', '+', queryStr)    
    resultList = []
    
    headerDict = {"X-ELS-APIKey":ELS_API_KEY,
               "X-ELS-ResourceVersion": "XOCS" ,
               "Accept": "application/json"}
    for currYear in testYears:
            firstInd = 0
        # figure out how many search results are in this year:
            searchLinkFull = searchLinkBase % (queryStrQuoted, currYear, 1, 0)
            
            request = Request(searchLinkFull, headers = headerDict)
            contents = urlopen(request).read()
            resultDict = json.loads(contents)
            totalArticles = int(resultDict['search-results']['opensearch:totalResults'])

            while firstInd <= totalArticles:
                print('searching %d of %d articles' % (firstInd, totalArticles))
                searchLinkFull = searchLinkBase % (queryStrQuoted, currYear, NUMHITS, firstInd)
                request = Request(searchLinkFull, headers = headerDict)
                contents = urlopen(request).read()
                resultDict = json.loads(contents)
                searchResults = resultDict['search-results']['entry']
                resultList.extend(searchResults)
                firstInd += NUMHITS 
                
    return resultList
    
authorIdQueryBase = "http://api.elsevier.com/content/search/index:SCOPUS?query=au-id(7006830307)&doctype(ar)&pubdatetxt(2013)"
#queryStr = authorIdQueryBase % (7006830307)
query = re.sub('&', '%20AND%20', authorIdQueryBase)    
    