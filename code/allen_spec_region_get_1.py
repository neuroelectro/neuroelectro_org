# -*- coding: utf-8 -*-
"""
Created on Tue Feb 07 10:16:04 2012

@author: Shreejoy
"""


link = http://mouse.brain-map.org/mouse/data/P56/search/list_rows/54QMD41OUJ12?numRows=100&startRow=0&showDetail=0


from xml.etree.ElementTree import XML
from urllib2 import urlopen, build_opener
import json
from pprint import pprint
from pubapp.models import Neuron, Article, IonChannel, NeuronSyn, InSituExpt
from django.core.exceptions import ObjectDoesNotExist

import os.path
import urllib2
from numpy  import *

COOKIEFILE = 'cookies.lwp'
# the path and filename to save your cookies in

cj = None
ClientCookie = None
cookielib = None

# Let's see if cookielib is available
try:
    import cookielib
except ImportError:
    # If importing cookielib fails
    # let's try ClientCookie
    try:
        import ClientCookie
    except ImportError:
        # ClientCookie isn't available either
        urlopen = urllib2.urlopen
        Request = urllib2.Request
    else:
        # imported ClientCookie
        urlopen = ClientCookie.urlopen
        Request = ClientCookie.Request
        cj = ClientCookie.LWPCookieJar()
else:
    # importing cookielib worked
    urlopen = urllib2.urlopen
    Request = urllib2.Request
    cj = cookielib.LWPCookieJar()
    # This is a subclass of FileCookieJar
    # that has useful load and save methods

if cj is not None:
# we successfully imported
# one of the two cookie handling modules
    if os.path.isfile(COOKIEFILE):
        # if we have a cookie file already saved
        # then load the cookies into the Cookie Jar
        cj.load(COOKIEFILE)
    # Now we need to get our Cookie Jar
    # installed in the opener;
    # for fetching URLs
    if cookielib is not None:
        # if we use cookielib
        # then we get the HTTPCookieProcessor
        # and install the opener in urllib2
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
        urllib2.install_opener(opener)
    else:
        # if we use ClientCookie
        # then we get the HTTPCookieProcessor
        # and install the opener in ClientCookie
        opener = ClientCookie.build_opener(ClientCookie.HTTPCookieProcessor(cj))
        ClientCookie.install_opener(opener)


# an example url that sets a cookie,
# try different urls here and see the cookie collection you can make !

txdata = None
# if we were making a POST type request,
# we could encode a dictionary of values here,
# using urllib.urlencode(somedict)

txheaders =  {
'User-agent' : 'Mozilla/5.0 (Windows NT 6.1; WOW64)',
'Accept-Charset' : 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
'Cookie': 'preferences=wildcards:t; BIGipServerBAwebpool=1697203978.20480.0000; chkcookie=1328630643961',
}

link = 'http://mouse.brain-map.org/api/v2/data/SectionDataSet/472.json?wrap=false&include=structure_unionizes(structure%5Bid%24in236%2C698%2C1089%2C703%2C477%2C803%2C512%2C549%2C1097%2C313%2C771%2C354%5D)&only=id%2Cname%2Cexpression_energy%2Cacronym'
exprRatio = {}
for pageNum in range(192):
    print pageNum
    theurl = 'http://mouse.brain-map.org/mouse/data/P56/search/list_rows/TBQWJW1PYK11?numRows=100&startRow=%d&showDetail=0' %((pageNum)*100 + 1)
    req = Request(theurl, txdata, txheaders)
    handle = urlopen(req)
    json_data = json.loads(handle.read())
    for i in range(len(json_data)):
        isid = json_data[i]['id']
        foldchange = float(json_data[i]['fold-change'])
        exprRatio[isid] = foldchange

# get corresponding data from database
reg1Abbrev = 'CA'
reg2Abbrev = 'STR'
reg1Ob = BrainRegion.objects.get(abbrev = 'CA')
reg2Ob = BrainRegion.objects.get(abbrev = 'STR')
caExprDict = {}
strExprDict = {}
reg1Array = zeros(500)
reg2Array = zeros(500)
cnt = 0
isidList = exprRatio.keys()
ratioList = exprRatio.values()
for isid in isidList[0:500]:
    print cnt
    try:
        ise = InSituExpt.objects.get(imageseriesid = int(isid))
        reg1Val = ise.regionexprs.get(region = reg1Ob).val
        reg2Val = ise.regionexprs.get(region = reg2Ob).val
        reg1Array[cnt] = reg1Val
        reg2Array[cnt] = reg2Val
    except ObjectDoesNotExist:
        print '%s does not exist in db' % isid
        reg1Array[cnt] = -1
        reg2Array[cnt] = -1
    cnt += 1

ratioList[0:500]
myRatio = reg1Array/reg2Array

reg1Array = []
reObs = RegionExpr.objects.filter(region = reg1Ob)
reObs.annotate()
for re in reObs:
    reObs.val
    
GET /mouse/data/P56/search/list_rows/6E5FE51ZLK11?numRows=20&startRow=0&showDetail=1 HTTP/1.1
Host: mouse.brain-map.org
Connection: keep-alive
X-Requested-With: XMLHttpRequest
User-Agent: Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.7 (KHTML, like Gecko) Chrome/16.0.912.77 Safari/535.7
Accept: application/json, text/javascript, */*; q=0.01
Referer: http://mouse.brain-map.org/search/show?page_num=0&page_size=20&no_paging=false&domain1=477&domain2=375&domain1_threshold=0,50&domain2_threshold=0,50&image_set=P56&search_type=differential
Accept-Encoding: gzip,deflate,sdch
Accept-Language: en-US,en;q=0.8
Accept-Charset: ISO-8859-1,utf-8;q=0.7,*;q=0.3
Cookie: preferences=wildcards:t; BIGipServerBAwebpool=1697203978.20480.0000; chkcookie=1328629618284


try:
    req = Request(theurl, txdata, txheaders)
    # create a request object
    handle = urlopen(req)
    # and open it to return a handle on the url
except IOError, e:
    print 'We failed to open "%s".' % theurl
    if hasattr(e, 'code'):
        print 'We failed with error code - %s.' % e.code
    elif hasattr(e, 'reason'):
        print "The error object has the following 'reason' attribute :"
        print e.reason
        print "This usually means the server doesn't exist,',
        print "is down, or we don't have an internet connection."
    sys.exit()
else:
    print 'Here are the headers of the page :'
    print handle.info()
    # handle.read() returns the page
    # handle.geturl() returns the true url of the page fetched
    # (in case urlopen has followed any redirects, which it sometimes does)
print
if cj is None:
    print "We don't have a cookie library available - sorry."
    print "I can't show you any cookies."
else:
    print 'These are the cookies we have received so far :'
    for index, cookie in enumerate(cj):
        print index, '  :  ', cookie
    cj.save(COOKIEFILE)                     # save the cookies again
    
link = 'http://mouse.brain-map.org/mouse/data/P56/search/list_rows/QLJNTL1FRK14?numRows=20&startRow=0&showDetail=1'
GET /mouse/data/P56/search/list_rows/P4OWS4150K11?numRows=20&startRow=0&showDetail=1 HTTP/1.1
Host: mouse.brain-map.org
Connection: keep-alive
X-Requested-With: XMLHttpRequest
User-Agent: Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.7 (KHTML, like Gecko) Chrome/16.0.912.77 Safari/535.7
Accept: application/json, text/javascript, */*; q=0.01
Referer: http://mouse.brain-map.org/search/show?page_num=0&page_size=20&no_paging=false&domain1=477&domain2=375&domain1_threshold=0,50&domain2_threshold=0,50&image_set=P56&search_type=differential
Accept-Encoding: gzip,deflate,sdch
Accept-Language: en-US,en;q=0.8
Accept-Charset: ISO-8859-1,utf-8;q=0.7,*;q=0.3
Cookie: preferences=wildcards:t; BIGipServerBAwebpool=1697203978.20480.0000; chkcookie=1328628132783
GET /mouse/data/P56/search/list_rows/QLJNTL1FRK14?numRows=20&startRow=0&showDetail=1 HTTP/1.1
Host: mouse.brain-map.org
Connection: keep-alive
X-Requested-With: XMLHttpRequest
User-Agent: Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.7 (KHTML, like Gecko) Chrome/16.0.912.77 Safari/535.7
Accept: application/json, text/javascript, */*; q=0.01
Referer: http://mouse.brain-map.org/search/show?page_num=0&page_size=20&no_paging=false&domain1=477&domain2=375&domain1_threshold=0,50&domain2_threshold=0,50&image_set=P56&search_type=differential
Accept-Encoding: gzip,deflate,sdch
Accept-Language: en-US,en;q=0.8
Accept-Charset: ISO-8859-1,utf-8;q=0.7,*;q=0.3
Cookie: preferences=wildcards:t; BIGipServerBAwebpool=1697203978.20480.0000; chkcookie=1328630078468


opener = build_opener()
opener.addheaders.append(('Cookie', 'preferences=wildcards:t; BIGipServerBAwebpool=1697203978.20480.0000; chkcookie=1328628132783'))
handle = urlopen(link)
data = handle.read()

json_data = json.loads(data)
xml = XML(data)

data[u'name']

regionDict = {}
for i in range(len(json_data)):
    abbrev = json_data[i]['acronym']
    structId = json_data[i]['structure_id']
    regionDict{abbrev: structId}    