from bs4 import BeautifulSoup as bs
from article_text_mining.deprecated.find_neurons_in_text import findNeuronsInText
from neuroelectro import models as m

__author__ = 'stripathy'


def assocNeuronstoArticleMult2(artObs):
    #artObs = Article.objects.filter(datatable__ephysconceptmap__isnull = False).distinct()
    #artObs = Article.objects.filter(datatable__ephysconceptmap__isnull = False, neuronarticlemap__isnull = True).distinct()
    #artObs = Article.objects.filter(neuronarticlemap__isnull = True, articlefulltext__isnull = False).distinct()
    #artObs = artObs[0:10]
    #afts = ArticleFullText.objects.filter(article__data_table__ephys_concept_map__isnull = False)
    tot_count = artObs.count()
    #numRes = 23411881#res.count()
    print '%d num total articles' % tot_count
    blockSize = 100
    firstInd = 0
    lastInd = blockSize
    blockCnt = 0
    while firstInd < lastInd:
        print '%d of %d blocks ' % (blockCnt, tot_count/blockSize)
        for artOb in artObs[firstInd:lastInd].iterator():
            assocArticleNeuron(artOb)
        firstInd = lastInd + 1
        lastInd = min(lastInd+blockSize, tot_count)
        blockCnt += 1


def assocArticleNeuron(artOb):
    robot_user = m.get_robot_user()
    fullTextOb = artOb.articlefulltext_set.all()[0]
    fullTextHtml = fullTextOb.get_content()
    if fullTextHtml == 'test':
        return
    soup = bs(''.join(fullTextHtml))
    full_text = soup.get_text()
    neuronTuple = findNeuronsInText(full_text)
    usedNeurons = []
    for t in neuronTuple:
        neuronOb = t[0]
        numMentions = t[2]
        if neuronOb not in usedNeurons and numMentions > 2:
            #neuronSynOb = t[1]
            neuronArticleMapOb = m.NeuronArticleMap.objects.get_or_create(neuron = neuronOb,
                                                                  num_mentions = numMentions,
                                                                  article = artOb,
                                                                  added_by = robot_user)[0]
            usedNeurons.append(neuronOb)
        else:
            continue
    aftStatOb = m.ArticleFullTextStat.objects.get_or_create(article_full_text = fullTextOb)[0]
    aftStatOb.neuron_article_map_processed = True
    aftStatOb.save()