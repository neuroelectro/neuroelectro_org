# -*- coding: utf-8 -*-
"""
Created on Thu Oct 04 15:03:04 2012

@author: Shreejoy
"""

import numpy
from neuroelectro.models import Article, MeshTerm, Substance, Journal
from neuroelectro.models import Neuron, NeuronSyn, Unit
from neuroelectro.models import BrainRegion, InSituExpt, Protein, RegionExpr
from neuroelectro.models import DataTable, ArticleFullText, EphysConceptMap
from neuroelectro.models import EphysProp, EphysPropSyn, NeuronEphysLink, NeuronArticleMap
from neuroelectro.models import NeuronConceptMap, NeuronArticleMap, NeuronEphysDataMap
from neuroelectro.models import ArticleSummary, NeuronSummary, EphysPropSummary, NeuronEphysSummary

for i,name in enumerate(nnames):
    formName = str(name).strip()
    n = Neuron.objects.get(name = formName)
    nsOb = NeuronSummary.objects.get(neuron = n)
    nsOb.cluster_xval = xinds[i]
    nsOb.cluster_yval = yinds[i]
    nsOb.save()