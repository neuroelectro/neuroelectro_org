# -*- coding: utf-8 -*-
"""
Created on Sun Jan 27 16:10:16 2013

@author: Shreejoy
"""
import os
#import django_startup
import re
import struct
import gc
from matplotlib.pylab import *
import neuroelectro.models as m

from django.db import transaction
from django.db.utils import DatabaseError
from django.core.files import File
from xml.etree.ElementTree import XML
from urllib import quote_plus, quote
from urllib2 import Request, urlopen, URLError, HTTPError
from xml.etree.ElementTree import XML
import json
from pprint import pprint
from bs4 import BeautifulSoup
import time

from HTMLParser import HTMLParseError
from lxml import etree
import glob

from db_add import add_single_article_full, get_article_full_text_url, get_journal
from html_table_decode import assocDataTableEphysVal, assocDataTableEphysValMult
from article_text_processing import assocNeuronstoArticleMult2
from db_add_full_text_wiley import make_html_filename
from assign_metadata import assign_species, assign_electrode_type


def add_article_full_text_from_file(file_name, path):
   os.chdir(path)
   pmid_str = re.match('\d+_', file_name).group()[:-1]
   journal_name = get_journal(pmid_str)
   # is journal one among list of full text journals?
   if not isFullTextJournal(journal_name):
#       with open("analyzed_files.txt", "a") as af:
#           write_str = '%s\n' % file_name
#           af.write(write_str)
       return None
   # does journal already have full text assoc with it?
   if m.ArticleFullText.objects.filter(article__pmid = pmid_str).count() > 0:
       return None
   f = open(file_name, 'r')
   full_text = f.read()
   #print full_text
   
#   with open("analyzed_files.txt", "a") as af:
#       write_str = '%s\n' % file_name
#       af.write(write_str)

   name_str, file_ext = os.path.splitext(file_name)
   # first check if any tables
   if file_ext == '.xml':
       html_tables = extract_tables_from_xml(full_text, file_name)
   else:
       html_tables = extract_tables_from_html(full_text, file_name)
#   if len(html_tables) == 0: # don't do anything if no tables
#       return None
#   pmid_str = re.match('\d+_', file_name).group()[:-1]
   #print 'adding article with pmid: %s' % pmid_str
   a = add_single_article_full(int(pmid_str))
   if a is None:
       f.close()
       return None
   
   #print 'getting full text link for %s: ' % pmid_str
   full_text_url = get_article_full_text_url(pmid_str)
   a.full_text_link = full_text_url
   a.save()
   try:
       f = open(file_name, 'r')
       file_ob = File(f)
       aft = m.ArticleFullText.objects.get_or_create(article = a)[0]
       aft.full_text_file.save('new', file_ob)
#       aft.full_text_file.name = file_name
       f.close()
       file_ob.close()
   except Exception, e:
      with open('failed_files.txt', 'a') as f:
          f.write('%s\\%s' % (file_name, e))
      print e
      print file_name
      f.close()
   if html_tables is not None:
       # do a check to see if tables already exist, if do, just return
       if a.datatable_set.all().count() > 0:
           return a
       #print 'adding %d tables' % (len(html_tables))
       
       #get neuronarticlemaps here
       
       # for each data table
       for table in html_tables:
           tableSoup = BeautifulSoup(table)
           table_html = str(tableSoup)
           table_html = add_id_tags_to_table(table_html)
           table_text = tableSoup.get_text()
           table_text = table_text[0:min(9999,len(table_text))]
           data_table_ob = m.DataTable.objects.get_or_create(article = a, table_html = table_html, table_text = table_text)[0]
           ds = m.DataSource.objects.get_or_create(data_table=data_table_ob)[0]    
           
           #assign ephys properties to table here
           #assocDataTableEphysVal(data_table_ob)
       #data_table_ob = addIdsToTable(data_table_ob)
   return a

def add_multiple_full_texts_all(path):
    os.chdir(path)
    file_name_list_xml = [f for f in glob.glob("*.xml")]
    file_name_list_html = [f for f in glob.glob("*.html")]
    file_name_list = file_name_list_xml
    file_name_list.extend(file_name_list_html)
    if os.path.isfile('analyzed_files.txt'):
        # read files
        f = open('analyzed_files.txt')
        lines = f.readlines()
        f.close()
        # need to remove newline from lines
        new_lines = []
        for l in lines:
            new_lines.append(l[:-1])
        file_name_list = list(set(file_name_list).difference(set(new_lines)))
    
    num_files = len(file_name_list)
    print 'adding %s files...' % num_files
    for i,f in enumerate(file_name_list):
        prog(i, num_files)
        add_article_full_text_from_file(f, path)

def add_multiple_full_texts(path, publisher):
    os.chdir(path)
    if publisher == 'elsevier':
        file_name_list = [f for f in glob.glob("*.xml")]
    else:
        file_name_list = [f for f in glob.glob("*.html")]
    if os.path.isfile('analyzed_files.txt'):
        # read files
        f = open('analyzed_files.txt')
        lines = f.readlines()
        f.close()
        # need to remove newline from lines
        new_lines = []
        for l in lines:
            new_lines.append(l[:-1])
        file_name_list = list(set(file_name_list).difference(set(new_lines)))
    
    num_files = len(file_name_list)
    print 'adding %s files...' % num_files
    for i,f in enumerate(file_name_list):
        prog(i, num_files)
        add_article_full_text_from_file(f, path)
        
def add_old_full_texts():
    article_list = m.Article.objects.filter(datatable__datasource__neuronephysdatamap__val__isnull = False).distinct()
    path = "K:\Full_text_dir\Neuro_full_texts"
    publisher = "Highwire"
    os.chdir(path)
    file_name_list = []
    for a in article_list:
        file_name_list.append(make_html_filename(a.title, a.pmid))
#    file_name_list = [f for f in glob.glob("*.html")]
#    file_name_list_act
    if os.path.isfile('analyzed_files.txt'):
        # read files
        f = open('analyzed_files.txt')
        lines = f.readlines()
        f.close()
        # need to remove newline from lines
        new_lines = []
        for l in lines:
            new_lines.append(l[:-1])
        file_name_list = list(set(file_name_list).difference(set(new_lines)))
    
    num_files = len(file_name_list)
    print 'adding %s files...' % num_files
    for i,f in enumerate(file_name_list):
        prog(i, num_files)
        add_article_full_text_from_file(f, path, publisher)
    

def extract_tables_from_xml(full_text_xml, file_name):
    xslt_root = etree.parse("cals_merge.xsl")
    transform = etree.XSLT(xslt_root)
    soup = BeautifulSoup(full_text_xml)
    tables = soup.find_all('ce:table')
    html_tables = []
    for table in tables:
        table_str = unicode(table)
        #table_str = unicode(soup.find('ce:table'))
        table_str = table_str.replace('ce:', '')
        table_str = table_str.replace('xmlns="http://www.elsevier.com/xml/common/dtd"', '')
        table_str = table_str.replace('xmlns="http://www.elsevier.com/xml/common/cals/dtd"', '')
        #print table_str
        try:
            xml_input = etree.fromstring(table_str)
            table_html = etree.tostring(transform(xml_input), encoding='UTF-8')
            html_tables.append(table_html)
            #print filename
#            f = open('table_text_test2.html','w')
#            f.write(etree.tostring(transform(xml_input), encoding='UTF-8'))
#            f.close()
#            print cnt
#            cnt += 1
        except Exception, e:
            with open('failed_files.txt', 'a') as f:
                f.write('%s\\%s' % (file_name, e))
            print e
            print file_name
            #failedFiles.append([filename, e])
            continue
    return html_tables

def extract_tables_from_html(full_text_html, file_name):
    soup = BeautifulSoup(full_text_html)
    tables = soup.find_all('table')
    html_tables = []
    for table in tables:
        table_str = unicode(table)
        try:
            html_tables.append(table_str)
        except Exception, e:
            with open('failed_files.txt', 'a') as f:
                f.write('%s\\%s' % (file_name, e))
            print e
            print file_name
            #failedFiles.append([filename, e])
            continue
    return html_tables

def apply_article_metadata():
    artObs = m.Article.objects.filter(metadata__isnull = True, articlefulltext__isnull = False, 
                                      articlefulltext__articlefulltextstat__metadata_processed = False).distinct()
    num_arts = artObs.count()
    print 'annotating %s articles for metadata...' % num_arts
    for i,art in enumerate(artObs):   
        prog(i,num_arts)
        assign_species(art)
        assign_electrode_type(art)
        aft_ob = art.get_full_text()
        aftStatOb = m.ArticleFullTextStat.objects.get_or_create(article_full_text = aft_ob)[0]
        aftStatOb.metadata_processed = True
        aftStatOb.save()
    
def apply_neuron_article_maps():
    artObs = m.Article.objects.filter(neuronarticlemap__isnull = True, articlefulltext__isnull = False).distinct()
    assocNeuronstoArticleMult2(artObs)

def ephys_table_identify_all():
    artObs = m.Article.objects.filter(datatable__isnull = False, articlefulltext__isnull = False).distinct()
    dataTableObs = m.DataTable.objects.filter(article__in = artObs, datasource__ephysconceptmap__isnull = True).distinct()
    num_tables_total = dataTableObs.count()
    print num_tables_total
    BLOCKSIZE = 2000
    num_blocks = num_tables_total / BLOCKSIZE
    
    currTableInd = 0
    loop_cnt = 0
    while currTableInd < num_tables_total:
        print 'block %d of %d' % (loop_cnt, num_blocks)
        pk_inds = range(currTableInd,minimum(currTableInd+BLOCKSIZE,num_tables_total))
        #dataTableObsBlock = dataTableObs[currTableInd:minimum(BLOCKSIZE,len(dataTableObs))]
        ephys_table_identify_block(pk_inds)
        gc.collect()
        currTableInd += BLOCKSIZE
        loop_cnt += 1
       
def ephys_table_identify_block(pk_inds):
    dataTableObs = m.DataTable.objects.filter(pk__in = pk_inds).distinct()
    num_tables = dataTableObs.count()
    print 'analyzing %s tables in block' % num_tables
    for i,dt in enumerate(dataTableObs):    
        #prog(i, num_tables)
        assocDataTableEphysVal(dt)  
        
def ephys_table_identify():
    artObs = m.Article.objects.filter(datatable__isnull = False, articlefulltext__isnull = False).distinct()
    dataTableObs = m.DataTable.objects.filter(article__in = artObs).distinct()
    num_tables = dataTableObs.count()
    print 'analyzing %s tables' % num_tables
    for i,dt in enumerate(dataTableObs):    
        #prog(i, num_tables)
        assocDataTableEphysVal(dt)           
        
def prog(num,denom):
    fract = float(num)/denom
    hyphens = int(round(50*fract))
    spaces = int(round(50*(1-fract)))
    sys.stdout.write('\r%.2f%% [%s%s]' % (100*fract,'-'*hyphens,' '*spaces))
    sys.stdout.flush() 
        
def add_id_tags_to_table(table_html):
    try:
        soup = BeautifulSoup(table_html)
    except:
        return
    tdTags = soup.findAll('td')
    if len(soup.find_all(id=True)) == 0:
        #print 'adding id tags to table # %d' %dataTableOb.pk
        # contains no id tags, add them
        tdTags = soup.findAll('td')
        cnt = 1
        for tag in tdTags:
            tag['id'] = 'td-%d' % cnt
            cnt += 1
        thTags = soup.findAll('th')
        cnt = 1
        for tag in thTags:
            tag['id'] = 'th-%d' % cnt
            cnt += 1   
        trTags = soup.findAll('tr')
        cnt = 1
        for tag in trTags:
            tag['id'] = 'tr-%d' % cnt
            cnt += 1  
    
    table_html = str(soup)   
    return table_html

   

def get_full_text_from_link(fullTextLink):
#    searchLinkFull = 'http://jn.physiology.org/search?tmonth=Mar&pubdate_year=&submit=yes&submit=yes&submit=Submit&andorexacttitle=and&format=condensed&firstpage=&fmonth=Jan&title=&tyear=2012&hits=' + str(NUMHITS) + '&titleabstract=&flag=&journalcode=jn&volume=&sortspec=date&andorexacttitleabs=and&author2=&andorexactfulltext=and&author1=&fyear=1997&doi=&fulltext=%22input%20resistance%22%20AND%20neuron&FIRSTINDEX=' + str(firstInd)
#    fullTextLink = 'http://jn.physiology.org/content/107/6/1655.full'   
    (soup, fullTextLink) = soupify_plus(fullTextLink) 
#    isPdf = checkPdf(fullTextLink)
    if soup is False:
        return False
    #    print BeautifulSoup.prettify(soup)
    # find pubmed link and pmid
    try:
        tempStr = re.search('access_num=[\d]+', str(soup('a',text=('PubMed citation'))[0])).group()
    except (IndexError):
        return False
    pmid = int(re.search('\d+', tempStr).group())
    if Article.objects.filter(pmid = pmid).count() == 0:
        # add pmid abstract and stuff to db Article list
        add_articles([pmid])
    
    # get Article object
    art = Article.objects.get(pmid = pmid)
    art.full_text_link = fullTextLink
    art.save()
    
    # get article full text and save to object
    fullTextTag = soup.find('div', {'class':'article fulltext-view'})
#    fullTextTag = soup.find('div', {'itemprop':'articleBody'})

#    # tag finder for j-neurophys
#    tags = soup.find_all('div')
#    for t in tags:
#        if 'itemprop' in t.attrs and t['itemprop'] == 'articleBody':
#            fullTextTag = t
#            break
    fullTextOb = ArticleFullText.objects.get_or_create(article = art)[0]
    fullTextOb.full_text = str(fullTextTag)
    fullTextOb.save()
    
    # get article data table links
    # just count number of tables in article
#    tableList = []
    numTables = 0
    for link in soup.find_all('a'):
        linkText = link.get('href')
        if link.string == 'In this window' and linkText.find('T') != -1:
            print(linkText)
            numTables += 1
#            tableList.append(linkText)
    
    print 'adding %d tables' % (numTables)
    for i in range(numTables):
        tableLink = fullTextLink[:-5] + '/T' + str(i+1)  
        tableSoup = soupify(tableLink)
        if tableSoup is False:
            continue
        tableTag = tableSoup.find('div', {'class':'table-expansion'})
        if tableTag is None:
            tableTag = soup.find('div', {'itemprop':'articleBody'})
        dataTableOb = DataTable.objects.get_or_create(link = tableLink, article = art)[0]
        table_html = str(tableTag)
        
        dataTableOb.table_html = table_html
        table_text = tableTag.get_text()
        table_text = table_text[0:min(9999,len(table_text))]
        dataTableOb.table_text = table_text
        dataTableOb.save()
        
def isFullTextJournal(journal_name):
    valid_journals_names = ['Brain research', 'Neuroscience letters', 'Neuron', 'Molecular and cellular neurosciences',
                            'Neuroscience', 'Neuropsychologia', 'Neuropharmacology' 'Brain research bulletin', 
                            'Biophysical journal', 'Biophysical reviews and letters',
                            'Journal of neuroscience research', 'Hippocampus', 'Glia', 'The European journal of neuroscience', 'Synapse (New York, N.Y.)',
                            'The Journal of physiology', 'Epilepsia',
                            'The Journal of neuroscience : the official journal of the Society for Neuroscience', 'Journal of neurophysiology']  
    if journal_name in valid_journals_names:
        return True
    else:
        return False