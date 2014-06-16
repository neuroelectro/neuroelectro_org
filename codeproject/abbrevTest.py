# -*- coding: utf-8 -*-
"""
Created on Wed Apr 18 13:52:23 2012

@author: Shreejoy
"""
from ExtractAbbrev import ExtractAbbrev
#from ExtractAbbrev import *
import nltk
import re
import os
import django_startup
import struct
import gc
import nltk
from bs4 import BeautifulSoup
from matplotlib.pylab import *
os.chdir('C:\Python27\Scripts\Biophys\Biophysiome')
from neuroelectro.models import Article, MeshTerm, Substance, Journal
from neuroelectro.models import Neuron, NeuronSyn
from neuroelectro.models import BrainRegion, InSituExpt, Protein, RegionExpr
from neuroelectro.models import DataTable, ArticleFullText
from neuroelectro.models import EphysProp, EphysPropSyn, NeuronEphysLink
os.chdir('C:\Python27\Scripts\Biophys')
from random import sample

from find_neurons_in_text import findNeuronsInText

#text = "The anatomical organization of receptor neuron input into the olfactory bulb (OB) allows odor information to be transformed into an odorant-specific spatial map of mitral/tufted (M/T) cell glomerular activity at the upper level of the OB. In other sensory systems, neuronal representations of stimuli can be reorganized or enhanced following learning. While the mammalian OB has been shown to undergo experience-dependent plasticity at the glomerular level, it is still unclear if similar representational change occurs within (M/T) cell glomerular odor representations following learning. To address this, odorant-evoked glomerular activity patterns were imaged in mice expressing a GFP-based calcium indicator (GCaMP2) in OB (M/T) cells. Glomerular odor responses were imaged before and after olfactory associative conditioning to aversive foot shock. Following conditioning, we found no overall reorganization of the glomerular representation. Training, however, did significantly alter the amplitudes of individual glomeruli within the representation in mice in which the odor was presented together with foot shock. Further, the specific pairing of foot shock with odor presentations lead to increased responses primarily in initially weakly activated glomeruli. Overall, these results suggest that associative conditioning can enhance the initial representation of odors within the OB by enhancing responses to the learned odor in some glomeruli."
##text = "Acetylcholine (ACh) plays a major role in the processing of sensory inputs. Cholinergic input to the mammalian olfactory bulb modulates odor discrimination and perceptual learning by mechanisms that have yet to be elucidated. We have used the mouse olfactory bulb to examine the role of nicotinic ACh receptors (nAChRs) in regulating the responses of mitral cells (MCs), the output neurons of the olfactory bulb, to olfactory nerve input. We show that ACh activates α3β4* nAChRs (* denotes the possible presence of other subunits) on MCs, leading to their excitation. Despite depolarizing MCs directly, the net effect of nAChR activation is to suppress olfactory nerve-evoked responses in these cells via activity-dependent feedback GABAergic mechanisms. Our results indicate that nAChRs gate incoming olfactory nerve input wherein weak input stimuli are filtered out, whereas strong stimuli are transmitted via the MCs. Based on our observations, we provide a mechanistic model for the sharpening of MC receptive fields by nAChRs, which could aid in odor discrimination and perceptual learning."
#sents = nltk.sent_tokenize(text)
#abrOb = ExtractAbbrev()
#for s in sents:
#    abr=abrOb.extractabbrpairs(s)
#

arts = Article.objects.filter(full_text_link__isnull = False)
arts = arts[0:10]
for a in arts:
    
    f = ArticleFullText.objects.get(article = a)
    
    html = f.full_text
    
    htmlSoup = BeautifulSoup(html)
    
    # extract out all citations - this fcks up the abbrev editor
    refTags = htmlSoup.find_all("a", {"class" : "xref-bibr"})
    for r in refTags:
        r.string = ""
        
    # write a regex to extract out ( )'s thaat have no word chars
    htmlText = htmlSoup.text
    htmlText = re.sub('\n', ' ', htmlText)
    htmlText = re.sub('\(\W+\)', '', htmlText)
    htmlText = re.sub('\s+', ' ', htmlText)
    sents = nltk.sent_tokenize(htmlText)
    abrOb = ExtractAbbrev()
    
    #abrOb.extractabbrpairs(sents[0])
    #abrOb.extractabbrpairs(sents[1])
    #abrOb.extractabbrpairs(sents[4])
    #abrOb.extractabbrpairs(sents[5])
    
    for s in sents:
    #    print s.encode("iso-8859-15", "replace")
        abrOb.extractabbrpairs(s)
    #    print abr
    print abrOb.abbrevdict

