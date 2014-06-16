# -*- coding: utf-8 -*-
"""
Created on Thu May 10 14:57:30 2012

@author: Shreejoy
"""
import urllib2
import sleep

COOKIE = '664d9ed4a110fa1deb0dc4cc2d7e76fa00a75a0b5c9b3fa8'
def getpage(url,login=False,sleep_time=0.5):
  sleep(sleep_time) # Sleep for half a second to keep from making too many requests within a short period of time.  
  if login:
      opener = urllib2.build_opener()
      opener.addheaders.append(('Cookie','USER_STATE_COOKIE=%s' % COOKIE))
      page = opener.open(url)
  else:
      page = urllib2.urlopen(url)
      html = page.read()
  return html