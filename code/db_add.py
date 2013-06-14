# -*- coding: utf-8 -*-
"""
Created on Tue Jan 24 00:05:33 2012

@author: Shreejoy
"""

# -*- coding: utf-8 -*-
"""
Created on Tue Nov 08 16:51:31 2011

@author: Shreejoy
"""

import os
#import django_startup
import re
import struct
import gc
import glob
import sys
import numpy as np
#os.chdir('C:\Python27\Scripts\Biophys\Biophysiome')
from neuroelectro.models import Article, MeshTerm, Substance, Journal, Author
#from pubapp.models import Neuron, IonChannel, NeuronChanEvid
from neuroelectro.models import BrainRegion, InSituExpt, Protein, RegionExpr
#os.chdir('C:\Python27\Scripts\Biophys')

from django.db import transaction
from xml.etree.ElementTree import XML, ParseError
from urllib import quote_plus, quote
from urllib2 import Request, urlopen, URLError, HTTPError
from httplib import BadStatusLine
from xml.etree.ElementTree import XML
import json
from pprint import pprint



efetch = "http://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?&db=pubmed&retmode=xml&id=%s"
esummary = "http://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&id=%s&version=2.0"
def add_articles(pmids):
    if len(pmids) > 5:
        currPmids = [str(article.pmid) for article in Article.objects.all()]
        pmids = list(set(pmids).difference(set(currPmids)))
    cnt = 0
    MAXURLTRIES = 5
    print 'adding %u articles into database' % (len(pmids))
    with transaction.commit_on_success():
        failedArts = []
        for article in pmids:
            #check if article already is in db
            if len(Article.objects.filter(pmid = article)) > 0:
                cnt += 1
                if cnt % 100 == 0:
                    print '%d of %d articles' % (cnt, len(pmids))
#                print '%u of %u articles' % (cnt, len(pmids))
                continue
            else:
                cnt += 1
                add_single_article_full(pmid)
    return failedArts
    
# adds info for article, first checks if pmid already exists
def add_single_article(pmid):
    MAXURLTRIES = 5
    #check if article already is in db
    if len(Article.objects.filter(pmid = pmid)) > 0:
		a = Article.objects.get(pmid = pmid)
    else:
		a = add_single_article_full(pmid)
    return a
    
def get_journal(pmid):
    MAXURLTRIES = 5
    numTries = 0
    success = False
    link = esummary % (pmid)
    req = Request(link)
    while numTries < MAXURLTRIES and success == False: 
		try: 
			handle = urlopen(req)
			success = True
		except (URLError, HTTPError, BadStatusLine, ParseError):
			print ' failed %d times' % numTries 
			numTries += 1
#                        print URLError
    if numTries == MAXURLTRIES:
        journal_title = None 
        return journal_title
    try:                        
        data = handle.read()
        xml = XML(data)    
        journalXML = xml.find('.//FullJournalName')
        if journalXML is not None:
    		journal_title = journalXML.text
        else:
    		journal_title = None
        return journal_title
    except Exception, e:
        journal_title = None 
        return journal_title
	
# adds all info for article, doesn't check if already exists
def add_single_article_full(pmid):
    MAXURLTRIES = 5
    numTries = 0
    success = False
    link = efetch % (pmid)
    req = Request(link)
    while numTries < MAXURLTRIES and success == False: 
		try: 
			handle = urlopen(req)
			success = True
		except (URLError, HTTPError, BadStatusLine, ParseError):
			print ' failed %d times' % numTries 
			numTries += 1
#                        print URLError
    if numTries == MAXURLTRIES:
        a = None 
        return a
    try:                        
        data = handle.read()
        xml = XML(data)    
        titleXML = xml.find('.//ArticleTitle')
        if titleXML is not None:
    		title = titleXML.text
        else:
    		title = ' '
	
	# generate a new article in db

        a = Article.objects.get_or_create(title=title, pmid = pmid)[0]
    except Exception, e:
        a = None
        return a
	# add journalTitle to article
    journalTitle = xml.find('.//Title')
    if journalTitle is not None:
		j = Journal.objects.get_or_create(title = journalTitle.text)[0]
		a.journal = j
		if j.short_title is None:
			shortJournalTitleXML = xml.find('.//ISOAbbreviation')
			if shortJournalTitleXML is not None:
				j.short_title = shortJournalTitleXML.text 
				j.save()
	
	# add authors to article
    authorList = xml.findall(".//Author[@ValidYN='Y']")
    if len(authorList) == 0:
		authorList = xml.findall(".//Author")
    authorListText = []
    for author in authorList:
		#print author.text
		try:
			last = author.find("./LastName").text
			fore = author.find("./ForeName").text
			initials = author.find("./Initials").text
			#print last, fore, initials
			authorOb = Author.objects.get_or_create(first=fore, last=last, initials=initials)[0]
			a.authors.add(authorOb)
			currAuthorStr = '%s %s' % (last, initials)
			authorListText.append(currAuthorStr)
		except AttributeError:
			continue  
    author_list_str = '; '.join(authorListText)    
    author_list_str = author_list_str[0:min(len(author_list_str), 500)]
    a.author_list_str = author_list_str		 
	
	#get publication year
    pub_year = xml.find(".//PubDate/Year")
    if pub_year is not None:
		a.pub_year = int(pub_year.text)   
	# find mesh terms and add them to db
    for x in xml.findall('.//DescriptorName'):
		if x.text is not None:
			m = MeshTerm.objects.get_or_create(term = x.text)[0]
			a.terms.add(m)
	
	# find substances and add them to db
    for x in xml.findall('.//NameOfSubstance'):
		if x.text is not None:
			s = Substance.objects.get_or_create(term = x.text)[0]
			a.substances.add(s)    
	
    abstractXML = xml.findall('.//AbstractText')
    abstract = ' '
#                print 'abstract len %d' % len(abstractXML)
    if len(abstractXML) > 0:
		abstractList = [x.text for x in abstractXML]
		abstractList = filter(None, abstractList)
#                    print abstractList
		abstract = ' '.join(abstractList)
    a.abstract = abstract
    a.save()
    return a
    
def get_article_full_text_url(pmid):
    base_url = 'http://eutils.ncbi.nlm.nih.gov/entrez/eutils/elink.fcgi?dbfrom=pubmed&id=%s&cmd=prlinks&retmode=ref'
    url = base_url % pmid
    #print url
    try:
        req = Request(url)
        res = urlopen(req)
        final_url = res.geturl()
    except Exception:
        final_url = url
    return final_url
#elink = '
#def add_article_full_text_links():
#    arts = Article.objects.filter(full_text_link__isnull = True)
#    pmids = [str(a.pmid) for a in arts]
##    currPmids = [str(article.pmid) for article in Article.objects.all()]
##    pmids = list(set(pmids).difference(set(currPmids)))
#    cnt = 0
#    MAXURLTRIES = 5
#    print 'adding %u articles into database' % (len(pmids))
#    with transaction.commit_on_success():
#        failedArts = []
#        for article in pmids:    
#            cnt += 1
#            numTries = 0
#            success = False
#            if cnt % 100 == 0:
#                print '%d of %d articles' % (cnt, len(pmids))
#            link = efetch % (article)
#            req = Request(link)
#            while numTries < MAXURLTRIES and success == False: 
#                try: 
#                    handle = urlopen(req)
#                    success = True
#                except (URLError, HTTPError):
#                    print article + ' failed %d times' % numTries 
#                    numTries += 1
##                        print URLError
#            if numTries == MAXURLTRIES:
#                failedArts.append(article)
#                continue                                
#            data = handle.read()
#            xml = XML(data)    
                
def add_neuron_channel_links(linkMat):
    neurons = Neuron.objects.all()
    channels = IonChannel.objects.all()
    numNeurons = len(linkMat)
    numChannels= len(linkMat[1])
    skipList = []
    with transaction.commit_on_success():
        for i in range(numNeurons):
            currNeuron = neurons[i]
            
            for j in range(numChannels):
                currChannel = channels[j]
                currPmids = linkMat[i][j]
                if len(currPmids) > 0:
                    print '\n' + currNeuron.name + ' ' + currChannel.name
                    # check to see if some evid already is in db
                    query = NeuronChanEvid.objects.filter(neuron = currNeuron, ionchannel = currChannel)
                    
                    if len(currPmids) > 500:
                        skipList.append((i,j))
                        print 'Skipping %s , %s' %  (currNeuron.name, currChannel.name)
                        continue
                    
                    articleObList = Article.objects.filter(pmid__in = currPmids)

                             
                    if len(query) > 0:
                        nce = query[0]
                        existingArtObs = Article.objects.filter(neuronchanevid = nce)
#                        print 'existing abstracts = ' + existingArtObs
                        articleObList = list(set(articleObList).union(set(existingArtObs)))
                        nce.articles = articleObList
                        nce.numartices = len(articleObList)
                    else:
                        nce = NeuronChanEvid.objects.create(neuron = currNeuron, \
                        ionchannel = currChannel)
                        nce.articles = articleObList
                        nce.numartices = len(articleObList)
#                    print [a.title for a in articleObList]
                    print 'adding %u articles' % (len(articleObList))
                    nce.save()     
    add_neuron_channel_links_skipped(skipList, linkMat)

def add_neuron_channel_links_skipped(skipList, linkMat):
    neurons = Neuron.objects.all()
    channels = IonChannel.objects.all() 
    with transaction.commit_on_success():
        for i in range(len(skipList)):
            currNeuron = neurons[skipList[i][0]]
            currChannel = channels[skipList[i][1]]
            currPmids = linkMat[skipList[i][0]][skipList[i][1]]
            print '\n' + currNeuron.name + ' ' + currChannel.name
            query = NeuronChanEvid.objects.filter(neuron = currNeuron, ionchannel = currChannel)
            if len(query) > 0:
                nce = query[0]
            else:
                nce = NeuronChanEvid.objects.create(neuron = currNeuron, \
                ionchannel = currChannel)
            
            for pmid in currPmids:
                a = Article.objects.get(pmid = pmid)
                nce.articles.add(a)
            nce.numartices = len(currPmids)
            nce.save()  

def count_num_articles_nce():
    neurons = Neuron.objects.all()
    channels = IonChannel.objects.all()
    with transaction.commit_on_success():
        for i in range(len(neurons)):
            print neurons[i]
            for j in range(len(channels)):
                
                query = NeuronChanEvid.objects.filter(neuron = neurons[i], ionchannel = channels[j])
                if len(query) is 0:
                    continue
                
                nce = query[0]
                arts = Article.objects.filter(neuronchanevid = nce)
                print channels[j].name + ' ' + unicode(len(arts))
#                print nce.numarticles
                nce.numarticles = len(arts)
                print nce.numarticles
                nce.save()


            
def assign_allen_mean_reg_expr():
          
    bvaBase = 'http://mouse.brain-map.org/aba/api/expression/%s.bva'
    unpackStr = '159326f'
    regionObs = BrainRegion.objects.filter(isallen = True)
    numRegions = len(regionObs)
    
    MAXURLTRIES = 5
    failedisids = []
    BLOCKSIZE = 2000
    
    # only get ise exprs for ise's without bva files
    iseObs = InSituExpt.objects.filter(regionexprs__isnull = True, valid = True)
    cnt = 0
    with transaction.commit_on_success():
        for ise in iseObs[0:minimum(BLOCKSIZE,len(iseObs))]:
#            for j in range(BLOCKSIZE):        
            isid = ise.imageseriesid
            bvaLink = bvaBase % (isid)
            req = Request(bvaLink)
            numTries = 0
            success = False
            while numTries < MAXURLTRIES and success == False: 
                try: 
                    handle = urlopen(req)
                    binData = handle.read()
                    exprVals =  struct.unpack(unpackStr, binData)
                    exprVals = array(exprVals)
#                    ise.bva = exprVals
                    exprObs = []
                    for i in range(numRegions):
                        regionOb = regionObs[i]
                        meanExpr = computeAvgExpr(regionOb, exprVals)
                        regionExprOb = RegionExpr.objects.create(region = regionOb, val = meanExpr)
                        exprObs.append(regionExprOb)
                    
                    ise.regionexprs = exprObs
                    ise.save()
                    success = True  
#                    print 'imageseries %d succeeded' % (isid)
                except (URLError, HTTPError):
                    numTries += 1
                    print 'imageseries %d failed %d times' % (isid, numTries)
                    if numTries == MAXURLTRIES:
                        failedisids.append(isid)
                        ise.valid = False
                        ise.save()
            print '%d of %d elems' % (cnt, len(iseObs))
            cnt += 1
        print 'committing'
        return failedisids

def assign_allen_mean_expr_all():
    failedisids = []
    isObLen = len(InSituExpt.objects.filter(regionexprs__isnull = True, valid = True))
    while isObLen > 0:
        failed = assign_allen_mean_reg_expr()
        gc.collect()
        failedisids.extend(failed)
    return failedisids
    
def computeAvgExpr(regionOb, voxels):
    voxelInds = regionOb.voxelinds
#    print voxelInds
#    voxelInds = getRegionVoxels(region, brain_regions, allen_labelled_voxels)
    obsVoxelVals = voxels[array(voxelInds, int)]
    obsVoxelVals = obsVoxelVals.compress((obsVoxelVals > -1).flat)
    meanExpr = mean(obsVoxelVals)
    if math.isnan(meanExpr):
        meanExpr = -1
    return meanExpr


def add_all_allen_data(txtFile):
    with transaction.commit_on_success():
        a = txtFile
        lines = a.splitlines()
        cnt = 0
        currIseObs = InSituExpt.objects.all()
        currisidList = list(sort([currIseObs[i].imageseriesid for i in range(currIseObs.count())]))
        for line in lines[1:-1]:
            if cnt % 1000 == 0:
                print '%d of %d elems' % (cnt, len(lines[1:-1]))
            allenid, gene, name, isid, plane, entrezid, ncbiacc = line.split('\t')
            try:
                currisidList.index(int(isid))
                ise = InSituExpt.objects.filter(imageseriesid = int(isid))[0]
            except ValueError:
                ise = InSituExpt.objects.create(imageseriesid = int(isid), plane = plane)
            p = Protein.objects.get_or_create(gene = gene, name = name, allenid = int(allenid), entrezid = int(entrezid))[0]
            p.save()
            p.in_situ_expts.add(ise)
            ise.save()       
            cnt += 1

def get_allen_gene_expts():
    link_base = 'http://api.brain-map.org/api/v2/data/Gene/query.json?criteria=products%5Bid$eq1%5D'
    link_post = '&start_row=%d&num_rows=%d'
    
    num_genes = 200
    start_row = 1
    link_post_rep = link_post % (start_row, num_genes)
    
    link_post_coded = quote(link_post_rep, ':=/&()?_')
    handle = urlopen(link_base + link_post_coded)
    data = handle.read()
    json_data = json.loads(data)
    loop_counter = 0
    total_rows = json_data['total_rows']
    with transaction.commit_on_success():
        while start_row < total_rows:
            print 'loop counter = %d' % loop_counter
            link_post_rep = link_post % (start_row, num_genes)
            link_post_coded = quote(link_post_rep, ':=/&()?_')
            handle = urlopen(link_base + link_post_coded)
            data = handle.read()
            json_data = json.loads(data)
            for gene_struct in json_data['msg']:
                #print gene_struct
                gene = gene_struct['acronym']
                allenid = gene_struct['id']
                try:
                    entrezid = gene_struct['entrez_id']
                except KeyError:
                    entrezid = None
                name = gene_struct['name']
                p = Protein.objects.get_or_create(gene = gene, name = name,
                                              allenid = allenid, entrezid = entrezid)[0]
                #print p.name
            start_row += num_genes
            loop_counter += 1
            
def get_allen_image_series():
    link_base = "http://api.brain-map.org/api/v2/data/SectionDataSet/query.json?criteria=products%5Bid$eq1%5D,genes%5Bacronym$eq'"
    link_end = "'%5D"
    
    protein_list = Protein.objects.all().distinct()
    total_proteins = protein_list.count()
    with transaction.commit_on_success():
        for j, protein_ob in enumerate(protein_list):
            prog(j, total_proteins)
            gene_name = protein_ob.gene
            link = link_base + gene_name + link_end
            handle = urlopen(link)
            data = handle.read()
            json_data = json.loads(data)
            for ise_struct in json_data['msg']:
                #print gene_struct
                failed = ise_struct['failed']          
                if not failed:
                    
                    imageseriesid = ise_struct['id']
                    valid = True
                    plane_section_id = ise_struct['plane_of_section_id']
                    if plane_section_id == 2:
                        plane = 'sagittal'
                    else:
                        plane = 'coronal'
                    ise = InSituExpt.objects.get_or_create(imageseriesid = imageseriesid, plane = plane, valid = valid)[0]
#                else:
#                    print  ise_struct['id']
#                    print 'false'
    
def prog(num,denom):
    fract = float(num)/denom
    hyphens = int(round(50*fract))
    spaces = int(round(50*(1-fract)))
    sys.stdout.write('\r%.2f%% [%s%s]' % (100*fract,'-'*hyphens,' '*spaces))
    sys.stdout.flush() 

def get_allen_regions_ver_2():
    link = 'http://mouse.brain-map.org/ontology.json'
    
    handle = urlopen(link)
    data = handle.read()
    
    json_data = json.loads(data)
    with transaction.commit_on_success():
        regionDict = {}
        for i in range(len(json_data)):
            abbrev = json_data[i]['acronym']
            structId = json_data[i]['structure_id']
            depth = json_data[i]['depth']
            color = json_data[i]['color']
            name = json_data[i]['name']
            regionDict[abbrev]= (structId)
            b = BrainRegion.objects.get_or_create(abbrev = abbrev, name = name, 
                                                  isallen = True, treedepth = depth, color = color, 
                                                  allenid = structId)[0]
            b.save()
            
def get_allen_reg_expr_ver_2():
    linkBase = 'http://api.brain-map.org/api/v2/data/SectionDataSet/%d.json?wrap=false&include=structure_unionizes(structure)'
    linkPost = '&only=id,expression_energy,expression_density,voxel_energy_cv,acronym'

    file_dir_json = '/home/shreejoy/neuroelectro_org/data/allen_json'
    os.chdir(file_dir_json)
#    regObs = BrainRegion.objects.filter(isallen = True)
    linkPostCoded = quote(linkPost, ':=/&()?_')
    
    file_name_list_json = [f for f in glob.glob("*.json")]
    
    # only run on in situ experiments without regionExprs
    iseObs = InSituExpt.objects.all()
    num_ises = iseObs.count()
#    regionObDict = {}
#    for r in regObs:
#        allenid = r.allenid
#        regionObDict[allenid] = r
#    numRuns = minimum(500, num_ises)

    for i,iseOb in enumerate(iseObs):
        #prog(i, num_ises)
        filename = '%d.json' % iseOb.imageseriesid
        if filename in file_name_list_json:
            continue
        link = linkBase % iseOb.imageseriesid
        link = link + linkPostCoded
        try:
            handle = urlopen(link)
            data = handle.read()
        except Exception:
            print iseOb.imageseriesid
        with open(filename, 'wb') as f:
            f.write(data)
#        json_data = json.loads(data)
##        print json_data
##            iseOb = InSituExpt.objects.get(imageseriesid = isid)
#        try:
#            regDicts = json_data['msg'][0]['structure_unionizes']
##                print str(len(regDicts)) + ' found regions'
#            regExprObs = []
#            for regDict in regDicts:
#                expression_energy = regDict['expression_energy']
#                expression_density = regDict['expression_density']
#                voxel_energy_cv = regDict['voxel_energy_cv']
#                regionInd = regDict['structure']['id']
#                
#                try:
#                    regionOb = regionObDict[regionInd]
#                except KeyError:
#                    continue
#                regExprOb = RegionExpr.objects.get_or_create(region = regionOb, expr_energy = expression_energy,
#                                                             expr_energy_cv = voxel_energy_cv,
#                                                             expr_density = expression_density)[0]
#                regExprObs.append(regExprOb)
#                #iseOb.regionexprs.add(regExprOb)        
#            iseOb.regionexprs = regExprObs                
##            print iseOb
##            iseOb.regionExprs.add = regExprObs
##            print regExprObs
#        except (IndexError):
#            'isid %d not found in allen db'
#            iseOb.valid = False
#        iseOb.save()                
#        cnt += 1
#    print regDict['structure']['acronym']

def get_gene_exp_mat():
    file_dir_json = '/home/shreejoy/neuroelectro_org/data/allen_json'
    save_dir = '/home/shreejoy/neuroelectro_org/data'
#    file_dir_json = 'C:\Users\Shreejoy\Desktop\Neuroelectro_org\Data\Allen_json'
#    save_dir = 'C:\Users\Shreejoy\Desktop\Neuroelectro_org\Data'
    os.chdir(file_dir_json)
    
    file_name_list_json = [f for f in glob.glob("*.json")]
    
    # only run on in situ experiments without regionExprs
    iseObs = InSituExpt.objects.all()
    num_ises = iseObs.count()
    
    regObs = BrainRegion.objects.filter(isallen = True)
    num_regions = regObs.count()
    regionObDict = {}
    for r in regObs:
        allenid = r.allenid
        regionObDict[allenid] = r.pk
        
    gene_energy_mat = np.zeros([num_ises, num_regions])
    gene_density_mat = np.zeros([num_ises, num_regions])
    gene_energy_cv_mat = np.zeros([num_ises, num_regions])
#    numRuns = minimum(500, num_ises)
    for i,ise in enumerate(iseObs):
        prog(i, num_ises)
        file_name = '%d.json' % ise.imageseriesid
        if file_name in file_name_list_json:
            json_contents = open(file_name, 'r')
            json_data = json.load(json_contents)
            json_contents.close()
#            print file_name
            
            regDicts = json_data['msg'][0]['structure_unionizes']              
            
            for regDict in regDicts:
                try:
#                    print regDict
                    regionInd = regDict['structure']['id']
#                    print regionInd
                    expression_energy = regDict['expression_energy']
                    voxel_energy_cv = regDict['voxel_energy_cv']
                    expression_density = regDict['expression_density']
                    gene_energy_mat[i,regionInd] = expression_energy
                    gene_density_mat[i,regionInd] = expression_density
                    gene_energy_cv_mat[i,regionInd] = voxel_energy_cv
                except Exception:
                    continue
        else:
            ise.valid = False
            ise.save()
    os.chdir(save_dir)
    np.savetxt("gene_energy_mat.csv", gene_energy_mat, delimiter=",")
    np.savetxt("gene_density_mat.csv", gene_density_mat, delimiter=",")
    np.savetxt("gene_energy_cv_mat.csv", gene_energy_cv_mat, delimiter=",")
    
    return gene_energy_mat, gene_density_mat, gene_energy_cv_mat, iseObs, regObs
                

#        print json_data
#            iseOb = InSituExpt.objects.get(imageseriesid = isid)
#    try:
#        regDicts = json_data['msg'][0]['structure_unionizes']
##                print str(len(regDicts)) + ' found regions'
#        regExprObs = []
#        for regDict in regDicts:
#            expression_energy = regDict['expression_energy']
#            expression_density = regDict['expression_density']
#            voxel_energy_cv = regDict['voxel_energy_cv']
#            regionInd = regDict['structure']['id']
#            
#            try:
#                regionOb = regionObDict[regionInd]
#            except KeyError:
#                continue
#            regExprOb = RegionExpr.objects.get_or_create(region = regionOb, expr_energy = expression_energy,
#                                                         expr_energy_cv = voxel_energy_cv,
#                                                         expr_density = expression_density)[0]
#            regExprObs.append(regExprOb)
#            #iseOb.regionexprs.add(regExprOb)        
#        iseOb.regionexprs = regExprObs                
##            print iseOb
##            iseOb.regionExprs.add = regExprObs
##            print regExprObs
#    except (IndexError):
#        'isid %d not found in allen db'
#        iseOb.valid = False
#    iseOb.save()                
##    cnt += 1
#print regDict['structure']['acronym']

def get_all_reg_expr_data():
    for i in range(1, 100):
        print i
        get_allen_reg_expr_ver_2()
##structureList
#structureList= structureList[:-1] + ']'
##structureList = structureList + ']'
#isid = 472
#fullLink = linkBase % (isid, structureList)
#link = quote(fullLink, ':=/&()?_')
#
#print realLink
#print link
#handle = urlopen(link)
#data = handle.read()
#json_data = json.loads(data)
#regDicts = json_data['msg'][0]['structure_unionizes']
#            
def delete_regions_reg_expr():
    with transaction.commit_on_success():
        [rexpr.delete() for rexpr in RegionExpr.objects.all()]
        [b.delete() for b in BrainRegion.objects.all()]
