# -*- coding: utf-8 -*-
# Create your views here.
from django.template import Context, loader
from django.shortcuts import render,render_to_response, get_object_or_404
from django.db.models import Q
from neuroelectro.models import DataTable, DataSource, MailingListEntry
from neuroelectro.models import Neuron, Article, BrainRegion, NeuronSyn, MetaData, ArticleMetaDataMap
from neuroelectro.models import EphysProp, EphysConceptMap, EphysPropSyn, ContValue
from neuroelectro.models import ArticleSummary, NeuronEphysSummary, EphysPropSummary
from neuroelectro.models import NeuronConceptMap, NeuronEphysDataMap, NeuronSummary, ArticleFullTextStat
from neuroelectro.models import User, NeuronArticleMap, Institution, get_robot_user, get_anon_user
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.db.models import Count, Min
from django.contrib.auth.decorators import login_required
from django.contrib.auth.signals import user_logged_in
from bs4 import BeautifulSoup
import re, os
#import nltk
from html_table_decode import assocDataTableEphysVal, resolveHeader, isHeader, resolveDataFloat
from html_table_decode import assignDataValsToNeuronEphys
from compute_field_summaries import computeArticleSummary, computeNeuronEphysSummary
from html_process_tools import getMethodsTag
from db_add import add_single_article
from django.core.context_processors import csrf
from django.views.decorators.csrf import csrf_protect
from fuzzywuzzy import fuzz, process
from itertools import groupby
import json
from copy import deepcopy
import numpy as np
from scipy.stats.stats import pearsonr
from django import forms
from django.forms.widgets import SelectMultiple
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit,Layout,Fieldset,Submit,Button,Div,HTML
from crispy_forms.bootstrap import PrependedText,FormActions
# os.chdir('C:\Users\Shreejoy\Desktop\neuroelectro_org\Code')
# from ExtractAbbrev import ExtractAbbrev

def test(request):
    return render(request,'neuroelectro/test.html',{'request':request})

def scatter_test(request):
    return render(request,'neuroelectro/scatter_test.html',{'request':request})

# Overrides Django's render_to_response.  
# Obsolete now that 'render' exists. render_to_response(x,y,z) equivalent to render(z,x,y).  
def render_to_response2(template,dict,request):
    #dict.update({'request':request})
    return render_to_response(template,dict,context_instance=RequestContext(request))

def login(request):
    from django.contrib.auth.views import login as django_login
    user_logged_in.connect(login_hook)

    return django_login(request,template_name='neuroelectro/login.html')

def logout(request):
    from django.contrib.auth import logout as django_logout
    django_logout(request)
    return HttpResponseRedirect(request.META['HTTP_REFERER'])    

def login_hook(signal,**kwargs):
    pass
    #user = kwargs['user']
    #raise
    #user.save()
    #if 'Google' in user.backend:
    #    [new_user,created] = User.objects.get_or_create(email=user.email)
    #elif 'Twitter' in user.backend:
    #    [new_user,created] = User.objects.get_or_create(username=user.username)
    
def splash_page(request):
    myDict = {}
    myDict['form'] = MailingListForm()
    return render_to_response2('neuroelectro/splash_page.html',myDict,request)

class MailingListForm(forms.Form):
    email = forms.EmailField(
        label = "Email Address",
        required = True,
    )
    name = forms.CharField(
        label = "Name",
        max_length = 100,
        required = False,
    )
    comments = forms.CharField(
        widget = forms.Textarea(),
        label = 'Comments',
        max_length = 100,
        required = False,
    )
    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.helper.form_id = 'id-mailingListForm'
        self.helper.form_class = 'blueForms'
        self.helper.form_method = 'post'
        self.helper.form_action = '/mailing_list_form_post/'
        #self.helper.add_input(Submit('submit', 'Submit'))
        self.helper.layout = Layout(
            Fieldset(
                "Join our mailing list!",
                'email',
                'name',
                #'comments',
                ),
            FormActions(
                Submit('submit', 'Submit Information',align='middle'),
                )
            )
        super(MailingListForm, self).__init__(*args, **kwargs)

def mailing_list_form_post(request):
    if request.POST:
        print request 
        email = request.POST['email']
        if validateEmail(email):
            name = request.POST['name']
            #comments = request.POST['comments']
            legend = "Your email has been successfully added! "
            mailing_list_entry_ob = MailingListEntry.objects.get_or_create(email = email)[0]
            mailing_list_entry_ob.name = name
            #mailing_list_entry_ob.comments = comments
            mailing_list_entry_ob.save()
        else:
            legend = "Your email isn't valid, please enter it again"
    else:
        legend = "Please add your email (we promise won't spam you)"
    output_message = legend
    message = {}
    message['response'] = output_message
    return HttpResponse(json.dumps(message), mimetype='application/json')

def mailing_list_form(request):
    successBool = False
    if request.POST:
    	print request 
    	email = request.POST['email']
    	if validateEmail(email):
            name = request.POST['name']
            comments = request.POST['comments']
            legend = "Your email has been successfully added! "
            mailing_list_entry_ob = MailingListEntry.objects.get_or_create(email = email)[0]
            mailing_list_entry_ob.name = name
            mailing_list_entry_ob.comments = comments
            mailing_list_entry_ob.save()
            successBool = True
        else:
            legend = "Your email isn't valid, please enter it again"
    else:
    	legend = "Please add your email (we promise won't spam you)"
    	
    class MailingListForm(forms.Form):
		email = forms.EmailField(
			label = "Email Address",
			required = True,
		)
		name = forms.CharField(
			label = "Name",
			max_length = 100,
			required = False,
		)
		comments = forms.CharField(
			widget = forms.Textarea(),
		    label = 'Comments',
			max_length = 100,
			required = False,
		)
		def __init__(self, *args, **kwargs):
			self.helper = FormHelper()
			self.helper.form_id = 'id-mailingListForm'
			self.helper.form_class = 'blueForms'
			self.helper.form_method = 'post'
			self.helper.form_action = ''
			#self.helper.add_input(Submit('submit', 'Submit'))
			self.helper.layout = Layout(
                Fieldset(
                    "<p align='left'>%s</p>" % legend,
                    'email',
                    'name',
                    'comments',
                    ),
                FormActions(
                    Submit('submit', 'Submit Information',align='middle'),
                    )
                )
			super(MailingListForm, self).__init__(*args, **kwargs)
    returnDict = {}
    returnDict['form'] = MailingListForm
    returnDict['successBool'] = successBool
    print successBool
    return render_to_response2('neuroelectro/mailing_list_form.html', returnDict, request)

def validateEmail( email ):
    from django.core.validators import validate_email
    from django.core.exceptions import ValidationError
    try:
        validate_email( email )
        return True
    except ValidationError:
        return False

def neuron_index(request):
    neuron_list = Neuron.objects.all()
    # nedmsValid = NeuronEphysDataMap.objects.filter(neuron_concept_map__times_validated__gte = 1, ephys_concept_map__times_validated__gte = 1).distinct()
    # for n in neuron_list:
        # neuronNedms = nedmsValid.filter(neuron_concept_map__neuron = n).distinct()
        # numNedms = neuronNedms.count()
        # n.value_count = numNedms
        #articles = Article.objects.filter(neuronarticlemap__neuron = n).distinct()
        #articles = Article.objects.filter(datatable__neuronconceptmap__in = neuronNedms).distinct()
        #n.article_count = articles.count()
        # ncms = NeuronConceptMap.objects.filter(neuronephysdatamap__in = ephysNedms)
        # neurons = Neuron.objects.filter(neuronconceptmap__in = ncms).distinct()
        # numUniqueNeurons = neurons.count() 
        # e.neuron_count = numUniqueNeurons
        # neuronCount.append(numUniqueNeurons)
    return render_to_response2('neuroelectro/neuron_index.html', {'neuron_list': neuron_list},request)

#@login_required
def neuron_detail(request, neuron_id):
    n = get_object_or_404(Neuron, pk=neuron_id)
    print n
    #nedm_list = NeuronEphysDataMap.objects.filter(neuron_concept_map__neuron = n, val_norm__isnull = False).order_by('ephys_concept_map__ephys_prop__name')
    nedm_list = NeuronEphysDataMap.objects.filter(neuron_concept_map__neuron = n, val__isnull = False).order_by('ephys_concept_map__ephys_prop__name')
    ephys_nedm_list = []
    ephys_count = 0
    neuron_mean_ind = 2
    all_neurons_ind = 3
    neuron_mean_data_pt = 0
    neuron_mean_sd_line = 0
    main_ephys_prop_ids = [2, 3, 4, 5, 6, 7]
    for e in EphysProp.objects.all():
        nedm_list_by_ephys = nedm_list.filter(ephys_concept_map__ephys_prop = e)
        data_list_validated, data_list_unvalidated, neuronNameList, value_list_all = ephys_prop_to_list2(nedm_list_by_ephys)
        if len(data_list_validated) > 0:
            nes = NeuronEphysSummary.objects.get(neuron = n, ephys_prop = e)
            mean_val = nes.value_mean
            sd_val = nes.value_sd
            num_articles = nes.num_articles
            std_min_val = mean_val - sd_val
            std_max_val = mean_val + sd_val
            neuron_mean_data_pt = [ [neuron_mean_ind, mean_val, "%0.1f" % sd_val, str(num_articles), str(e.id)] ]
            neuron_mean_sd_line = [[neuron_mean_ind, std_min_val], [neuron_mean_ind, std_max_val]]
            # now calculate averages across all neurons
            eps = EphysPropSummary.objects.get(ephys_prop = e)
            mean_val_all = eps.value_mean_neurons
            sd_val_all = eps.value_sd_neurons
            num_neurons_all = eps.num_neurons
            all_neurons_data_pt = [[all_neurons_ind, mean_val_all, "%0.1f" % sd_val_all, str(num_neurons_all), str(e.id)]]
            std_min_val_all = mean_val_all - eps.value_sd_neurons
            std_max_val_all = mean_val_all + eps.value_sd_neurons
            all_neurons_sd_line = [[all_neurons_ind, std_min_val_all], [all_neurons_ind, std_max_val_all]]
            if e.id in main_ephys_prop_ids:
                main_ephys_prop = 1
            else:
                main_ephys_prop = 0
            ephys_nedm_list.append(['chart'+str(ephys_count), e, data_list_validated, data_list_unvalidated, neuron_mean_data_pt, neuron_mean_sd_line, all_neurons_data_pt, all_neurons_sd_line])
            ephys_count += 1
    for nedm in nedm_list:
        title = nedm.source.data_table.article.title
        nedm.title = title
    articles = Article.objects.filter(datatable__datasource__neuronephysdatamap__in = nedm_list).distinct()
    region_str = ''
    if n.regions:
        region_list = [str(region.allenid) for region in n.regions.all()]
        region_str = ','.join(region_list)
    curator_list = User.objects.filter(assigned_neurons__in = [n])
    returnDict = {'neuron': n, 'nedm_list': nedm_list, 'ephys_nedm_list': ephys_nedm_list, 'neuron_mean_data_pt':neuron_mean_data_pt,
        'neuron_mean_sd_line':neuron_mean_sd_line, 'article_list':articles, 'region_str':region_str, 'curator_list':curator_list}
    # print returnDict
    return render_to_response2('neuroelectro/neuron_detail.html',returnDict,request)
    
def ephys_prop_index(request):
    ephys_prop_list = EphysProp.objects.all()
    returnDict = {'ephys_prop_list': ephys_prop_list}
    return render_to_response2('neuroelectro/ephys_prop_index.html', returnDict, request)

def dajax_test(request):
	return render_to_response('neuroelectro/dajax_test.html', context_instance = RequestContext(request))

def ephys_prop_detail(request, ephys_prop_id):
    e = get_object_or_404(EphysProp, pk=ephys_prop_id)
    nedm_list = NeuronEphysDataMap.objects.filter(ephys_concept_map__ephys_prop = e, val_norm__isnull = False).order_by('neuron_concept_map__neuron__name')
    data_list_validated, data_list_unvalidated, neuronNameList, value_list_all = ephys_prop_to_list2(nedm_list)
    neuron_list = [Neuron.objects.get(name = nName) for nName in neuronNameList]
    #print data_list_validated
    #print neuron_list
    return render_to_response2('neuroelectro/ephys_prop_detail.html', {'ephys_prop': e, 'nedm_list':nedm_list, 
                                                                    'data_list_validated': data_list_validated,
                                                                    'data_list_unvalidated': data_list_unvalidated,
                                                                     'neuronNameList':neuronNameList,
                                                                     'neuron_list':neuron_list},
                                request)
                                
def ephys_prop_pair(request, ephys_prop_id1, ephys_prop_id2):
    e1 = get_object_or_404(EphysProp, pk=ephys_prop_id1)
    nedm_list = NeuronEphysDataMap.objects.filter(ephys_concept_map__ephys_prop = e1, val_norm__isnull = False).order_by('neuron_concept_map__neuron__name')
    data_list_validated, data_list_unvalidated, neuronNameList, value_list_all = ephys_prop_to_list2(nedm_list)
    neuron_list = [Neuron.objects.get(name = nName) for nName in neuronNameList]
    #print data_list_validated
    #print neuron_list
    return render_to_response2('neuroelectro/ephys_prop_detail.html', {'ephys_prop': e, 'nedm_list':nedm_list, 
                                                                      'data_list_validated': data_list_validated,
                                                                      'data_list_unvalidated': data_list_unvalidated,
                                                                      'neuronNameList':neuronNameList,
                                                                      'neuron_list':neuron_list},
                            request)

def ephys_prop_correlation(request):
    pass

def neuron_clustering(request):
    neuron_summary_list = NeuronSummary.objects.filter(cluster_xval__isnull = False).order_by('num_articles')
    neuron_list = Neuron.objects.filter(neuronsummary__in = neuron_summary_list).order_by('name')
    data_pts = []
    data_pts2 = []
    for i,nsOb in enumerate(neuron_summary_list):
        xVal = nsOb.cluster_xval
        yVal = nsOb.cluster_yval
        num_arts = nsOb.num_articles
        name = nsOb.neuron.name
        nId = nsOb.neuron.pk
        if num_arts < 1:
            num_arts = 1
        currDataPt = [xVal, yVal, str(np.sqrt(num_arts)), str(name), str(nId)]
        data_pts.append(currDataPt)
    returnDict = {'neuron_list': neuron_list, 'data_pts': data_pts, 'data_pts2': data_pts2}
    return render_to_response2('neuroelectro/neuron_clustering.html', returnDict, request) 

def neuron_ephys_prop_count(request):
    neuron_list = Neuron.objects.filter(neuronconceptmap__times_validated__gte = 1).distinct()
    ephys_list = EphysProp.objects.all()
    valid_pk_list = range(2,8)
    ephys_list = ephys_list.filter(pk__in = valid_pk_list)
    neuron_ephys_count_table = []

    for n in neuron_list:
        temp_ephys_count_list = [0]*ephys_list.count()
        for i,e in enumerate(ephys_list):
            nes_query = NeuronEphysSummary.objects.filter(neuron = n, ephys_prop = e)
            if nes_query.count() > 0:
                temp_ephys_count_list[i] = nes_query[0].num_articles
        neuron_ephys_count_table.append(temp_ephys_count_list)
        n.ephys_count_list = temp_ephys_count_list
        n.total_ephys_count = sum(temp_ephys_count_list)
    print neuron_ephys_count_table
    returnDict = {'neuron_list': neuron_list, 'ephys_list': ephys_list, 'neuron_ephys_count_table' : neuron_ephys_count_table}
    return render_to_response2('neuroelectro/neuron_ephys_prop_count.html', returnDict, request) 

# Deprecated.

def ephys_prop_to_list2(nedm_list):
    data_list_validated = []
    data_list_unvalidated = []
    cnt = 0
    neuronCnt = 0
    value_list_all = []
    oldNeuronName = []
    neuronNameList = oldNeuronName
    for nedm in nedm_list:
        val = nedm.val_norm
        if val is None:
            continue
        art = nedm.source.data_table.article
        neuronName = nedm.neuron_concept_map.neuron.name
        if neuronName != oldNeuronName:
            neuronCnt += 1
            oldNeuronName = neuronName
            neuronNameList.append(str(oldNeuronName))
        title = art.title.encode("iso-8859-15", "replace")
        author_list = art.author_list_str
        if not author_list:
            author_list = ''
#         if art.articlesummary_set.all().count() > 0:
#         	author_list = art.articlesummary_set.all()[0].author_list_str
#         	
#     	else:
#     		author_list = ''
    	#print author_list
    	author_list = author_list.encode("iso-8859-15", "replace")
        data_table_ind = nedm.source.data_table.id
        value_list = [neuronCnt, val, str(neuronName), title, author_list, str(data_table_ind)]
        value_list_all.append(val)
        #print nedm.times_validated
        if nedm.neuron_concept_map.times_validated != 0 and nedm.ephys_concept_map.times_validated:
            data_list_validated.append(value_list)
        else:
            data_list_unvalidated.append(value_list)
        # neuron_ephys_val_list.append([neuronCnt, val, str(nedm.neuron.name), title, str(data_table_ind)])    
        cnt += 1
    return data_list_validated, data_list_unvalidated, neuronNameList, value_list_all
    
def article_detail(request, article_id):
    article = get_object_or_404(Article, pk=article_id)
    metadata_list = article.metadata.all()
    print metadata_list
    nedm_list = []
    for datatable in article.datatable_set.all():
        nedm_list_temp = datatable.datasource_set.get().neuronephysdatamap_set.all().order_by('neuron_concept_map__neuron__name', 'ephys_concept_map__ephys_prop__name')
        nedm_list.extend(nedm_list_temp)
    print nedm_list
    returnDict = {'article': article, 'metadata_list':metadata_list, 'nedm_list':nedm_list}
    # full_text = article.articlefulltext_set.all()[0].get_content()
    return render_to_response2('neuroelectro/article_detail.html', returnDict, request)

def article_full_text_detail(request, article_id):
    article = get_object_or_404(Article, pk=article_id)
    article_full_text = article.get_full_text()
    returnDict = {'article_full_text': article_full_text.get_content()}
    # full_text = article.articlefulltext_set.all()[0].get_content()
    return render_to_response2('neuroelectro/article_full_text_detail.html', returnDict, request)

def article_metadata(request, article_id):
    article = get_object_or_404(Article, pk=article_id)
    if request.POST:
        print request.POST 
        user = request.user
        ordinal_list_names = ['Species', 'Strain', 'ElectrodeType', 'PrepType']
        cont_list_names = ['AnimalAge', 'AnimalWeight', 'RecTemp',]
        for o in ordinal_list_names:
            if o in request.POST:
                curr_mds = MetaData.objects.filter(name = o)
                curr_list = request.POST.getlist(o)
                amdms_old = list(ArticleMetaDataMap.objects.filter(article = article, metadata__name = o))
                print amdms_old
                for elem in curr_list:
                    metadata_ob = MetaData.objects.filter(pk = elem)[0]
                    amdmQuerySet = ArticleMetaDataMap.objects.filter(article = article, metadata = metadata_ob)
                    if amdmQuerySet.count() > 0:
                        amdm = amdmQuerySet[0]
                        # check if amdm ob already exists
                        if amdm in amdms_old:
                            amdms_old.remove(amdm)
                        amdm.metadata = metadata_ob
                        amdm.times_validated = amdm.times_validated + 1
                        amdm.save()
                    else:
                        amdm = ArticleMetaDataMap.objects.create(article = article, metadata = metadata_ob, added_by = user, times_validated = 1)
                for amdm in amdms_old:
                    amdm.delete()
            else:
                amdms = ArticleMetaDataMap.objects.filter(article = article, metadata__name = o)
                amdms.delete()
        for c in cont_list_names:
            if c in request.POST:
                entered_string = unicode(request.POST[c])
                if len(entered_string) > 0:
                    retDict = resolveDataFloat(entered_string)
                    if retDict:
                        min_range = None
                        max_range = None
                        stderr = None
                        if 'minRange' in retDict:
                            min_range = retDict['minRange']
                        if 'maxRange' in retDict:
                            max_range = retDict['maxRange']
                        if 'error' in retDict:
                            stderr = retDict['error']
                        cont_value_ob = ContValue.objects.get_or_create(mean = retDict['value'], min_range = min_range,
                                                                          max_range = max_range, stderr = stderr)[0]
                        metadata_ob = MetaData.objects.get_or_create(name=c, cont_value=cont_value_ob)[0]
                        # check if amdm ob already exists, if it does, just update pointer for amdm, but leave old md intact
                        amdmQuerySet = ArticleMetaDataMap.objects.filter(article = article, metadata__name = c)
                        if amdmQuerySet.count() > 0:
                            amdm = amdmQuerySet[0]
                            amdm.metadata = metadata_ob
                            amdm.times_validated = amdm.times_validated + 1
                            amdm.save()
                        else:
                            amdm = ArticleMetaDataMap.objects.create(article = article, metadata = metadata_ob, added_by = user, times_validated = 1)
                else:
                    amdms = ArticleMetaDataMap.objects.filter(article = article, metadata__name = c)
                    amdms.delete()
        # note that the article metadata has now been checked and validated by a human
        afts = ArticleFullTextStat.objects.get(article_full_text__article = article)
        afts.metadata_human_assigned = True
        print 'human assigned'
        afts.save()
    metadata_list = MetaData.objects.filter(articlemetadatamap__article = article).distinct()
    #print metadata_list
    #print metadata_list
    # if article.get_full_text_stat():
    # if article.get_full_text_stat().methods_tag_found:
    methods_html = getMethodsTag(article.get_full_text().get_content(), article)
    methods_html = str(methods_html)
    # else:
    #     methods_html = None
    returnDict = {'article': article, 'metadata_list':metadata_list, 'methods_html': methods_html}
    initialFormDict = {}
    for md in metadata_list:
        print md
        if md.value:
            if initialFormDict.has_key(md.name):
                initialFormDict[md.name].append(unicode(md.id))
            else:
                initialFormDict[md.name] = [unicode(md.id)]
        else:
            initialFormDict[md.name] = unicode(md.cont_value)
    print initialFormDict
    print '\n'
    # initialFormDict = {'Species':[u'3', u'5'], 'ElectrodeType':[u'14'],'Age': u'123', 'Temp': u'1246'}
    # print initialFormDict

    returnDict['form'] = ArticleMetadataForm(initial=initialFormDict)

        # species_list = request.POST['Species']
        # strain_list = request.POST['Strain']
        # electrode_type_list = request.POST['ElectrodeType']
    # full_text = article.articlefulltext_set.all()[0].get_content()
    return render_to_response2('neuroelectro/article_metadata.html', returnDict, request)


class ArticleMetadataForm(forms.Form):
    # SPECIES_CHOICES = assign_species_choices()
    # print SPECIES_CHOICES
    AnimalAge = forms.CharField(
        required = False,
        label = u'Age (days, e.g. 5-10; P46-P94)'
    )
    AnimalWeight = forms.CharField(
        required = False,
        label = u'Weight (grams, e.g. 150-200)'
    )
    RecTemp = forms.CharField(
        required = False,
        label = u'Temp (°C, e.g. 33-45°C)'

    )

    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.helper.form_id = 'id-metaDataForm'
        self.helper.form_class = 'blueForms'
        self.helper.form_method = 'post'
        self.helper.form_action = ''
        #self.helper.add_input(Submit('submit', 'Submit'))
        self.helper.layout = Layout(
            Fieldset(
                "Assign Metadata",
                'Species',
                'Strain',
                'ElectrodeType',
                'PrepType',
                'AnimalAge',
                'RecTemp',
                'AnimalWeight',
                ),
            FormActions(
                Submit('submit', 'Submit Information',align='middle'),
                )
            )
        super(ArticleMetadataForm, self).__init__(*args, **kwargs)
        self.fields['Species'] = forms.MultipleChoiceField(
            choices=[ (md.id, md.value) for md in MetaData.objects.filter(name = 'Species')], 
            required = False,
        )
        self.fields['Strain'] = forms.MultipleChoiceField(
            choices=[ (md.id, md.value) for md in MetaData.objects.filter(name = 'Strain')],
            required = False,
        )
        self.fields['ElectrodeType'] = forms.MultipleChoiceField(
            choices=[ (md.id, md.value) for md in MetaData.objects.filter(name = 'ElectrodeType')],
            required = False,
        )
        self.fields['PrepType'] = forms.MultipleChoiceField(
            choices=[ (md.pk, md.value) for md in MetaData.objects.filter(name = 'PrepType')],
            required = False,
        )

def data_table_detail(request, data_table_id):
    datatable = get_object_or_404(DataTable, pk=data_table_id)
    nedm_list = datatable.datasource_set.get().neuronephysdatamap_set.all().order_by('neuron_concept_map__neuron__name', 'ephys_concept_map__ephys_prop__name')
    #inferred_neurons = list(set([str(nel.neuron.name) for nel in nel_list]))
    context_instance=RequestContext(request)
    csrf_token = context_instance.get('csrf_token', '')
    if request.user.is_authenticated():
        print request.user.username
        validate_bool = True
        enriched_html_table = enrich_ephys_data_table(datatable, csrf_token, validate_bool)
        returnDict = {'datatable': datatable, 'nedm_list': nedm_list,
						'enriched_html_table':enriched_html_table}  
        return render_to_response2('neuroelectro/data_table_detail_validate.html', returnDict, request)
    #enriched_html_table = datatable.table_html
    enriched_html_table = enrich_ephys_data_table(datatable, csrf_token)
    returnDict = {'datatable': datatable, 'nedm_list': nedm_list,
                    'enriched_html_table':enriched_html_table}      
    #print str(csrf)
    return render_to_response2('neuroelectro/data_table_detail.html', returnDict, request)

def data_table_detail_validate(request, data_table_id):
    if request.method == 'POST':
        # print request.POST
        datatable = get_object_or_404(DataTable, pk=data_table_id)
        ecmObs = datatable.datasource_set.all()[0].ephysconceptmap_set.all()
        ncmObs = datatable.datasource_set.all()[0].neuronconceptmap_set.all()
        nedmObs = datatable.datasource_set.all()[0].neuronephysdatamap_set.all()
        neurons = Neuron.objects.filter(neuronconceptmap__in = ncmObs)
        for e in ecmObs:
            e.times_validated += 1
            e.save()
        for ncm in ncmObs:
            ncm.times_validated += 1
            ncm.save()
        for nedm in ncmObs:
            nedm.times_validated += 1
            nedm.save()
        computeNeuronEphysSummary(ncmObs, ecmObs, nedmObs)
        articleQuerySet = Article.objects.filter(datatable = datatable)
        # print articleQuerySet
        asOb = computeArticleSummary(articleQuerySet)
        # print asOb
        # computeNeuronEphysSummary(neuron)
        # for all concept mappings (neuron, ephys prop), validate
        urlStr = '/neuroelectro/data_table/%d/' % int(data_table_id)
        # return HttpResponseRedirect(urlStr)
    datatable = get_object_or_404(DataTable, pk=data_table_id)
    nedm_list = datatable.datasource_set.get().neuronephysdatamap_set.all().order_by('neuron_concept_map__neuron__name', 'ephys_concept_map__ephys_prop__name')
    #inferred_neurons = list(set([str(nel.neuron.name) for nel in nel_list]))
    context_instance=RequestContext(request)
    csrf_token = context_instance.get('csrf_token', '')
    #enriched_html_table = datatable.table_html
    validate_bool = True
    enriched_html_table = enrich_ephys_data_table(datatable, csrf_token, validate_bool)
    returnDict = {'datatable': datatable, 'nedm_list': nedm_list,
                    'enriched_html_table':enriched_html_table}      
    #print str(csrf)
    return render_to_response2('neuroelectro/data_table_detail_validate.html', returnDict, request)

def ephys_concept_map_detail(request, ephys_concept_map_id):
    ecm = get_object_or_404(EphysConceptMap, pk=ephys_concept_map_id)
    return render_to_response2('neuroelectro/ephys_concept_map_detail.html', {'ephys_concept_map': ecm}, request)
    
def contact_info(request):
    return render_to_response2('neuroelectro/contact_info.html', {}, request)
    
def data_table_validate_example(request):
    return render_to_response2('neuroelectro/data_table_validate_example.html', {}, request)

def faqs(request):
    return render_to_response2('neuroelectro/faqs.html', {}, request)
    
def api(request):
    return render_to_response2('neuroelectro/api.html', {}, request)
    
def contribute(request):
    return render_to_response2('neuroelectro/contribute.html', {}, request)

def suggest(request):
    myDict = {}
    if request.POST:
        success = True # Replace with some actual validation code, and then submission to the database...
        if success:
            legend = "Thank you for the submissions!"
        else:
            legend = "There was a problem with your URLs."
    legend = "Enter some links to full texts of articles..."
    prefix = "http://"
    placeholder = "Enter a URL here..."
    css_class = 'input-xxlarge'
    class URLListForm(forms.Form):
        url1 = forms.URLField(label = "URL 1",initial = '',required = False)
        url2 = forms.URLField(label = "URL 2",initial = '',required = False)
        url3 = forms.URLField(label = "URL 3",initial = '',required = False)
        url4 = forms.URLField(label = "URL 4",initial = '',required = False)
        url5 = forms.URLField(label = "URL 5",initial = '',required = False)

        def __init__(self, *args, **kwargs):
            self.helper = FormHelper()
            self.helper.form_id = 'id-urlListForm'
            self.helper.form_class = 'blueForms form-horizontal'
            self.helper.form_method = 'post'
            self.helper.form_action = ''
            self.helper.layout = Layout(
                Fieldset(
                    "<p align='middle'>%s</p>" % legend,
                    PrependedText('url1', prefix, placeholder=placeholder, css_class=css_class),
                    PrependedText('url2', prefix, placeholder=placeholder, css_class=css_class),
                    PrependedText('url3', prefix, placeholder=placeholder, css_class=css_class),
                    PrependedText('url4', prefix, placeholder=placeholder, css_class=css_class),
                    PrependedText('url5', prefix, placeholder=placeholder, css_class=css_class),
                    ),
                FormActions(
                    Submit('submit', 'Submit Suggestions',align='middle'),
                    )
                )
            return super(URLListForm, self).__init__(*args, **kwargs)
    
    myDict['form'] = URLListForm
    return render_to_response2('neuroelectro/suggest.html', myDict, request)

def upload(request):
    myDict = {'form':ExampleForm}
    return render_to_response2('neuroelectro/upload.html', myDict, request)

def fix(request):
    myDict = {'form':ExampleForm}
    return render_to_response2('neuroelectro/fix.html', myDict, request)

@csrf_protect
def ajax_test(request):
    context_instance=RequestContext(request)
    csrf_token = context_instance.get('csrf_token', '')
    print csrf_token
    returnDict = {'token' : csrf_token}
    return render_to_response2('neuroelectro/ajax_test.html', returnDict, request)

def neuron_article_suggest(request, neuron_id):
    n = get_object_or_404(Neuron, pk=neuron_id)
    context_instance=RequestContext(request)
    csrf_token = context_instance.get('csrf_token', '')
    print csrf_token
    returnDict = {'token' : csrf_token, 'neuron': n}
    return render_to_response2('neuroelectro/neuron_article_suggest.html', returnDict, request)

def neuron_article_suggest_post(request, neuron_id):
    if not request.POST:
        output_message = 'article not post!'
        message = {}
        message['response'] = output_message
        return HttpResponse(json.dumps(message), mimetype='application/json')
    n = get_object_or_404(Neuron, pk=neuron_id)
    if request.user.is_anonymous():
    	user = get_anon_user()
    else:
    	user = request.user
    pmid = request.POST['pmid']
    # is article in db?
    articleQuery = Article.objects.filter(pmid = pmid)
    if len(articleQuery) == 0:
    	article = add_single_article(pmid)
    	print 'new article'
    	#a.suggester.add(user)
    	# assign suggester here
    else:
    	article = articleQuery[0]
    	print 'old article'
    	#a.suggester.add(user)
    #print article
    nam = NeuronArticleMap.objects.get_or_create(neuron=n, article = article)[0]
    nam.added_by = user
    nam.save()
    print nam.added_by.username
    output_message = 'article suggested!'
    message = {}
    message['response'] = output_message
    return HttpResponse(json.dumps(message), mimetype='application/json')
    
def neuron_article_curate_list(request, neuron_id):
    n = get_object_or_404(Neuron, pk=neuron_id)
    min_mentions_nam_1 = 20
    min_mentions_nam_2 = 3
    max_un_articles = 50
    articles_ex = Article.objects.filter(datatable__datasource__neuronconceptmap__neuron = n, datatable__datasource__neuronephysdatamap__isnull = False).distinct()
    for art in articles_ex:
        dts = DataTable.objects.filter(article = art, datasource__ephysconceptmap__isnull = False).distinct()
    	art.datatables = dts
    robot_user = get_robot_user()
    # articles_robot = Article.objects.filter(Q(neuronarticlemap__neuron = n, 
    # 	neuronarticlemap__num_mentions__gte = min_mentions_nam, 
    # 	datatable__datasource__neuronephysdatamap__isnull = True,
    #     datatable__datasource__ephysconceptmap__isnull = False)).distinct()
    articles_robot = Article.objects.filter(Q(neuronarticlemap__neuron = n, 
        neuronarticlemap__num_mentions__gte = min_mentions_nam_1)).distinct()
        # metadata__name = 'ElectrodeType')
    if articles_robot.count() < 5:
        articles_robot = Article.objects.filter(Q(neuronarticlemap__neuron = n, 
            neuronarticlemap__num_mentions__gte = min_mentions_nam_2)).distinct()
            # metadata__name = 'ElectrodeType')
    articles_robot.exclude(datatable__datasource__neuronconceptmap__times_validated__gte = 1)
    articles_human = Article.objects.filter(Q(neuronarticlemap__neuron = n,  
    	datatable__datasource__neuronephysdatamap__isnull = True)).exclude(neuronarticlemap__added_by=robot_user).distinct()
    # articles_un = set(articles_robot).difference(set(articles_human) )
    articles_un = articles_robot.exclude(pk__in = articles_ex)
    print articles_robot
    # articles_un = articles_human.exclude(pk__in = articles_robot)
    # if articles_un.count() > max_un_articles:
    # 	articles_un = articles_un[0:max_un_articles]
    # annotate(num_mentions = Count('neuronarticlemap__neuron = n, neuronarticlemap__num_mentions'))
    for art in articles_un:
        # dts = DataTable.objects.filter(article = art, datasource__ephysconceptmap__isnull = False).distinct()
        dts = DataTable.objects.filter(article = art).distinct()
        dts = dts.annotate(num_unique_ephys = Count('datasource__ephysconceptmap__ephys_prop__id'))
        dts = dts.filter(num_unique_ephys__gte = 2)
        #dts = DataTable.objects.filter(article = art).distinct()
    	art.datatables = dts
    	nam = NeuronArticleMap.objects.filter(article = art, neuron = n)[0]
        art.neuron_mentions = nam.num_mentions
        if art.neuron_mentions is None:
            art.neuron_mentions = 0
    	#art.how_added = '%s %s' % (nam.added_by.first_name, nam.added_by.last_name)
    	if nam.added_by:
    		art.how_added = '%s %s' % (nam.added_by.first_name, nam.added_by.last_name)
    	else:
    		art.how_added = 'Anon'
    #articles_un = articles_un.order_by('-neuron_mentions')
    # print articles_un.count()
    returnDict = {'articles_ex':articles_ex, 'articles_un':articles_un, 'neuron': n}
    return render_to_response2('neuroelectro/neuron_article_curate_list.html', returnDict, request)
    
def neuron_curator_ask(request, neuron_id):
    n = get_object_or_404(Neuron, pk=neuron_id)
    returnDict = {'neuron': n}
    return render_to_response2('neuroelectro/neuron_curator_ask.html', returnDict, request)

@login_required
def neuron_become_curator(request, neuron_id):
    n = get_object_or_404(Neuron, pk=neuron_id)
    user = request.user
    user_inst_default = ''
    if user.institution:
    	user_inst_default = user.institution.name
    if request.POST:
    	print request 
    	lab_head = request.POST['lab_head']
    	lab_website_url = request.POST['lab_website_url']
    	email_address = request.POST['email_address']
        institution= request.POST['institution']
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']

        # check that entered email address is actually valid
        if validateEmail(email_address): 
            success = True
        if success:
            legend = "Your information has been successfully added!"
            user = request.user
            user.lab_head = lab_head
            user.lab_website_url = lab_website_url
            user.email = email_address
            user.first_name = first_name
            user.last_name = last_name
            user.assigned_neurons.add(n)
            i = Institution.objects.get_or_create(name = institution)[0]
            user.institution = i
            user.save()
        else:
            legend = "There was a problem."
    else:
    	legend = 'Please add some additional identifying information'
    class NeuronCurateForm(forms.Form):
        first_name = forms.CharField(
        	label = "First Name",
        	max_length = 200,
        	required = True,
        	initial = user.first_name
        )
        last_name = forms.CharField(
        	label = "Last Name",
        	max_length = 200,
        	required = True,
        	initial = user.last_name
        )
        email_address = forms.EmailField(
            label = "Email",
            max_length = 200,
            required = True,
            initial = user.email
        )
        institution = forms.CharField(
        	label = "Institute (e.g. Carnegie Mellon University)",
        	max_length = 200,
        	required = False,
        	initial = user_inst_default
        )

        lab_head = forms.CharField(
        	label = "Lab head or adviser (e.g. Nathan Urban)",
        	max_length = 80,
        	required = False,
        	initial = user.lab_head
        )

        lab_website_url = forms.CharField(
        	label = "Lab website URL (e.g. http://www.andrew.cmu.edu/user/nurban/Lab_pages/)",
        	required = False,
        	initial = user.lab_website_url
        )

        notes = forms.CharField(
        	label = "Additional notes or feedback",
        	required = False,
        )
        def __init__(self, *args, **kwargs):
        	self.helper = FormHelper()
        	self.helper.form_id = 'id-neuronCurateForm'
        	self.helper.form_class = 'blueForms'
        	self.helper.form_method = 'post'
        	self.helper.form_action = ''
        	#self.helper.add_input(Submit('submit', 'Submit'))
        	self.helper.layout = Layout(
                Fieldset(
                    "<p align='left'>%s</p>" % legend,
                    'first_name',
                    'last_name',
                    'email_address',
                    'institution',
                    'lab_head',
                    'lab_website_url',
                    'notes',
                    ),
                FormActions(
                    Submit('submit', 'Submit Information',align='middle'),
                    )
                )
        	super(NeuronCurateForm, self).__init__(*args, **kwargs)

    returnDict = {'neuron': n}
    returnDict['form'] = NeuronCurateForm
    return render_to_response2('neuroelectro/neuron_become_curator.html', returnDict, request)
    
def fancybox_test(request):
    return render_to_response2('neuroelectro/fancybox_test.html', {}, request)
    
def nlex_neuron_id_list(request):
    neurons = Neuron.objects.filter(nlex_id__isnull = False)
    neurons = neurons.filter(neuronsummary__num_articles__gte = 1)
    outStr = ''
    for n in neurons:
        outStr += '%s,%s,%s' % (n.nlex_id, n.id, n.name)
        outStr += '<br>'
    print outStr
    return render_to_response2('neuroelectro/nlex_neuron_id_list.html', {'display_str': outStr}, request)
    
def ephys_prop_ontology(request):
    #return render_to_response2('neuroelectro/ephys_prop_ontology.html', {}, request)
    return render(request,'neuroelectro/ephys_prop_ontology.html', {})
    
def data_table_to_validate_list(request):
    dts = DataTable.objects.all()
    # dts = DataTable.objects.exclude(needs_expert = True)
    # dts = dts.filter(datasource__ephysconceptmap__isnull = False, datasource__neuronconceptmap__isnull = False)
    dts = dts.filter(datasource__ephysconceptmap__isnull = False)
    dts = dts.annotate(min_validated = Min('datasource__ephysconceptmap__times_validated'))
    dts = dts.exclude(min_validated__gt = 0)
    dts = dts.distinct()
    dts = dts.annotate(num_ecms=Count('datasource__ephysconceptmap__ephys_prop', distinct = True))
    dts = dts.order_by('-num_ecms')
    dts = dts.exclude(num_ecms__lte = 2)
    for dt in dts:
        dt_ncm_set = dt.article.neuronarticlemap_set.all().order_by('-num_mentions')
        if dt_ncm_set.count() > 0:
            dt.top_neuron = dt_ncm_set[0].neuron
            dt.top_neuron_total_num = NeuronConceptMap.objects.filter(neuron = dt.top_neuron, times_validated__gte = 1).count()
        else:
            dt.top_neuron = None
            dt.top_neuron_total_num = None
        # dt.num_ecms = EphysProp.objects.filter(ephysconceptmap__source__data_table = dt).distinct().count()
    return render_to_response2('neuroelectro/data_table_to_validate_list.html', {'data_table_list': dts}, request)

def data_table_no_neuron_list(request):
    dts = DataTable.objects.filter(datasource__ephysconceptmap__isnull = False, datasource__neuronconceptmap__isnull = True).distinct()
    dts = dts.annotate(min_validated = Min('datasource__ephysconceptmap__times_validated'))
    dts = dts.exclude(min_validated__gt = 0)
    dts = dts.distinct()
    dts = dts.annotate(num_ecms=Count('datasource__ephysconceptmap__ephys_prop', distinct = True))
    dts = dts.filter(num_ecms__gte = 4)
    dts = dts.order_by('-num_ecms')
    return render_to_response2('neuroelectro/data_table_no_neuron_list.html', {'data_table_list': dts}, request)

def data_table_expert_list(request):
    dts = DataTable.objects.filter(needs_expert = True).distinct()
    dts = dts.annotate(num_ecms=Count('datasource__ephysconceptmap__ephys_prop', distinct = True))
    dts = dts.order_by('-num_ecms')
    return render_to_response2('neuroelectro/data_table_expert_list.html', {'data_table_list': dts}, request)
	
def article_list(request):
    articles = Article.objects.filter(articlesummary__isnull = False)
    returnDict = {'article_list':articles}
    return render_to_response2('neuroelectro/article_list.html', returnDict, request)

def article_metadata_list(request):
    articles = Article.objects.filter(datatable__datasource__neuronconceptmap__times_validated__gte = 1).distinct()
    nom_vars = ['Species', 'Strain', 'ElectrodeType', 'PrepType']
    cont_vars  = ['RecTemp', 'AnimalAge', 'AnimalWeight']
    metadata_table = []
    for a in articles:
        amdms = ArticleMetaDataMap.objects.filter(article = a)
        curr_metadata_list = [None]*7
        for i,v in enumerate(nom_vars):
            valid_vars = amdms.filter(metadata__name = v)
            temp_metadata_list = [vv.metadata.value for vv in valid_vars]
            curr_metadata_list[i] = u', '.join(temp_metadata_list)
        for i,v in enumerate(cont_vars):
            valid_vars = amdms.filter(metadata__name = v)
            curr_str = ''
            for vv in valid_vars:
                cont_value_ob = vv.metadata.cont_value
                curr_str += unicode(cont_value_ob)
            curr_metadata_list[i+4] = curr_str
        # print curr_metadata_list
        a.metadata_list = curr_metadata_list
        if a.get_full_text_stat():
            a.metadata_human_assigned = a.get_full_text_stat().metadata_human_assigned
        else:
            a.metadata_human_assigned = False
        neuron_list = Neuron.objects.filter(neuronconceptmap__source__data_table__article = a, neuronconceptmap__times_validated__gte = 1).distinct()
        neuron_list = [n.name for n in neuron_list]
        a.neuron_list = ', '.join(neuron_list)
    # print metadata_table
    returnDict = {'article_list':articles, 'metadata_table' : metadata_table}
    return render_to_response2('neuroelectro/article_metadata_list.html', returnDict, request)
	

def neuron_add(request):
    region_list = BrainRegion.objects.all()
    returnDict = {'region_list':region_list}
    if request.POST:
        print request.POST
        if 'neuron_name' in request.POST and request.POST['neuron_name'] and 'region_id' in request.POST:
            neuron_name = request.POST['neuron_name']
            region_id = int(request.POST['region_id'])
            # article_id = int(request.POST['article_id'])
            
            # artOb = Article.objects.get(pk = article_id)
            neuronOb = Neuron.objects.get_or_create(name = neuron_name,
                                                    added_by = 'human',
                                                    )[0]
            if region_id is not 0:
                regionOb = BrainRegion.objects.get(pk = region_id)
                neuronOb.regions.add(regionOb)
            # neuronOb.defining_articles.add(artOb)
            neuronSynOb = NeuronSyn.objects.get_or_create(term = neuron_name)[0]
            neuronOb.synonyms.add(neuronSynOb)
            neuronOb.save()
            urlStr = '/neuroelectro/neuron/%d/' % int(neuronOb.pk)
            print urlStr
            return HttpResponseRedirect(urlStr)
        else:
            return HttpResponse('null')
    if 'HTTP_REFERER' in request.META:
        if request.META['HTTP_REFERER'] is not None:
            citing_link = request.META['HTTP_REFERER']
            temp = re.search('/\d+/', citing_link)
            if temp:
                temp = temp.group()
                dt_pk = int(re.sub('/', '', temp))
                article_query = Article.objects.filter(datatable__pk = dt_pk)
                if article_query.count() > 0:
                    citing_article = article_query[0]
                    returnDict['citing_article'] = citing_article

        #if 'data_table_id' in request.POST and 'box_id' in request.POST and 'dropdown' in request.POST
        
    return render_to_response2('neuroelectro/neuron_add.html', returnDict, request) 

def data_table_validate_all(request, data_table_id):
    if request.method == 'POST':
        # print request.POST
        datatable = get_object_or_404(DataTable, pk=data_table_id)
        ecmObs = datatable.ephysconceptmap_set.all()
        ncmObs = datatable.neuronconceptmap_set.all()
        nedmObs = datatable.neuronephysdatamap_set.all()
        for e in ecmObs:
            e.times_validated += 1
            e.save()
        for n in ncmObs:
            n.times_validated += 1
            n.save()
        for nedm in ncmObs:
            nedm.times_validated += 1
            nedm.save()
        article = datatable.article
        print article
        asOb = computeArticleSummary(article)
        print asOb
        # for all concept mappings (neuron, ephys prop), validate
        urlStr = '/neuroelectro/data_table/%d/' % int(data_table_id)
        return HttpResponseRedirect(urlStr)
        
def data_table_annotate(request, data_table_id):
    if request.method == 'POST' and request.POST['expert']:
        print request.POST
        datatable = get_object_or_404(DataTable, pk=data_table_id)
        if request.POST['expert'] == 'needs_expert':
            datatable.needs_expert = True
            datatable.save()
        urlStr = '/neuroelectro/data_table/%d/' % int(data_table_id)
        return HttpResponseRedirect(urlStr)

def neuron_concept_map_modify(request):
    print request.POST
    user = request.user
    if request.user.is_anonymous():
    	user = get_anon_user()
    if 'data_table_id' in request.POST and 'box_id' in request.POST and 'neuron_dropdown' in request.POST and 'neuron_note' in request.POST: 
        dt_pk = int(request.POST['data_table_id'])
        dtOb = DataTable.objects.get(pk = dt_pk)
        dsOb = DataSource.objects.get(data_table = dtOb)
        urlStr = "/neuroelectro/data_table/%d" % dt_pk
        box_id = request.POST['box_id']
        neuron_note = request.POST['neuron_note']
        print neuron_note
        selected_neuron_name = request.POST['neuron_dropdown']
        if selected_neuron_name == "None selected":
            ncm_pk = int(request.POST['ncm_id'])
            ncmOb = NeuronConceptMap.objects.get(pk= ncm_pk)
            ncmOb.delete()
            return HttpResponseRedirect(urlStr)
        neuron_ob = Neuron.objects.get(name = selected_neuron_name)
        # modifying an already existing ncm
        if 'ncm_id' in request.POST: 
            ncm_pk = int(request.POST['ncm_id'])
            ncmOb = NeuronConceptMap.objects.get(pk= ncm_pk)
            # only modify ecm if not the same as original
            if ncmOb.neuron != neuron_ob:
                ncmOb.neuron = neuron_ob
                ncmOb.added_by = user
            elif len(neuron_note) > 0:
                ncmOb.note = neuron_note
            ncmOb.save()

        # else creating a new ecm object
        else:
        # get text corresponding to box_id for ref_text
            table_soup = BeautifulSoup(dtOb.table_html)
            box_tag = table_soup.find('td', id = box_id)
            if box_tag is None:
                box_tag = table_soup.find('th', id = box_id)
            ref_text = box_tag.get_text()
            # normHeader = resolveHeader(ref_text)
            # ephysSyns = EphysPropSyn.objects.filter(ephys_prop = ephys_prop_ob)
            # ephysSynList = [e.term.lower() for e in ephysSyns]
            # processOut = process.extractOne(normHeader, ephysSynList)
            # if processOut is not None:
                # bestMatch, matchVal = processOut
            # ephysSynOb = EphysPropSyn.objects.get(term = bestMatch)
            ncmOb = NeuronConceptMap.objects.get_or_create(ref_text = ref_text,
                                                          neuron = neuron_ob,
                                                          # ephys_prop_syn = ephysSynOb,
                                                          source = dsOb,
                                                          dt_id = box_id,
                                                          #match_quality = matchVal,
                                                          added_by = user)[0]
            if len(neuron_note) > 0:
                ncmOb.note = neuron_note
                ncmOb.save()
        # since ncm changed, run data val mapping function on this data table
        assignDataValsToNeuronEphys(dtOb)                                                
        # if correct_value == u'y':
            # ecm.yes_votes += 1
        # else:
            # ecm.no_votes += 1
        # ecm.save()
        #return render_to_response2(HTTP_REFERER)
        
        return HttpResponseRedirect(urlStr)
        #return render_to_response2('neuroelectro/ephys_concept_map_detail.html', {'ephys_concept_map': ecmOb})
    else:
        message = 'null'
        return HttpResponse(message)

def ephys_concept_map_modify(request):
    #ecm = get_object_or_404(EphysConceptMap, pk=ephys_concept_map_id)
    #print request.POST
    user = request.user
    if request.user.is_anonymous():
    	user = get_anon_user()
    # check that post request comes back in correct form
    if 'data_table_id' in request.POST and 'box_id' in request.POST and 'ephys_dropdown' in request.POST and 'ephys_note' in request.POST: 
        dt_pk = int(request.POST['data_table_id'])
        dtOb = DataTable.objects.get(pk = dt_pk)
        dsOb = DataSource.objects.get(data_table = dtOb)
        urlStr = "/neuroelectro/data_table/%d" % dt_pk
        box_id = request.POST['box_id']
        ephys_note = request.POST['ephys_note']
        selected_ephys_prop_name = request.POST['ephys_dropdown']
        if selected_ephys_prop_name == "None selected":
            ecm_pk = int(request.POST['ecm_id'])
            ecmOb = EphysConceptMap.objects.get(pk= ecm_pk)
            ecmOb.delete()
            return HttpResponseRedirect(urlStr)
        ephys_prop_ob = EphysProp.objects.get(name = selected_ephys_prop_name)
        # modifying an already existing ecm
        if 'ecm_id' in request.POST: 
            ecm_pk = int(request.POST['ecm_id'])
            ecmOb = EphysConceptMap.objects.get(pk= ecm_pk)
            # only modify ecm if not the same as original
            if ecmOb.ephys_prop != ephys_prop_ob:
                ecmOb.ephys_prop = ephys_prop_ob
                ecmOb.added_by = user
            elif len(ephys_note) > 0:
                ecmOb.note = ephys_note
            ecmOb.save()
        # else creating a new ecm object
        else:
        # get text corresponding to box_id for ref_text
            table_soup = BeautifulSoup(dtOb.table_html)
            box_tag = table_soup.find('td', id = box_id)
            if box_tag is None:
                box_tag = table_soup.find('th', id = box_id)
            ref_text = box_tag.get_text()
            #normHeader = resolveHeader(ref_text)
#             ephysSyns = EphysPropSyn.objects.filter(ephys_prop = ephys_prop_ob)
#             ephysSynList = [e.term.lower() for e in ephysSyns]
#             processOut = process.extractOne(normHeader, ephysSynList)
#             if processOut is not None:
#                 bestMatch, matchVal = processOut
#             else:
#                 bestMatch = ephysSynList[0]
#                 matchVal = 0
#             ephysSynOb = EphysPropSyn.objects.get(term = bestMatch)
            ecmOb = EphysConceptMap.objects.get_or_create(ref_text = ref_text,
                                                          ephys_prop = ephys_prop_ob,
                                                          #ephys_prop_syn = ephysSynOb,
                                                          source = dsOb,
                                                          dt_id = box_id,
                                                          #match_quality = matchVal,
                                                          added_by = user)[0]
            if len(ephys_note) > 0:
                ecmOb.note = ephys_note
                ecmOb.save()
        # since ecm changed, run data val mapping function on this data table
        assignDataValsToNeuronEphys(dtOb, user)
        # if correct_value == u'y':
            # ecm.yes_votes += 1
        # else:
            # ecm.no_votes += 1
        # ecm.save()
        #return render_to_response2(HTTP_REFERER)
        
        return HttpResponseRedirect(urlStr)
        #return render_to_response2('neuroelectro/ephys_concept_map_detail.html', {'ephys_concept_map': ecmOb})
    else:
        message = 'null'
        return HttpResponse(message)
    # if value == "yes":
        # ecm.yes_votes += 1
    # else:
        # ecm.no_votes += 1
    #return HttpResponseRedirect(reverse('neuroelectro.views.ephys_concept_map', args=(ecm.id,)))
        
def display_meta(request):
    values = request.META.items()
    values.sort()
    html = []
    #return HttpResponse("Welcome to the page at %s" % request.is_secure())
    for k, v in values:
        html.append('<tr><td>%s</td><td>%s</td></tr>' % (k, v))
    return HttpResponse('<table>%s</table>' % '\n'.join(html))  

def neuron_search_form(request):
    return render_to_response2('neuroelectro/neuron_search_form.html')    
   
def navbar(request):
    return render_to_response2('neuroelectro/navbar.html')    

def neuron_search(request):
    if 'q' in request.GET and request.GET['q']:
        q = request.GET['q']
        neurons = Neuron.objects.filter(name__icontains=q)
        return render_to_response2('neuroelectro/neuron_search_results.html',
            {'neurons': neurons, 'query': q})
    else:
        return HttpResponse('Please submit a search term.')
    # try:
        
    # nel_list = datatable.neuronephyslink_set.all()
    # inferred_neurons = list(set([str(nel.neuron.name) for nel in nel_list]))
    # enriched_html_table = enrich_ephys_data_table(datatable)
    # returnDict = {'datatable': datatable, 'inferred_neurons': inferred_neurons, 'nel_list': nel_list,
                    # 'enriched_html_table':enriched_html_table}
    # return render_to_response2('neuroelectro/data_table_detail.html', returnDict, request)

def addFormBoxIds(inputSoup):
    print inputSoup
    formTags = inputSoup.find_all("form")
    print formTags
    for f in formTags:
        parentTag = f.parent()
        parentId = parentTag['id']
        newTag = BeautifulSoup('''<input type="hidden" name="box_id" value=%s />''' % (parentId))
        print newTag

# def sortAnmObs(anmObs)
    # newList = anmObs.order_by('-num_mentions')
    # return newList
def enrich_ephys_data_table(dataTableOb, csrf_token, validate_bool = False):
    soup = BeautifulSoup(dataTableOb.table_html)#.decode('utf-8')
    ecmObs = dataTableOb.datasource_set.get().ephysconceptmap_set.all()
    ncmObs = dataTableOb.datasource_set.get().neuronconceptmap_set.all()
    anmObs = dataTableOb.article.neuronarticlemap_set.all().order_by('neuron__name')
    nedmObs = dataTableOb.datasource_set.get().neuronephysdatamap_set.all()
    # if len(ecmObs) == 0:
        # assocDataTableEphysVal(dataTableOb)
        # ecmObs = dataTableOb.ephysconceptmap_set.all()
    # else:
        # ecmObs.delete()
        # assocDataTableEphysVal(dataTableOb)
        # ecmObs = dataTableOb.ephysconceptmap_set.all()
    # if len(ncmObs) == 0:
        # assocDataTableEphysVal(dataTableOb)
        # ecmObs = dataTableOb.ephysconceptmap_set.all()
        
    matchingDTIds = [ecm.dt_id for ecm in ecmObs]
    matchingNeuronDTIds = [ncm.dt_id for ncm in ncmObs]
    matchingDataValIds = [nedm.dt_id for nedm in nedmObs]     
    allTableTags = soup.find_all('td') + soup.find_all('th')
    for td_tag in allTableTags:
        tdText = td_tag.get_text().strip()
        # check if text is a header or data value
        # if isHeader(tdText) == False:
            # continue
        parent_tag = td_tag.parent
        if 'id' in td_tag.attrs.keys():
            tag_id = str(td_tag['id'])
        else: 
            tag_id = '-1'
        #print str(parent_tag_id)
        if len(tdText) > 0:
            #print tdText
            currMatchText = tdText
            if tag_id is not '-1' and tag_id in matchingDTIds:
                matchIndex = matchingDTIds.index(tag_id)
                ecmMatch = ecmObs[matchIndex]
                td_tag['style'] = "background-color:red;"
                # add html for correct radio buttons, drop down menu, submit button
                dropdownTag = ephys_neuron_dropdown(csrf_token, dataTableOb, tag_id, ecmMatch, None, None, validate_bool)
                td_tag.append(dropdownTag)
            elif tag_id is not '-1' and tag_id in matchingNeuronDTIds:
                matchIndex = matchingNeuronDTIds.index(tag_id)
                ncmMatch = ncmObs[matchIndex]
                td_tag['style'] = "background-color:pink;"         
                dropdownTag = ephys_neuron_dropdown(csrf_token, dataTableOb, tag_id, None,ncmMatch, anmObs, validate_bool) 
                td_tag.append(dropdownTag)     
            elif tag_id is not '-1' and tag_id in matchingDataValIds:
                matchIndex = matchingDataValIds.index(tag_id)
                ncmMatch = nedmObs[matchIndex]
                td_tag['style'] = "background-color:yellow;"                           
                #print td_tag
            elif isHeader(tdText) == False:
                continue
            else:
                if validate_bool == True:
                    dropdownTag = ephys_neuron_dropdown(csrf_token, dataTableOb, tag_id, None, None, anmObs, validate_bool)
                
                    td_tag.append(dropdownTag)
                a = 1
                #print td_tag  
            # add html for drop down menu, submit button
    # .decode('raw-unicode-escape').encode('utf-8')    
    #print soup
    tableStr = str(soup)
    #print tableStr
    #print tableStr
    enriched_html_table = tableStr
    #enriched_html_table = re.sub(r"\'", '', tableStr)

    return enriched_html_table   

def change_add_tag(baseTagAddStr, ecmOb = None, ncmOb = None):
    tagSoup = BeautifulSoup(baseTagAddStr)
    #print tagSoup
    if ecmOb is not None:
        ephysDropTag = tagSoup.find("form", {"name": "ephys_form"})
        ecmTag = BeautifulSoup('''<input type="hidden" name="ecm_id" value=%d />''' % (int(ecmOb.pk)))
        ephysDropTag.append(ecmTag)
        name = ecmOb.ephys_prop.name
        optionTag = ephysDropTag.find(value = name)
        optionTag["selected"] = "selected"
    if ncmOb is not None:
        radioTag = tagSoup.find("form", {"id": "ephys_neuron_radio"})
        neuronRadio = radioTag.find(value = "neuron")
        neuronRadio['checked'] = "checked"
        dropTag = tagSoup.find("form", {"name": "neuron_form"})
        ncmTag = BeautifulSoup('''<input type="hidden" name="ncm_id" value=%d />''' % (int(ncmOb.pk)))
        name = ncmOb.neuron.name
        optionTag = dropTag.find(value = name)
        optionTag["selected"] = "selected"
    return tagSoup
    
def add_box_id_to_forms(td_tag):
    if td_tag is not None:
        formTags = td_tag.find_all("form")
        for t in formTags:
            t.append('<input type="hidden" name="box_id" value=%r />')
        return t
    else:
        return td_tag
        
def ephys_neuron_dropdown2(csrf_token, dataTableOb, anmObs = None):
    csrf_tok = csrf_token
    chunk = ''
    #anmObs = dataTableOb.article.neuronarticlemap_set.order_by('-num_mentions')
    chunk += '''<form class="ephys_neuron_radio" id="ephys_neuron_radio">
                <input type="radio" name="ephys_neuron_radio" value="ephys_prop" checked />Ephys Prop
                <input type="radio" name="ephys_neuron_radio" value="neuron"/>Neuron
                </form>'''
    chunk += ephys_dropdown_form2(csrf_tok, dataTableOb)
    chunk += neuron_dropdown_form2(csrf_tok, dataTableOb, anmObs)
    chunk = re.sub(r'>[\s]+<', '> <', chunk)
    #print chunk
    return BeautifulSoup(chunk)    
    
def ephys_dropdown_form2(csrf_tok, dataTableOb):
    chunk = ''
    chunk += '''<form action="/neuroelectro/ephys_concept_map/mod/" method="post" class="ephys_dropdown" name="ephys_form">'''
    chunk += '''<input type="hidden" name="csrfmiddlewaretoken" value="%s"/>''' % str(csrf_tok)
    chunk +='''<input type="hidden" name="data_table_id" value=%d />''' % (int(dataTableOb.pk))
    ephysDropdownHtml = genEphysListDropdown2()
    chunk += ephysDropdownHtml
    chunk += '''<input type="submit" value="Submit" class="dropdown"/>'''
    chunk += '''</form>'''        
    return chunk
    
def neuron_dropdown_form2(csrf_tok, dataTableOb, anmObs):
    chunk = ''
    chunk += '''<form action="/neuroelectro/neuron_concept_map/mod/" method="post" class="neuron_dropdown" name="neuron_form">'''
    chunk += '''<input type="hidden" name="csrfmiddlewaretoken" value="%s"/>''' % str(csrf_tok)
    chunk +='''<input type="hidden" name="data_table_id" value=%d />''' % (int(dataTableOb.pk))
    if anmObs is not None:
        neuronNameList = [anmOb.neuron.name for anmOb in anmObs]
        neuronNameList = [ key for key,_ in groupby(neuronNameList)] 
    else:
        neuronNameList = None
    neuronDropdownHtml = genNeuronListDropdown2(neuronNameList)
    chunk += neuronDropdownHtml
    chunk += '''<input type="submit" value="Submit" class="dropdown"/>'''
    chunk += '''<br/><a href="/neuroelectro/neuron/add" target="_blank">Add a new neuron</a>'''
    chunk += '''</form>'''                 
    return chunk

def genEphysListDropdown2():
    chunk = '''<select class="ephys_dropdown" name ="ephys_dropdown">'''
    chunk += '''<option value=%r>%r</option>''' % ('None selected', 'None selected')
    for ephys_prop in EphysProp.objects.all():
        ephys_name = str(ephys_prop.name)
        chunk += '''<option value=%r>%r</option>''' % (str(ephys_prop.name), str(ephys_prop.name))
    chunk+= '''</select>'''
    return chunk
    
def genNeuronListDropdown2(neuronNameList = None):
    chunk = '''<select class="neuron_dropdown" name ="neuron_dropdown">'''
    if neuronNameList is not None:
        for name in neuronNameList:
            neuron_name = str(name)
            chunk += '''<option value=%r>%r</option>''' % (neuron_name, neuron_name)
    chunk += '''<option value=%r>%r</option>''' % ('None selected', 'None selected')
    for neuron in Neuron.objects.all():
        neuron_name = str(neuron.name)
        chunk += '''<option value=%r>%r</option>''' % (neuron_name, neuron_name)
    chunk+= '''</select>'''
    return chunk    
     
def genEphysListDropdown(defaultSelected = None):
    chunk = '''<select class="ephys_dropdown" name ="ephys_dropdown">'''
    chunk += '''<option value=%r>%r</option>''' % ('None selected', 'None selected')
    for ephys_prop in EphysProp.objects.all():
        ephys_name = str(ephys_prop.name)
        if ephys_name == defaultSelected:
            chunk += '''<option selected="selected" value=%r name = %r>%r</option>''' % (ephys_name, ephys_name, ephys_name)
        else:
            chunk += '''<option value=%r>%r</option>''' % (str(ephys_prop.name), str(ephys_prop.name))
    chunk+= '''</select>'''
    return chunk
    
def genNeuronListDropdown(defaultSelected = None, neuronNameList = None):
    chunk = '''<select class="neuron_dropdown" name ="neuron_dropdown">'''
    if neuronNameList is not None:
        for name in neuronNameList:
            neuron_name = str(name)
            if neuron_name == defaultSelected:
                chunk += '''<option selected="selected" value=%r name = %r>%r</option>''' % (neuron_name, neuron_name, neuron_name)
            else:
                chunk += '''<option value=%r>%r</option>''' % (neuron_name, neuron_name)
    chunk += '''<option value=%r>%r</option>''' % ('None selected', 'None selected')
    for neuron in Neuron.objects.all():
        neuron_name = str(neuron.name)
        if neuron_name == defaultSelected:
            chunk += '''<option selected="selected" value=%r name = %r>%r</option>''' % (neuron_name, neuron_name, neuron_name)
        else:
            chunk += '''<option value=%r>%r</option>''' % (neuron_name, neuron_name)
    chunk+= '''</select>'''
    #print chunk
    return chunk

    
def ephys_neuron_dropdown(csrf_token, dataTableOb, tag_id = None, ecmOb = None, ncmOb = None, anmObs = None, validate_bool = False):
    csrf_tok = csrf_token
    chunk = ''
    if ecmOb is not None:
        chunk += '''<br/><i>Concept: %s</i>''' % ecmOb.ephys_prop.name
    if ncmOb is not None:
        chunk += '''<br/><i>Concept: %s</i>''' % ncmOb.neuron.name
    if validate_bool == True:
        anmObs = dataTableOb.article.neuronarticlemap_set.order_by('-num_mentions')
        chunk += '''<form class="ephys_neuron_radio" id="ephys_neuron_radio">
                    <input type="radio" name="ephys_neuron_radio" value="ephys_prop" checked />Ephys Prop
                    <input type="radio" name="ephys_neuron_radio" value="neuron"/>Neuron
                    </form>'''
        chunk += ephys_dropdown_form(csrf_tok, tag_id, dataTableOb, ecmOb)
        chunk += neuron_dropdown_form(csrf_tok, tag_id, dataTableOb, ncmOb, anmObs)
        chunk = re.sub(r'>[\s]+<', '> <', chunk)
    return BeautifulSoup(chunk)
    
def ephys_dropdown_form(csrf_tok, tag_id, dataTableOb, ecmOb):
    chunk = ''
    chunk += '''<form action="/ephys_concept_map/mod/" method="post" class="ephys_dropdown" name="ephys_form">'''
    chunk += '''<input type="hidden" name="csrfmiddlewaretoken" value="%s"/>''' % str(csrf_tok)
    #chunk += '''{% autoescape off %}{{ csrf_str }}{% endautoescape %}'''
    if tag_id is not None:
        chunk +=''' <input type="hidden" name="box_id" value=%r />
                    <input type="hidden" name="data_table_id" value=%d />''' % (tag_id, int(dataTableOb.pk))
    if ecmOb is not None:
        chunk += '''<input type="hidden" name="ecm_id" value=%d />''' % (int(ecmOb.pk))
        ephysDropdownHtml = genEphysListDropdown(str(ecmOb.ephys_prop.name))
    else:
        ephysDropdownHtml = genEphysListDropdown()
    chunk += ephysDropdownHtml
    chunk += '''<input type="submit" value="Submit" class="dropdown"/>'''
    if ecmOb is not None and ecmOb.note:
        note_str = re.sub('\s', '_', ecmOb.note)
        chunk += '''<br/>Note: <input type="text" name="ephys_note" class="dropdown" value=%s/>''' % (note_str)
    else:
        chunk += '''<br/>Note: <input type="text" name="ephys_note" class="dropdown">'''
    chunk += '''</form>'''        
    return chunk
    
def neuron_dropdown_form(csrf_tok, tag_id, dataTableOb, ncmOb, anmObs):
    chunk = ''
    chunk += '''<form action="/neuron_concept_map/mod/" method="post" class="neuron_dropdown" name="neuron_form">'''
    chunk += '''<input type="hidden" name="csrfmiddlewaretoken" value="%s"/>''' % str(csrf_tok)
    chunk +=''' <input type="hidden" name="box_id" value=%r />
                    <input type="hidden" name="data_table_id" value=%d />''' % (tag_id, int(dataTableOb.pk))
    if anmObs is not None:
        neuronNameList = [anmOb.neuron.name for anmOb in anmObs]
        neuronNameList = [ key for key,_ in groupby(neuronNameList)] 
        #print neuronNameList
    else:
        neuronNameList = None
    if ncmOb is not None:
        chunk += '''<input type="hidden" name="ncm_id" value=%d />''' % (int(ncmOb.pk))
        neuronDropdownHtml = genNeuronListDropdown(str(ncmOb.neuron.name), neuronNameList)
    else:
        neuronDropdownHtml = genNeuronListDropdown(None, neuronNameList)
    chunk += neuronDropdownHtml
    chunk += '''<input type="submit" value="Submit" class="dropdown"/>'''
    if ncmOb is not None and ncmOb.note:
        note_str = re.sub('\s', '_', ncmOb.note)
        chunk += '''<br/>Note: <input type="text" name="neuron_note" class="dropdown" value=%s>'''% (note_str)
    else:
        chunk += '''<br/>Note: <input type="text" name="neuron_note" class="dropdown">'''
    chunk += '''<br/><a href="/neuroelectro/neuron/add" target="_blank">Add a new neuron</a>'''
    chunk += '''</form>'''                 
    return chunk
    
def dropdownMenu1(csrf_token, tag_id, dataTableOb, ecmOb = None):
    csrf_tok = csrf_token
    chunk = ''
    if ecmOb is not None:
        chunk += '''<br/><i>Concept: %s</i>''' % ecmOb.ephys_prop.name
    chunk += '''<form action="/ephys_concept_map/mod/" method="post" class="dropdown" name="ephys_form">'''
    chunk += '''<input type="hidden" name="csrfmiddlewaretoken" value="%s"/>''' % str(csrf_tok)
    #chunk += '''{% autoescape off %}{{ csrf_str }}{% endautoescape %}'''
    chunk +=''' <input type="hidden" name="box_id" value=%r />
                    <input type="hidden" name="data_table_id" value=%d />''' % (tag_id, int(dataTableOb.pk))
    if ecmOb is not None:
        chunk += '''<input type="hidden" name="ecm_id" value=%d />''' % (int(ecmOb.pk))
        ephysDropdownHtml = genEphysListDropdown(str(ecmOb.ephys_prop.name))
    else:
        ephysDropdownHtml = genEphysListDropdown()
    chunk += ephysDropdownHtml
    chunk += '''<input type="submit" value="Submit" class="dropdown"/>'''
    chunk += '''</form>''' 
                    # <select class="dropdown">
                        # <option>Milk</option>
                        # <option>Coffee</option>
                        # <option>Tea</option>
                    # </select>
                
    chunk = re.sub(r'>[\s]+<', '> <', chunk)
    return BeautifulSoup(chunk)
