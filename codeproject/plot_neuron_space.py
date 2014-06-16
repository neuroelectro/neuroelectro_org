
import numpy as np
from neuroelectro.models import Article, MeshTerm, Substance, Journal
from neuroelectro.models import Neuron, NeuronSyn, Unit
from neuroelectro.models import BrainRegion, InSituExpt, Protein, RegionExpr
from neuroelectro.models import DataTable, ArticleFullText, EphysConceptMap
from neuroelectro.models import EphysProp, EphysPropSyn, NeuronEphysLink, NeuronArticleMap
from neuroelectro.models import NeuronConceptMap, NeuronArticleMap, NeuronEphysDataMap
from neuroelectro.models import ArticleSummary, NeuronSummary, EphysPropSummary, NeuronEphysSummary

from django.db.models import Count, Min

neuronCount = Neuron.objects.all().count()
ephysCount = EphysProp.objects.all().count()
neuronData = np.zeros( (neuronCount, ephysCount))
nInd = 0
for i,n in enumerate(Neuron.objects.all()):
    for j, e in enumerate(EphysProp.objects.all()):
        currNesObs = NeuronEphysSummary.objects.filter(ephys_prop = e, neuron = n)
        if currNesObs.count() > 0:
            currNesObs = currNesObs[0]
            neuronData[i,j] = currNesObs.value_mean
            #print currNesObs.value_mean