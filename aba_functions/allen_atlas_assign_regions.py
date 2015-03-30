# -*- coding: utf-8 -*-
"""
Created on Sat Jan 21 19:43:38 2012

@author: Shreejoy
"""

# figure out recursive brain-subpart relationships brom allen_list

import os
import django_startup
from matplotlib.pylab import *
#run django_startup
os.chdir('C:\Python27\Scripts\Biophys\pubdb\pubdir')
from pubapp.models import BrainRegion
os.chdir('C:\Python27\Scripts\Biophys')

def getChildrenRegions(currRegion, brain_regions):
    # find all other regions with currRegion as parent
    parentRegions = [str(brain_regions[i][2]) for i in range(numRegions)]
    childList = [currRegion]
    for i in range(len(parentRegions)):
        possParent = parentRegions[i]
        if currRegion == possParent:
            childRegion = str(brain_regions[i][1])
#            childList.append(childRegion)
#            print childRegion
            childList.extend(getChildrenRegions(childRegion, brain_regions))
    return childList

def getRegionInd(region, brain_regions):
    regionList = brain_regions[:,1]
    ind = (regionList == region).nonzero()
    regionInd = brain_regions[ind, 3]
    return regionInd

def getRegionVoxels(region, brain_regions, allen_labelled_voxels):
    childRegions = getChildrenRegions(region, brain_regions)
    regionInds = [getRegionInd(childRegion, brain_regions) for childRegion in childRegions]        
#    for i in regionInds:
    voxelList = []   
    for ind in regionInds:
#        print ind
        voxels = (allen_labelled_voxels == ind).nonzero()
        voxels = voxels[1]
#        print voxels
        voxelList.extend(voxels)
#        print voxelList
    return voxelList

numRegions = len(brain_regions)
for i in range(numRegions):
    regionName = str(brain_regions[i][0])
    abbrev = str(brain_regions[i][1])
    voxelInds = getRegionVoxels(abbrev, brain_regions, allen_labelled_voxels)
    b = BrainRegion.objects.get_or_create(name = regionName, abbrev = abbrev)[0]
    b.voxelinds = voxelInds
    b.save()


        