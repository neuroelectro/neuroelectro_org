# -*- coding: utf-8 -*-
"""
Created on Wed Dec 21 15:53:40 2011

@author: Shreejoy
"""

# compare results of channel-neuron matrix with matrix from allen
# figure out recursive brain-subpart relationships brom allen_list

from xml.etree.ElementTree import XML
from urllib2 import Request, urlopen, URLError, HTTPError
import struct
import os
import django_startup
from matplotlib.pylab import *
#run django_startup
os.chdir('C:\Python27\Scripts\Biophys\pubdb\pubdir')
from pubapp.models import BrainRegion, InSituExpt, IonChannel, RegionExpr
os.chdir('C:\Python27\Scripts\Biophys')
    
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


esearch = 'http://www.brain-map.org/aba/api/gene/%s.xml'
bvaBase = 'http://mouse.brain-map.org/aba/api/expression/%s.bva'
unpackStr = '159326f'
regionObs = BrainRegion.objects.all()
numRegions = len(regionObs)

ionchannels = IonChannel.objects.all()
for ic in ionchannels:
    if ic.gene is not None:
        geneName = ic.gene
        link = esearch % (geneName)
        req = Request(link)
        try: handle = urlopen(req)
        except URLError, e:
            print geneName
            print URLError
            continue
            
        data = handle.read()
        xml = XML(data)
        xmlOut = xml.findall('.//imageseriesid')
        ids = [x.text for x in xmlOut]
        planesXML = xml.findall('.//plane')
        planes = [x.text for x in planesXML]
        print geneName
#        print ids
        for i in range(len(ids)):
            isid = ids[i]
            bvaLink = bvaBase % (isid)
            req = Request(bvaLink)
            try: handle = urlopen(req)
            except URLError, e:
                continue
            print isid
            plane = planes[i]
            ise = InSituExpt.objects.get_or_create(imageseriesid = isid, gene = geneName, plane = plane)[0]
            ise.ionchannel = ic
            binData = handle.read()
            exprVals =  struct.unpack(unpackStr, binData)
            exprVals = array(exprVals)
            ise.bva = exprVals
            
            exprObs = []
            for i in range(numRegions):
                regionOb = regionObs[i]
                meanExpr = computeAvgExpr(regionOb, exprVals)
                regionExprOb = RegionExpr.objects.create(region = regionOb, val = meanExpr)
                exprObs.append(regionExprOb)
            
            ise.regionexprs = exprObs
            ise.save()
