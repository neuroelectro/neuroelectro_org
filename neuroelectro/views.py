# -*- coding: utf-8 -*-
# Create your views here.
import json
import os
import re
import smtplib
import textwrap
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from itertools import groupby
from time import strftime

import numpy as np
from bs4 import BeautifulSoup
from ckeditor.widgets import CKEditorWidget
from crispy_forms.bootstrap import FormActions
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout,Fieldset,Submit
from django import forms
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.signals import user_logged_in
from django.core.context_processors import csrf
from django.core.exceptions import ObjectDoesNotExist
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.core.mail import BadHeaderError
from django.db.models import Count, Min, Max
from django.db.models import Q
from django.forms.formsets import DELETION_FIELD_NAME
from django.forms.models import BaseInlineFormSet, inlineformset_factory
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, render_to_response, get_object_or_404
from django.template import RequestContext
from django.template.defaulttags import register
from django.template.response import TemplateResponse

import neuroelectro.models as m
from article_text_mining.article_html_db_utils import add_table_ob_to_article, add_single_full_text, \
    process_uploaded_table
from article_text_mining.assign_metadata import record_compounds, update_amd_obj
from article_text_mining.assign_table_ephys_data import assign_data_vals_to_table
from article_text_mining.html_process_tools import getMethodsTag
from article_text_mining.mine_ephys_prop_in_table import get_units_from_table_header
from article_text_mining.resolve_data_float import resolve_data_float
from db_functions import add_ephys_nedm
from db_functions.compute_field_summaries import computeArticleSummaries, computeNeuronEphysSummariesAll
from db_functions.normalize_ephys_data import check_data_val_range, normalize_nedm_val
from db_functions.pubmed_functions import add_single_article
from helpful_functions import trunc
from neuroelectro.forms import DataTableUploadForm, ArticleMetadataForm, ArticleFullTextUploadForm, NeuronConversionForm

# neuroNER sherlok imports
from sherlok import Sherlok
from requests import ConnectionError
from neuroner.normalize import clean_annotations, normalize_annots
from db_functions.add_neuroner_annotations import calculate_neuroner_similarity


# Overrides Django's render_to_response.
# Obsolete now that 'render' exists. render_to_response(x,y,z) equivalent to render(z,x,y).  
def render(template,inDict,request):
    return render_to_response(template,inDict,context_instance=RequestContext(request))

# Adds a filter that enables access of dictionary items in templates, http://stackoverflow.com/questions/8000022/django-template-how-to-lookup-a-dictionary-value-with-a-variable
@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

def login(request):
    from django.contrib.auth.views import login as django_login
    user_logged_in.connect(login_hook)

    d = {'plus_id':settings.SOCIAL_AUTH_GOOGLE_PLUS_KEY}
    return django_login(request,
                        template_name='neuroelectro/login.html',
                        extra_context=d)

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
            
def unsubscribe(request):
    if request.POST:
        email = request.POST['email']
        if validateEmail(email):
            if (m.MailingListEntry.objects.filter(email = email).exists()):
                m.MailingListEntry.objects.filter(email = email).delete()
                legend = "Your email has been successfully removed from the mailing list"
                send_email([email], "Unsubscribed from neuroelectro.org", """
You have successfully unsubscribed from neuroelectro.org. If desired at a later date - subscribe to our emails on the front page of the website.
                """)
            else:
                legend = "The entered email is not on the mailing list"
        else:
            legend = "The email isn't valid, please enter it again"
    else:
        legend = "Enter your email to unsubscribe from the NeuroElectro mailing list"
        
    class UnsubscribeForm(forms.Form):
        email = forms.EmailField(
            label = "Email Address",
            required = True,
        )
        def __init__(self, *args, **kwargs):
            self.helper = FormHelper()
            self.helper.form_id = 'id-unsubscribeForm'
            self.helper.form_class = 'blueForms'
            self.helper.form_method = 'post'
            self.helper.form_action = '/unsubscribe/'
            self.helper.layout = Layout(
                Fieldset(
                    "<p align='left'>%s</p>" % legend,
                    'email'
                    ),
                FormActions(
                    Submit('submit', 'Unsubscribe',align='middle'),
                    )
                )
            super(UnsubscribeForm, self).__init__(*args, **kwargs)
    returnDict = {}
    returnDict['form'] = UnsubscribeForm
    return render('neuroelectro/unsubscribe.html', returnDict, request)

def splash_page(request):
    return render('neuroelectro/splash_page.html', {}, request)

def curator_view(request):
    username = None
    if request.user.is_authenticated():
        username = request.user.get_username()
    #curator_list = m.User.objects.filter(assigned_neurons__isnull = False).distinct()
    returnDict = {'username': username}  
    return render('neuroelectro/curator_view.html', returnDict, request)

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
    def __init__(self, request, *args, **kwargs):
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
    if 'email' in request.POST:
        email = request.POST['email']
        if validateEmail(email):
            name = request.POST['name']
            #comments = request.POST['comments']
            legend = "Your email has been successfully added! "
            mailing_list_entry_ob = m.MailingListEntry.objects.get_or_create(email = email)[0]
            mailing_list_entry_ob.name = name
            #mailing_list_entry_ob.comments = comments
            mailing_list_entry_ob.save()
            send_email([email], "Neuroelectro confirmation email", """
Congratulations,

You have been added to Neuroelectro mailing list. We will now be able to notify you of any updates to the website.

If this is a mistake: unsubscribe at neuroelectro.org/unsubscribe

Best wishes from the Neuroelectro development team.            
            """)
        else:
            legend = "Your email isn't valid, please enter it again"
    else:
        legend = "Please add your email (we promise we won't spam you)"
    message = {}
    message['response'] = legend
    return HttpResponse(json.dumps(message), mimetype='application/json')

def send_email(TO, SUBJECT, TEXT):
    # TO must be a list
    gmail_user = settings.ADMIN_EMAIL_ADDRESS
    gmail_pwd = settings.ADMIN_EMAIL_PASSWORD

    # Prepare actual message
    message = MIMEMultipart('alternative')
    message['Subject'] = SUBJECT
    message['From'] = gmail_user
    message['To'] = ", ".join(TO)
    message.attach(MIMEText(TEXT, 'plain'))
    message.attach(MIMEText(TEXT, 'html'))
    
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.ehlo()
        server.starttls()
        server.login(gmail_user, gmail_pwd)
        server.sendmail(gmail_user, TO, message.as_string())
        server.close()
        print 'Successfully sent the email'
    except:
        print "Failed to send the email"
        
# Overwriting Django mail_admins function in favor of using google SMTP server
def mail_admins(subject, message):
    mailingList = [a[1] for a in settings.ADMINS]
    send_email(mailingList, subject, message)

@user_passes_test(lambda u: u.is_staff)        
def admin_list_email(request):
    legend = "Type the body of the email in the text box and choose a title. Click submit to email all subscribers."
    if request.POST:
        text = request.POST['text']
        title = request.POST['title']
        if (text and title):
            mailingList = [o.email for o in m.MailingListEntry.objects.all()]
            legend = "Email \"%s\" has been sent to all subscribers" % title
            send_email(mailingList, title, text)

    class Admin_List_Email_Form(forms.Form):
        title = forms.CharField(
            label = "Subject:",
            max_length = 1000,
            required = True
        )
        text = forms.CharField(
            widget = CKEditorWidget(),                   
            label = 'Body of the email:',
            max_length = 10000,
            required = True
        )
        def __init__(self, *args, **kwargs):
            self.helper = FormHelper()
            self.helper.form_id = 'id-admin_list_email_form'
            self.helper.form_class = 'blueForms'
            self.helper.form_method = 'post'
            self.helper.form_action = '/admin_list_email/'
            self.helper.layout = Layout(
                Fieldset(
                    "<p align='left'>%s</p>" % legend,
                    'title',
                    'text'
                    ),
                FormActions(
                    Submit('submit', 'Send the email to subscribers',align='middle'),
                    )
                )
            super(Admin_List_Email_Form, self).__init__(*args, **kwargs)
    returnDict = {}
    returnDict['form'] = Admin_List_Email_Form
    return render('neuroelectro/admin_list_email.html', returnDict, request)

#This mailing list form appears at neuroelectro/mailing_list_form
def mailing_list_form(request):
    successBool = False
    if request.POST:
        email = request.POST['email']
        if validateEmail(email):
            name = request.POST['name']
            comments = request.POST['comments']
            legend = "Your email has been successfully added! "
            mailing_list_entry_ob = m.MailingListEntry.objects.get_or_create(email = email)[0]
            mailing_list_entry_ob.name = name
            mailing_list_entry_ob.comments = comments
            mailing_list_entry_ob.save()
            successBool = True
            send_email([email], "Neuroelectro confirmation email", """
Congratulations,

You have been added to Neuroelectro mailing list. We will now be able to notify you of any updates to the website.

If this is a mistake: unsubscribe at neuroelectro.org/unsubscribe

Best wishes from the Neuroelectro development team.            
            """)
        else:
            legend = "Your email isn't valid, please enter it again"
    else:
        legend = "Please add your email (we promise not to spam you)"
        
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
                    ),
                )
            super(MailingListForm, self).__init__(*args, **kwargs)
    returnDict = {}
    returnDict['form'] = MailingListForm
    returnDict['successBool'] = successBool
    return render('neuroelectro/mailing_list_form.html', returnDict, request)

def validateEmail( email ):
    from django.core.validators import validate_email
    from django.core.exceptions import ValidationError
    try:
        validate_email( email )
        return True
    except ValidationError:
        return False

def neuron_index(request):
    neuron_list = m.Neuron.objects.all()
    return render('neuroelectro/neuron_index.html', {'neuron_list': neuron_list},request)

#@login_required
def neuron_detail(request, neuron_id):
    n = get_object_or_404(m.Neuron, pk=neuron_id)
    nedm_list = m.NeuronEphysDataMap.objects.filter(neuron_concept_map__neuron = n, 
                                                  val_norm__isnull = False, 
                                                  ephys_concept_map__ephys_prop__in = get_ephys_prop_ordered_list()
                                                  ).order_by('ephys_concept_map__ephys_prop__name')
    ephys_nedm_list = []
    ephys_count = 0
    neuron_mean_ind = 2
    all_neurons_ind = 3
    neuron_mean_data_pt = 0
    neuron_mean_sd_line = 0
    for e in get_ephys_prop_ordered_list():
        nedm_list_by_ephys = nedm_list.filter(ephys_concept_map__ephys_prop = e)
        data_list_validated, data_list_unvalidated, neuronNameList, value_list_all = ephys_prop_to_list2(nedm_list_by_ephys)
        if len(data_list_validated) > 0:
            try:
                nes = m.NeuronEphysSummary.objects.get(neuron = n, ephys_prop = e)
                mean_val = nes.value_mean
                sd_val = nes.value_sd
                num_articles = nes.num_articles
            except ObjectDoesNotExist:
                mean_val = None
                sd_val = None
                num_articles = 0
            if mean_val is None:
                mean_val = 0
            if sd_val is None:
                sd_val = 0
            std_min_val = mean_val - sd_val
            std_max_val = mean_val + sd_val
            neuron_mean_data_pt = [ [neuron_mean_ind, trunc.trunc(mean_val), trunc.trunc(sd_val), str(num_articles), str(e.id)] ]
            neuron_mean_sd_line = [[neuron_mean_ind, std_min_val], [neuron_mean_ind, std_max_val]]
            # now calculate averages across all neurons
            eps = m.EphysPropSummary.objects.get(ephys_prop = e)
            mean_val_all = eps.value_mean_neurons
            sd_val_all = eps.value_sd_neurons
            if sd_val_all is None:
                sd_val_all = 0
            if mean_val_all is None:
                mean_val_all = 0
            num_neurons_all = eps.num_neurons
            all_neurons_data_pt = [[all_neurons_ind, trunc.trunc(mean_val_all), trunc.trunc(sd_val_all), str(num_neurons_all), str(e.id)]]
            std_min_val_all = mean_val_all - sd_val_all
            std_max_val_all = mean_val_all + sd_val_all
            all_neurons_sd_line = [[all_neurons_ind, std_min_val_all], [all_neurons_ind, std_max_val_all]]
            if len(data_list_unvalidated) is 0:
                data_list_unvalidated = [data_list_unvalidated]
            if len(data_list_validated) is 0:
                data_list_validated = [data_list_validated]
            ephys_nedm_list.append(['chart'+str(ephys_count), e, data_list_validated, data_list_unvalidated, neuron_mean_data_pt, neuron_mean_sd_line, all_neurons_data_pt, all_neurons_sd_line])
            ephys_count += 1
    for nedm in nedm_list:
        try:
            title = nedm.source.data_table.article.title
        except AttributeError:
            title = nedm.source.user_submission.article.title
        nedm.title = title
    articles = m.Article.objects.filter(Q(datatable__datasource__neuronconceptmap__neuronephysdatamap__in = nedm_list,
                                                     datatable__datasource__neuronconceptmap__times_validated__gte = 1) | 
                                                     Q(usersubmission__datasource__neuronconceptmap__neuronephysdatamap__in = nedm_list)).distinct()
    region_str = ''
    if n.regions:
        region_list = [str(region.allenid) for region in n.regions.all()]
        region_str = ','.join(region_list)
    curator_list = m.User.objects.filter(assigned_neurons__in = [n])
    returnDict = {'neuron': n, 'nedm_list': nedm_list, 'ephys_nedm_list': ephys_nedm_list, 'neuron_mean_data_pt':neuron_mean_data_pt,
        'neuron_mean_sd_line':neuron_mean_sd_line, 'article_list':articles, 'region_str':region_str, 'curator_list':curator_list}
    return render('neuroelectro/neuron_detail.html',returnDict,request)

def neuron_data_detail(request, neuron_id):
    n = get_object_or_404(m.Neuron, pk=neuron_id)
    nedm_list = m.NeuronEphysDataMap.objects.filter(neuron_concept_map__neuron = n, ephys_concept_map__ephys_prop__in = get_ephys_prop_ordered_list()).order_by('ephys_concept_map__ephys_prop__name')
    for nedm in nedm_list:
        try:
            article = nedm.source.data_table.article
        except AttributeError:
            article = nedm.source.user_submission.article
        nedm.article = article
    returnDict = {'neuron': n, 'nedm_list': nedm_list}
    return render('neuroelectro/neuron_data_detail.html',returnDict,request)

def ephys_data_detail(request, ephys_prop_id):
    e = get_object_or_404(m.EphysProp, pk=ephys_prop_id)
    nedm_list = m.NeuronEphysDataMap.objects.filter(ephys_concept_map__ephys_prop = e).order_by('neuron_concept_map__neuron__name')
    for nedm in nedm_list:
        try:
            article = nedm.source.data_table.article
        except AttributeError:
            article = nedm.source.user_submission.article
        nedm.article = article
    returnDict = {'ephys_prop': e, 'nedm_list':nedm_list}
    return render('neuroelectro/ephys_data_detail.html',returnDict,request)
    
def ephys_prop_index(request):
    ephys_prop_list = get_ephys_prop_ordered_list()
    returnDict = {'ephys_prop_list': ephys_prop_list}
    return render('neuroelectro/ephys_prop_index.html', returnDict, request)

def get_ephys_prop_ordered_list():
    ephys_props = m.EphysProp.objects.all()
    ephys_props = ephys_props.exclude(id__in = [15, 11, 12, 9, 25])
    ephys_props = ephys_props.order_by('-ephyspropsummary__num_nedms')
    return ephys_props

def ephys_concept_map_detail(request, ephys_concept_map_id):
    ecm = get_object_or_404(m.EphysConceptMap, pk=ephys_concept_map_id)
    return render('neuroelectro/ephys_concept_map_detail.html', {'ephys_concept_map': ecm}, request)  

def concept_map_detail(request, data_table_id, data_table_cell_id):
    data_table = get_object_or_404(m.DataTable, pk=data_table_id)
    concept_maps = data_table.get_concept_maps()
    cm_list = []
    for cm in concept_maps:
        if cm.dt_id == data_table_cell_id:
            cm_list.append(cm)
    returnDict = {'concept_maps' : cm_list}
    return render('neuroelectro/concept_map_detail.html', returnDict, request)  

def ephys_prop_detail(request, ephys_prop_id):
    e = get_object_or_404(m.EphysProp, pk=ephys_prop_id)
    nedm_list = m.NeuronEphysDataMap.objects.filter(ephys_concept_map__ephys_prop = e, val_norm__isnull = False).order_by('neuron_concept_map__neuron__name')
    if e.id == 16:
        nedm_list = m.NeuronEphysDataMap.objects.filter(ephys_concept_map__ephys_prop__id__in = [16, 19], val_norm__isnull = False).order_by('neuron_concept_map__neuron__name')
    data_list_validated, data_list_unvalidated, neuronNameList, value_list_all = ephys_prop_to_list2(nedm_list)
    neuron_list = [m.Neuron.objects.get(name = nName) for nName in neuronNameList]
    #log_ephys_axis_names = ['input resistance', 'rheobase', 'cell capacitance']
    if e.plot_transform == 'log10':
        log_ephys_axis_flag = 1
    else:
        log_ephys_axis_flag = 0
    if len(data_list_unvalidated) is 0:
        data_list_unvalidated = [data_list_unvalidated]
    if len(data_list_validated) is 0:
        data_list_validated = [data_list_validated]
    return render('neuroelectro/ephys_prop_detail.html', {'ephys_prop': e, 'nedm_list':nedm_list, 
                                                                    'data_list_validated': data_list_validated,
                                                                    'data_list_unvalidated': data_list_unvalidated,
                                                                     'neuronNameList':neuronNameList,
                                                                     'neuron_list':neuron_list, 
                                                                     'log_ephys_axis_flag':log_ephys_axis_flag},
                                request)  

def ephys_prop_correlation(request):
    pass

def neuron_clustering(request):
    neuron_summary_list = m.NeuronSummary.objects.filter(cluster_xval__isnull = False).order_by('num_articles')
    neuron_list = m.Neuron.objects.filter(neuronsummary__in = neuron_summary_list).order_by('name')
    data_pts = []
    data_pts2 = []
    for nsOb in neuron_summary_list:
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
    return render('neuroelectro/neuron_clustering.html', returnDict, request) 

def neuron_ephys_prop_count(request):
    neuron_list = m.Neuron.objects.filter(neuronconceptmap__times_validated__gte = 1).distinct()
    ephys_list = m.EphysProp.objects.all()
    valid_pk_list = range(2,8)
    ephys_list = ephys_list.filter(pk__in = valid_pk_list)
    neuron_ephys_count_table = []

    for n in neuron_list:
        temp_ephys_count_list = [0]*ephys_list.count()
        for i,e in enumerate(ephys_list):
            nes_query = m.NeuronEphysSummary.objects.filter(neuron = n, ephys_prop = e)
            if nes_query.count() > 0:
                temp_ephys_count_list[i] = nes_query[0].num_articles
        neuron_ephys_count_table.append(temp_ephys_count_list)
        n.ephys_count_list = temp_ephys_count_list
        n.total_ephys_count = sum(temp_ephys_count_list)
        n.num_articles = n.neuronsummary_set.all()[0].num_articles
    returnDict = {'neuron_list': neuron_list, 'ephys_list': ephys_list, 'neuron_ephys_count_table' : neuron_ephys_count_table}
    return render('neuroelectro/neuron_ephys_prop_count.html', returnDict, request) 

# TODO: refactor this function
def ephys_prop_to_list2(nedm_list):
    data_list_validated = []
    data_list_unvalidated = []
    cnt = 0
    neuronCnt = 0
    value_list_all = []
    oldNeuronName = []
    neuronNameList = oldNeuronName
    #main_ephys_prop_ids = [2, 3, 4, 5, 6, 7]
    main_ephys_prop_ids = range(1, 28)
    for nedm in nedm_list:
        val = nedm.val_norm
        if not check_data_val_range(val, nedm.ephys_concept_map.ephys_prop):
            val = None
        if val is None:
            continue
        try:
            art = nedm.source.data_table.article
        except AttributeError:
            art = nedm.source.user_submission.article
        neuronName = nedm.neuron_concept_map.neuron.name
        if neuronName != oldNeuronName:
            neuronCnt += 1
            oldNeuronName = neuronName
            neuronNameList.append(str(oldNeuronName))
        neuron_long_name = nedm.neuron_concept_map.neuron_long_name
        if neuron_long_name:
            neuronName = neuronName + " (" + neuron_long_name + ')'
        neuronName = neuronName.encode("iso-8859-15", "replace")
        neuronName = "</br>".join(textwrap.wrap(neuronName, width=70))
        title = art.title.encode("iso-8859-15", "replace")
        title = "</br>".join(textwrap.wrap(title, width=70))
        journal_name = art.journal.short_title
        journal_name = journal_name.encode("iso-8859-15", "replace")
        pub_year = str(art.pub_year).encode("iso-8859-15", "replace")
        author_list = art.author_list_str
        if not author_list:
            author_list = ''
        author_list = author_list.encode("iso-8859-15", "replace")
        author_list = "</br>".join(textwrap.wrap(author_list, width=70))
        try:
            data_table_ind = nedm.source.data_table.id
        except AttributeError:
            #data_table_ind = 0
            # Note: this is a hack to accomodate data point views going to article page
            data_table_ind = -art.pk
        trunc_val = trunc.trunc(val, 3)
        value_list = [neuronCnt + np.random.randn()/100.0, trunc_val, str(neuronName), title, author_list, journal_name, pub_year, str(data_table_ind)]
        value_list_all.append(val)
        if nedm.neuron_concept_map.times_validated != 0 and nedm.ephys_concept_map.times_validated and nedm.ephys_concept_map.ephys_prop.id in main_ephys_prop_ids:
            data_list_validated.append(value_list)
        else:
            data_list_unvalidated.append(value_list)
        # neuron_ephys_val_list.append([neuronCnt, val, str(nedm.neuron.name), title, str(data_table_ind)])    
        cnt += 1
    return data_list_validated, data_list_unvalidated, neuronNameList, value_list_all

def article_detail(request, article_id):
    article = get_object_or_404(m.Article, pk=article_id)
    metadata_list = m.MetaData.objects.filter(articlemetadatamap__article = article).distinct()
    nedm_list = []

    dts = article.datatable_set.all()
    for datatable in dts:
        nedm_list_temp = datatable.datasource_set.get().neuronephysdatamap_set.all().order_by('neuron_concept_map__neuron__name', 'ephys_concept_map__ephys_prop__name')
        nedm_list.extend(nedm_list_temp)
    for usersubmission in article.usersubmission_set.all():
        nedm_list_temp = usersubmission.datasource_set.get().neuronephysdatamap_set.all().order_by('neuron_concept_map__neuron__name', 'ephys_concept_map__ephys_prop__name')
        nedm_list.extend(nedm_list_temp)

    dts = dts.annotate(times_validated = Max('datasource__ephysconceptmap__times_validated'))
#     dts = dts.annotate(min_validated = Min('datasource__ephysconceptmap__times_validated'))
    dts = dts.distinct()
    dts = dts.annotate(num_ecms=Count('datasource__ephysconceptmap__ephys_prop', distinct = True))
    dts = dts.order_by('-num_ecms')

    robot_user = m.get_robot_user()
    for dt in dts:
        # who has curated article
        user_list = dt.get_curating_users()
        if robot_user in user_list:
            user_list.remove(robot_user)
        dt.curated_by = user_list

    returnDict = {'article': article, 'metadata_list':metadata_list, 'nedm_list':nedm_list, 'data_table_list': dts}
    return render('neuroelectro/article_detail.html', returnDict, request)


def article_detail_pmid(request, article_pmid):
    """Kind of a hack, but checks if article exists in DB, and if not, just returns pubmed link
        based on entered pmid"""
    try:
        article = m.Article.objects.get(pmid=article_pmid)
        urlStr = '/article/%d' % article.pk
    except ObjectDoesNotExist:
        urlStr = "http://www.ncbi.nlm.nih.gov/pubmed/%s" % article_pmid

    return HttpResponseRedirect(urlStr)


def article_full_text_detail(request, article_id):
    article = get_object_or_404(m.Article, pk=article_id)
    article_full_text = article.get_full_text()
    returnDict = {'article_full_text': article_full_text.get_content()}
    # full_text = article.articlefulltext_set.all()[0].get_content()
    return render('neuroelectro/article_full_text_detail.html', returnDict, request)


def article_metadata(request, article_id):
    article = get_object_or_404(m.Article, pk=article_id)
    if request.POST:
        user = request.user
        ordinal_list_names = ['Species', 'Strain', 'ElectrodeType', 'PrepType', 'JxnPotential']
        cont_list_names = ['AnimalAge', 'AnimalWeight', 'RecTemp', 'JxnOffset']
        
        for o in ordinal_list_names:
            if o in request.POST:
                # check for submission of note
                note_post_key = o + 'Note'
                if note_post_key in request.POST:
                    note = request.POST[note_post_key]
                else:
                    note = None
                #curr_mds = m.MetaData.objects.filter(name = o)
                curr_list = request.POST.getlist(o)
                amdms_old = list(m.ArticleMetaDataMap.objects.filter(article = article, metadata__name = o))
                for elem in curr_list:
                    metadata_ob = m.MetaData.objects.filter(pk = elem)[0]
                    amdmQuerySet = m.ArticleMetaDataMap.objects.filter(article = article, metadata = metadata_ob)
                    if amdmQuerySet.count() > 0:
                        amdm = amdmQuerySet[0]
                        # check if amdm ob already exists
                        if amdm in amdms_old:
                            amdms_old.remove(amdm)
                        amdm.metadata = metadata_ob
                        amdm.times_validated += 1
                        amdm.note = note
                        amdm.save()
                    else:
                        amdm = m.ArticleMetaDataMap.objects.create(article = article, metadata = metadata_ob, added_by = user, times_validated = 1, note = note)
                for amdm in amdms_old:
                    amdm.delete()
            else:
                amdms = m.ArticleMetaDataMap.objects.filter(article = article, metadata__name = o)
                amdms.delete()
        for c in cont_list_names:
            if c in request.POST:
                # check for submission of note
                note_post_key = c + 'Note'
                if note_post_key in request.POST:
                    note = request.POST[note_post_key]
                else:
                    note = None
                entered_string = unicode(request.POST[c])
                if len(entered_string) > 0:
                    retDict = resolve_data_float(entered_string, initialize_dict=True)
                    if retDict:
                        cont_value_ob = m.ContValue.objects.get_or_create(mean = retDict['value'], min_range = retDict['min_range'],
                                                                          max_range = retDict['max_range'], stderr = retDict['error'], n = retDict['num_obs'])[0]
                        metadata_ob = m.MetaData.objects.get_or_create(name=c, cont_value=cont_value_ob)[0]
                        # check if amdm ob already exists, if it does, just update pointer for amdm, but leave old md intact
                        amdmQuerySet = m.ArticleMetaDataMap.objects.filter(article = article, metadata__name = c)
                        if amdmQuerySet.count() > 0:
                            amdm = amdmQuerySet[0]
                            amdm.metadata = metadata_ob
                            amdm.times_validated += 1
                            amdm.note = note
                            amdm.save()
                        else:
                            amdm = m.ArticleMetaDataMap.objects.create(article = article, metadata = metadata_ob, added_by = user, times_validated = 1, note = note)
                else:
                    amdms = m.ArticleMetaDataMap.objects.filter(article = article, metadata__name = c)
                    amdms.delete()
                    
        solution_names = {"external": 'ExternalSolution', 
                          "internal": 'InternalSolution'}
        note = ""
        
        for soln, soln_name in solution_names.iteritems():
            if soln_name in request.POST:
                if request.POST[soln_name]:
                    note_post_key = soln_name + 'Note'
                    if note_post_key in request.POST:
                        note = request.POST[note_post_key]
                    
                    record_compounds(article, request.POST[soln_name], ["", "", "", ""], "%s_0" % soln, user)
                    cont_value_ob = m.ContValue.objects.get_or_create(mean = 5, stdev = None,
                                                                      stderr = None, min_range = None,
                                                                      max_range = None, n = None)[0]
                    metadata_ob = m.MetaData.objects.get_or_create(name = soln_name, cont_value = cont_value_ob)[0]
                    
                    update_amd_obj(article, metadata_ob, m.ReferenceText.objects.get_or_create(text = request.POST[soln_name])[0], user, note)
                else:
                    m.ArticleMetaDataMap.objects.filter(article = article, metadata__name = soln_name).delete()
                    m.ArticleMetaDataMap.objects.filter(article = article, metadata__name__icontains = "%s_0" % soln).delete()
                    
        # if no full text object in DB, create one
        aft = m.ArticleFullText.objects.get_or_create(article=article)[0]
        afts = m.ArticleFullTextStat.objects.get_or_create(article_full_text = aft)[0]

        # note that the article metadata has now been checked and validated by a human
        afts.metadata_human_assigned = True

        # now process metadata needs curation and notes fields
        if 'NeedsExpert' in request.POST:
            if 'Expert' in request.POST['NeedsExpert']:
                afts.metadata_needs_expert = True
        else:
            afts.metadata_needs_expert = False
        if 'MetadataNote' in request.POST:
            if len(request.POST['MetadataNote']) > 0:
                afts.metadata_curation_note = request.POST['MetadataNote']
            else:
                afts.metadata_curation_note = None

        afts.save()

    # send methods section if we can identify it
    if article.get_full_text_stat():
        if article.get_full_text_stat().methods_tag_found:
            methods_html = getMethodsTag(article.get_full_text().get_content(), article)
            methods_html = str(methods_html)
        else:
            methods_html = None
    else:
        methods_html = None

    # populate initial form fields
    metadata_list = m.MetaData.objects.filter(articlemetadatamap__article = article).distinct()
    amdms = m.ArticleMetaDataMap.objects.filter(article = article)
    initialFormDict = {}
    for md in metadata_list:
        if md.value:
            if md.name in initialFormDict:
                initialFormDict[md.name].append(unicode(md.id))
            else:
                initialFormDict[md.name] = [unicode(md.id)]
        else:
            if md.name == "ExternalSolution" or md.name == "InternalSolution":
                for amdm in amdms:
                    if amdm.metadata.name == md.name and amdm.ref_text:
                        initialFormDict[md.name] = amdm.ref_text.text
            else:
                initialFormDict[md.name] = unicode(md.cont_value)
   
    # set notes fields
    for amdm in amdms:
        if amdm.note:
            initialFormDict[amdm.metadata.name + 'Note'] = unicode(amdm.note)

    # set needs expert and general note fields
    if article.get_full_text_stat():
        afts = article.get_full_text_stat()
        general_note = afts.metadata_curation_note
        if general_note:
            initialFormDict['MetadataNote'] = unicode(general_note)
        needs_expert = afts.metadata_needs_expert
        needs_peer_review = afts.metadata_needs_peer_review
        if needs_expert or needs_peer_review:
            initialFormDict['NeedsExpert'] = []
        if needs_expert:
            initialFormDict['NeedsExpert'].append('Expert')

    returnDict = {'article': article, 'metadata_list': metadata_list, 'methods_html': methods_html}
    returnDict['form'] = ArticleMetadataForm(initial = initialFormDict)

    return render('neuroelectro/article_metadata.html', returnDict, request)


def data_table_detail(request, data_table_id):
    ordinal_list_names = ['Species', 'Strain', 'ElectrodeType', 'PrepType', 'JxnPotential']
    cont_list_names = ['AnimalAge', 'AnimalWeight', 'RecTemp', 'NumObs']
    datatable = get_object_or_404(m.DataTable, pk=data_table_id)
    user = request.user
    if request.method == 'POST':
        # Process the curated data and save it in the database
        if 'curation_form_name' in request.POST:
            dsOb = m.DataSource.objects.get(data_table = datatable)
            ecmObs = datatable.datasource_set.all()[0].ephysconceptmap_set.all()
            ncmObs = datatable.datasource_set.all()[0].neuronconceptmap_set.all()
            nedmObs = datatable.datasource_set.all()[0].neuronephysdatamap_set.all()
            efcmObs = datatable.datasource_set.all()[0].expfactconceptmap_set.all()
            
            matchingNeuronDTIds = [ncm.dt_id for ncm in ncmObs]
            matchingEphysDTIds = [ecm.dt_id for ecm in ecmObs]
            matchingMetaDTIds = [efcm.dt_id for efcm in efcmObs]
            
            # If we decide to annotate individual cells in tables - we will need this
            #matchingDataValIds = [nedm.dt_id for nedm in nedmObs]
            
            # In the post we have a dictionary of name: value pairs from the curation form
            for key, value in request.POST.iteritems():
                # The code relies on keys consisting of th-digits or td-digits 
                cell_id = re.search('(td|th)-\d+', key)
                
                # If not a curation field - continue to the next request.POST line
                if not cell_id:
                    continue
                
                cell_id = cell_id.group(0)
                ephys_note = request.POST['ephys_note_%s' % cell_id] if 'ephys_note_%s' % cell_id in request.POST else None
                neuron_note = request.POST['neuron_note_%s' % cell_id] if 'neuron_note_%s' % cell_id in request.POST else None
                # get ref_text from datatable based on cell_id
                #ref_text = request.POST['ref_text_%s' % cell_id]
                ref_text = BeautifulSoup(datatable.table_html).find(id = cell_id).text
                identified_unit = get_units_from_table_header(ref_text)
                
                # Create or update ephys property
                if 'ephys_dropdown' in key:
                    ephys_prop_ob = m.EphysProp.objects.get(name = value)
                    
                    # create new ecm object if not in annotated list
                    if cell_id not in matchingEphysDTIds:
                        ecmOb = m.EphysConceptMap.objects.create(
                            ref_text = ref_text,
                            ephys_prop = ephys_prop_ob,
                            source = dsOb,
                            dt_id = cell_id,
                            changed_by = user,
                            note = ephys_note,
                            identified_unit = identified_unit)
                    else:
                        # if already annotated - update
                        ecmOb = ecmObs[matchingEphysDTIds.index(cell_id)]
                        ecmOb.ephys_prop = ephys_prop_ob
                        ecmOb.changed_by = user
                        ecmOb.note = ephys_note
                        ecmOb.identified_unit = identified_unit
                        ecmOb.save()
                    
                    # Log the change
                    with open(settings.OUTPUT_FILES_DIRECTORY + 'curation_log.txt', 'a+') as f:
                        f.write(("%s\t%s\tDataTable: %s,%s\tAdded/Modified EphysProp concept: '%s' for text '%s'\tNote: '%s'\n" % 
                                 (strftime("%Y-%m-%d %H:%M:%S"), user, data_table_id, cell_id, ecmOb.ephys_prop.name, ecmOb.ref_text, ephys_note)).encode('utf8'))
                
                # Create or update neuron type        
                if 'neuron_dropdown' in key:
                    neuron_ob = m.Neuron.objects.get(name = value)
                    neuron_long_name = request.POST.get('neuron_long_name_%s' % cell_id)
                    
                    #create new ncm object if not in annotated list
                    if cell_id not in matchingNeuronDTIds:
                        ncmOb = m.NeuronConceptMap.objects.create(ref_text = ref_text,
                                                                      neuron = neuron_ob,
                                                                      source = dsOb,
                                                                      dt_id = cell_id,
                                                                      changed_by = user,
                                                                      note = neuron_note,
                                                                      neuron_long_name = neuron_long_name)
                    else:
                        # if already annotated - update
                        ncmOb = ncmObs[matchingNeuronDTIds.index(cell_id)]
                        ncmOb.neuron = neuron_ob
                        ncmOb.neuron_long_name = neuron_long_name  
                        ncmOb.changed_by = user 
                        ncmOb.note = neuron_note
                        ncmOb.save()
                        
                    # Log the change
                    with open(settings.OUTPUT_FILES_DIRECTORY + 'curation_log.txt', 'a+') as f:
                        f.write(("%s\t%s\tDataTable: %s,%s\tAdded/Modified Neuron concept: '%s'\tLongName: '%s'\tfor text: '%s'\tNote: '%s'\n" % 
                            (strftime("%Y-%m-%d %H:%M:%S"), user, data_table_id, cell_id, ncmOb.neuron.name, neuron_long_name, ncmOb.ref_text, neuron_note)).encode('utf8'))
                
                # Create or update metadata (experimental factor)
                if "meta_dropdown" in key:
                    metadata_name = key.replace("meta_dropdown_" + cell_id + "_", "")
                    metadata_value = request.POST.get('meta_value_' + cell_id + "_" + metadata_name)
                    metadata_note = request.POST.get('meta_note_' + cell_id + "_" + metadata_name) if 'meta_note_' + cell_id + "_" + metadata_name in request.POST else None

                    if metadata_value == "None":
                        for efcmOb in efcmObs:
                            if efcmOb.dt_id == cell_id and efcmOb.metadata.name == metadata_name:
                                efcmOb.delete()
                        continue

                    if metadata_name in cont_list_names:
                        
                        retDict = resolve_data_float(metadata_value, initialize_dict=True)
                        if retDict:
                            cont_value_ob = m.ContValue.objects.get_or_create(mean = retDict['value'], min_range = retDict['min_range'],
                                                                              max_range = retDict['max_range'], stderr = retDict['error'])[0]
                            metadata_ob = m.MetaData.objects.get_or_create(name = metadata_name, cont_value = cont_value_ob)[0]
                        else:
                            # TODO : check if this ever gets called
                            cont_value_ob = m.ContValue.objects.get_or_create(mean = float(metadata_value))[0]
                            metadata_ob = m.MetaData.objects.get_or_create(name = metadata_name, cont_value = cont_value_ob)[0]
                            
                    elif metadata_name in ordinal_list_names:
                        metadata_ob = m.MetaData.objects.get(name = metadata_name, value = metadata_value)
                        
                    else:
                        print "Unknown metadata type reported: %s with value: %s" % (metadata_name, metadata_value)
                        continue
                           
                    # Try saving the efcmOb - if it fails create a new one 
                    try:
                        # if efcmOb exists- update it
                        efcmOb = m.ExpFactConceptMap.objects.get(source = dsOb, dt_id = cell_id, metadata__name = metadata_name)
                        if efcmOb.metadata != metadata_ob:
                            efcmOb.metadata = metadata_ob
                            efcmOb.changed_by = user
                            efcmOb.note = metadata_note
                            efcmOb.save()
                        if efcmOb.note != metadata_note:
                            efcmOb.note = metadata_note
                            efcmOb.save()
                    except ObjectDoesNotExist:
                        # if efcmOb doesn't exist - create one
                        efcmOb = m.ExpFactConceptMap.objects.create(ref_text = ref_text,
                                                                        metadata = metadata_ob,
                                                                        source = dsOb,
                                                                        dt_id = cell_id,
                                                                        note = metadata_note,
                                                                        changed_by = user)

                    # Log the change
                    with open(settings.OUTPUT_FILES_DIRECTORY + 'curation_log.txt', 'a+') as f:
                        f.write(("%s\t%s\tDataTable: %s,%s\tAdded/Modified Exp Fact concept: '%s, %s' from text: '%s'\tNote: '%s'\n" % 
                            (strftime("%Y-%m-%d %H:%M:%S"), user, data_table_id, cell_id, efcmOb.metadata.name, metadata_value, efcmOb.ref_text, metadata_note)).encode('utf8'))
                    
                if 'delete_' in key:
                    if cell_id in matchingEphysDTIds:
                        ecmOb = ecmObs[matchingEphysDTIds.index(cell_id)]

                        with open(settings.OUTPUT_FILES_DIRECTORY + 'curation_log.txt', 'a+') as f:
                            f.write(("%s\t%s\tDataTable: %s,%s\tDeleted EphysProp concept: '%s' from text '%s'\tNote: '%s'\n" % 
                                 (strftime("%Y-%m-%d %H:%M:%S"), user, data_table_id, cell_id, ecmOb.ephys_prop.name, ecmOb.ref_text, ephys_note)).encode('utf8'))

                        ecmOb.delete()
                        
                    if cell_id in matchingNeuronDTIds:
                        ncmOb = ncmObs[matchingNeuronDTIds.index(cell_id)]
                        
                        with open(settings.OUTPUT_FILES_DIRECTORY + 'curation_log.txt', 'a+') as f:
                            f.write(("%s\t%s\tDataTable: %s,%s\tDeleted Neuron concept: '%s' from text: '%s'\tNote: '%s'\n" % 
                                 (strftime("%Y-%m-%d %H:%M:%S"), user, data_table_id, cell_id, ncmOb.neuron.name, ncmOb.ref_text, neuron_note)).encode('utf8'))
                        
                        ncmOb.delete()
                        
                    if cell_id in matchingMetaDTIds:
                        for efcmOb in efcmObs:
                            if efcmOb.dt_id == cell_id:
                                efcmOb.delete()
                                
                        with open(settings.OUTPUT_FILES_DIRECTORY + 'curation_log.txt', 'a+') as f:
                            f.write(("%s\t%s\tDataTable: %s,%s\tDeleted Exp Fact concept: '%s' from text: '%s'\n" % 
                                     (strftime("%Y-%m-%d %H:%M:%S"), user, data_table_id, cell_id, efcmOb.metadata.name, efcmOb.ref_text)).encode('utf8'))
                        
            # Create and remove the nedms as needed
            assign_data_vals_to_table(datatable, user)

        # process output from check boxes
        if 'validate_all' in request.POST:

            ecmObs = datatable.datasource_set.all()[0].ephysconceptmap_set.all()
            ncmObs = datatable.datasource_set.all()[0].neuronconceptmap_set.all()
            nedmObs = datatable.datasource_set.all()[0].neuronephysdatamap_set.all()
            #
            #neurons = m.Neuron.objects.filter(neuronconceptmap__in = ncmObs)
            for nedm in nedmObs:
                # normalize nedm
                normalized_dict = normalize_nedm_val(nedm)
                if not nedm.val_norm and normalized_dict['value']:
                    nedm.val_norm = normalized_dict['value']
                    nedm.err_norm = normalized_dict['error']

                nedm.times_validated += 1
                nedm.changed_by = user
                nedm.save()
            for e in ecmObs:
                e.times_validated += 1
                e.changed_by = user
                e.save()
            for ncm in ncmObs:
                ncm.times_validated += 1
                ncm.changed_by = user
                ncm.save()
            for efcm in efcmObs:
                efcm.times_validated += 1
                efcm.changed_by = user
                efcm.save()

        elif 'remove_all' in request.POST:
            ecmObs.delete()
            ncmObs.delete()
            nedmObs.delete()
        if 'expert' in request.POST:
            datatable.needs_expert = True
        else:
            datatable.needs_expert = False
        if 'complex_neurons' in request.POST:
            datatable.complex_neurons = True
        else:
            datatable.complex_neurons = False
        if 'irrelevant_flag' in request.POST:
            datatable.irrelevant_flag = True
        else:
            datatable.irrelevant_flag = False
        if 'data_table_note' in request.POST:
            note = request.POST['data_table_note'] 
            if len(note) > 0:
                datatable.note = note
            else:
                datatable.note = None
        datatable.save()

        # this calculates summary fields and then normalizes nedm values
        #computeNeuronEphysSummary(ncmObs, ecmObs, nedmObs)
        #computeArticleSummaries(datatable.article)

    nedm_list = datatable.datasource_set.all()[0].neuronephysdatamap_set.all()
    ecmObs = datatable.datasource_set.all()[0].ephysconceptmap_set.all()
    ncmObs = datatable.datasource_set.all()[0].neuronconceptmap_set.all()
    #inferred_neurons = list(set([str(nel.neuron.name) for nel in nel_list]))

    meta_all = dict()
    for metadata in m.MetaData.objects.all().order_by('name'):
        if metadata.name in ordinal_list_names:
            if metadata.name in meta_all.keys() and metadata.value not in meta_all[metadata.name]:
                meta_all[metadata.name].append(metadata.value)
            elif metadata.name not in meta_all.keys():
                meta_all[metadata.name] = [metadata.value]
            
    for metadata_name in cont_list_names:
        meta_all[metadata_name] = None
    
    efcmObs = datatable.datasource_set.all()[0].expfactconceptmap_set.all()

    if request.user.is_authenticated():
        # TODO: call these from database directly
        names_helper_text = {'AnimalAge' : '(days, e.g. 5-10; P46-P94)',
                             'AnimalWeight' : '(grams, e.g. 150-200)', 
                             'RecTemp' : '(degree C, e.g. 33-45)'}
        
        returnDict = {'datatable': datatable, 'nedm_list': nedm_list,
                        'enriched_html_table': str(BeautifulSoup(datatable.table_html)).replace('##160;', ''), 
                        'ecm_list': ecmObs,
                        'ncm_list': ncmObs,
                        'meta_list': efcmObs,
                        'ephys_all': m.EphysProp.objects.all().order_by('name'),
                        'neuron_all': m.Neuron.objects.all().order_by('name'),
                        'meta_all': meta_all,
                        'meta_helper': names_helper_text
                     }  
        if datatable.note:
            returnDict['data_table_note'] = datatable.note
        return render('neuroelectro/data_table_detail_validate.html', returnDict, request)
    # If user is not authenticated - show the curations but no curator functionality will be present
    else:
        returnDict = {'datatable': datatable, 'nedm_list': nedm_list,
                        'enriched_html_table': str(BeautifulSoup(datatable.table_html)).replace('##160;', ''), 
                        'ecm_list': ecmObs,
                        'ncm_list': ncmObs,
                        'meta_list': efcmObs
                     }      
        return render('neuroelectro/data_table_detail.html', returnDict, request)


def data_table_detail_no_annotation(request, data_table_id):
    datatable = get_object_or_404(m.DataTable, pk=data_table_id)
    returnDict = {'datatable': datatable}      
    return render('neuroelectro/data_table_detail_no_annotation.html', returnDict, request)
    
def contact_info(request):
    return render('neuroelectro/contact_info.html', {}, request)
    
def data_table_validate_example(request):
    return render('neuroelectro/data_table_validate_example.html', {}, request)

def faqs(request):
    return render('neuroelectro/faqs.html', {}, request)
    
def api(request):
    return render('neuroelectro/api.html', {}, request)

def api_docs(request):
    return render('neuroelectro/api_docs.html', {}, request)
    
def contribute(request):
    curator_list = m.User.objects.filter(assigned_neurons__isnull = False).distinct()
    returnDict = {'curator_list': curator_list}  
    return render('neuroelectro/contribute.html', returnDict, request)

def publications(request):
    return render('neuroelectro/publications.html', {}, request)

# function to add electrophys data tagged to a specific publication
@login_required
def neuron_data_add(request):
    neuron_list = m.Neuron.objects.order_by('name')
    ephys_prop_list = m.EphysProp.objects.order_by('name')
    
    def neurondata_callback(field):
        if field.name == 'neuron_name':
            return forms.ChoiceField(
                          label = 'Neuron type',
                          choices =  [ (n.name, n.name) for n in neuron_list],
                          widget = forms.Select(attrs = {'class':'selector'})) 
    
    def ephysprop_callback(field):
        if field.name == 'ephys_name':
            return forms.ChoiceField(
                          label = "Ephys name",
                          choices=[ (ep.name, ep.name) for ep in ephys_prop_list ],
                          widget = forms.Select(attrs = {'class':'selector'}))
        if field.name == 'ephys_value':
            return forms.CharField(
                          label = 'Ephys value: ',
                          required = True,
                          initial = "A ± B (C)")
        return field.formfield()

    EphysPropFormSet = inlineformset_factory(m.NeuronData, m.EphysProperty, extra=1, formfield_callback = ephysprop_callback, exclude = ('',))

    class BaseNeuronFormSet(BaseInlineFormSet):
        def add_fields(self, form, index):
            super(BaseNeuronFormSet, self).add_fields(form, index)
            
            try:
                instance = self.get_queryset()[index]
                pk_value = instance.pk
            except IndexError:
                instance = None
                pk_value = hash(form.prefix)
            
            form.nested = [
                EphysPropFormSet(data = self.data if self.data and index is not None else None,
                                instance = instance,
                                prefix = 'EPHYS_PROP_%s' % pk_value)]
            
        def is_valid(self):
            result = super(BaseNeuronFormSet, self).is_valid()
            
            return result
        
        def save_new(self, form, commit=False):
            instance = super(BaseNeuronFormSet, self).save_new(form, commit=commit)
            form.instance = instance
            
            for nested in form.nested:
                nested.instance = instance
                
                for cleandata in nested.cleaned_data:
                    cleandata[nested.fk.name] = instance
                    
            return instance
        
        def should_delete(self, form):
            if self.can_delete:
                raw_delete_value = form._raw_value(DELETION_FIELD_NAME)
                should_delete = form.fields(DELETION_FIELD_NAME).clean(raw_delete_value)
                return should_delete
            
            return False
        
        def save_all(self, commit=False):
            objects = self.save(commit=False)
            
            if commit:
                for o in objects:
                    o.save()
                    
            if not commit:
                self.save_m2m()
                
            for form in set(self.initial_forms + self.saved_forms):
                if self.should_delete(form):
                    continue
                
                for nested in form.nested:
                    nested.save(commit=commit)        
        
    NeuronDataFormSet = inlineformset_factory(m.NeuronDataAddMain, m.NeuronData, formset=BaseNeuronFormSet, extra=1, formfield_callback = neurondata_callback, exclude = ('',))
    
    if request.POST:
        neuron_data_formset = NeuronDataFormSet(request.POST, prefix='neurondata')
        
        if neuron_data_formset.is_valid():
            pubmed_id = request.POST["pubmed_id"]
            
            dictOfPrefixes = {}
            data = neuron_data_formset.data
            
            for (key, value) in data.items():
                if re.match('EPHYS_PROP_\d+$', key.encode('ascii','ignore')) is not None:
                    dictOfPrefixes[key.encode('ascii','ignore')] = value.encode('ascii','ignore')
            
            neuron_type_list = []
            ephys_prop_list = []                    
            for (ephys_prefix, neuron_index) in dictOfPrefixes.items():
                neuron_name = data[neuron_index + "-neuron_name"]
                neuron_ob = m.Neuron.objects.filter(name = neuron_name)[0]
                neuron_type_list.append(neuron_ob)

                for i in range(int(data[ephys_prefix + "-TOTAL_FORMS"])):
                    ephys_name = data[ephys_prefix + "-" + str(i) + "-ephys_name"]
                    ephys_value = data[ephys_prefix + "-" + str(i) + "-ephys_value"]

                    ephys_prop_ob = m.EphysProp.objects.filter(name = ephys_name)[0]
                    ephys_prop_list.append(ephys_prop_ob)
                    
                    try:
                        add_ephys_nedm.add_ephys_nedm(ephys_name, ephys_value, pubmed_id, neuron_name, request.user) 
                    except:
                        error_text = "An exception has occurred while attempting to write neuron data: Pubmed id: %s, Neuron name: %s, Ephys. name: %s, Ephys. value: %s, User: %s" % (pubmed_id, neuron_name, ephys_name, ephys_value, request.user)
                        return TemplateResponse('neuroelectro/redirect_template.html', { 'redirect_url':'/contribute/', 'alert_before_redirect': error_text }, request)
                        
            article = get_object_or_404(m.Article, pmid = pubmed_id)

            # update article summary model object
            # SJT NOTE - note updating neuron or ephys summaries because they take too long
            computeArticleSummaries(article)
            computeNeuronEphysSummariesAll(neuron_type_list, ephys_prop_list)
            #computeNeuronSummaries(neuron_type_list)
            #computeEphysPropSummaries(ephys_prop_list)
            
            # mail admins for notification of data addition
            message = 'user %s added data for %s \nfrom %s' % (request.user, neuron_type_list, article.title)
            subject = 'User %s added data to NeuroElectro' % request.user
            mail_admins(subject, message)

            return TemplateResponse('neuroelectro/redirect_template.html', { 'redirect_url':'/article/' + str(article.pk), 'alert_before_redirect': 'Neuron data was submitted successfully! You will now be redirected to the page that contains your contribution' }, request)
    else:
        neuron_data_formset = NeuronDataFormSet(prefix='neurondata')
    
    c = { 'neuron_data_formset': neuron_data_formset, 'entrez_ajax_api_key': settings.ENTREZ_AJAX_API_KEY }
    c.update(csrf(request))
    
    return render('neuroelectro/neuron_data_add.html', c, request)

def neuron_article_suggest(request, neuron_id):
    n = get_object_or_404(m.Neuron, pk=neuron_id)
    context_instance=RequestContext(request)
    csrf_token = context_instance.get('csrf_token', '')
    returnDict = {'token' : csrf_token, 'neuron': n, 'entrez_ajax_api_key': settings.ENTREZ_AJAX_API_KEY }
    return render('neuroelectro/neuron_article_suggest.html', returnDict, request)

def neuron_article_suggest_post(request, neuron_id):
    if not request.POST:
        output_message = 'article not post!'
        message = {}
        message['response'] = output_message
        return HttpResponse(json.dumps(message), mimetype='application/json')
    n = get_object_or_404(m.Neuron, pk=neuron_id)
    if request.user.is_anonymous():
        user = m.get_anon_user()
    else:
        user = request.user
    pmid = request.POST['pmid']
    # is article in db?
    articleQuery = m.Article.objects.filter(pmid = pmid)
    if len(articleQuery) == 0:
        article = add_single_article(pmid)
        #a.suggester.add(user)
        # assign suggester here
    else:
        article = articleQuery[0]
        #a.suggester.add(user)
    nam = m.NeuronArticleMap.objects.get_or_create(neuron=n, article = article)[0]
    nam.added_by = user
    nam.save()

    # stuff to send email to site admins
    subject = 'Suggested article to %s neuron in NeuroElectro' % (n.name)
    pmid_link = 'http://www.ncbi.nlm.nih.gov/pubmed/%s' % pmid
    email_message = 'Neuron name: %s \nArticle Title: %s \nPubmed Link: %s \nUser: %s \n' % (n.name, article.title, pmid_link, user)
    output_message = 'article suggested!'
    try:
        mail_admins(subject, email_message)
    except BadHeaderError:
        output_message = "Please make sure all fields are filled out"
    message = {}
    message['response'] = output_message
    return HttpResponse(json.dumps(message), mimetype='application/json')

def article_suggest(request):
    context_instance=RequestContext(request)
    csrf_token = context_instance.get('csrf_token', '')
    returnDict = {'token' : csrf_token, 'entrez_ajax_api_key': settings.ENTREZ_AJAX_API_KEY }
    return render('neuroelectro/article_suggest.html', returnDict, request)

def article_suggest_post(request):
    if not request.POST:
        output_message = 'article not post!'
        message = {}
        message['response'] = output_message
        return HttpResponse(json.dumps(message), mimetype='application/json')
    if request.user.is_anonymous():
        user = m.get_anon_user()
    else:
        user = request.user
    pmid = request.POST['pmid']
    # is article in db?
    articleQuery = m.Article.objects.filter(pmid = pmid)
    if len(articleQuery) == 0:
        article = add_single_article(pmid)
    else:
        article = articleQuery[0]

    # stuff to send email to site admins
    subject = 'Suggested article to NeuroElectro'
    pmid_link = 'http://www.ncbi.nlm.nih.gov/pubmed/%s' % pmid
    email_message = 'Article Title: %s \nPubmed Link: %s \nUser: %s \n' % (article.title, pmid_link, user)
    output_message = 'article suggested!'
    try:
        mail_admins(subject, email_message)
    except BadHeaderError:
        output_message = "Please make sure all fields are filled out"
        
    message = {}
    message['response'] = output_message
    return HttpResponse(json.dumps(message), mimetype='application/json')


@login_required
def full_text_upload(request):
    if request.method == 'POST':
        print request

        #print request.FILES['table_file']
        article_form = ArticleFullTextUploadForm(request.POST, request.FILES)
        print article_form.is_valid()
        if article_form.is_valid():
            f = request.FILES['full_text_file']
            pmid_str = request.POST['pmid']
            path = default_storage.save('tmp/%s' % f.name, ContentFile(f.read()))
            tmp_file_path = os.path.join(settings.MEDIA_ROOT, path)
            #path = f.temporary_file_path()
            article_ob = add_single_full_text(tmp_file_path, pmid_str, require_mined_ephys = False, require_sections = False)
            if article_ob:
                parse_success = True
                article_ob_pk = article_ob.pk
                response_message = 'Article adding succeeded!'
            else:
                response_message = 'Something failed in the article adding'
                article_ob_pk = None
    else:
        article_form = ArticleFullTextUploadForm()
        article_ob_pk = None
        response_message = 'No article added yet'

    # on post
    # do text mining on uploaded full text file if it's provided
    # associate uploaded table to
    # context_instance=RequestContext(request)
    # csrf_token = context_instance.get('csrf_token', '')
    # returnDict = {'token' : csrf_token, 'entrez_ajax_api_key': settings.ENTREZ_AJAX_API_KEY }
    return_dict = {'article_form': article_form, 'article_pk': article_ob_pk, 'response_message' : response_message}
    return render('neuroelectro/full_text_upload.html', return_dict, request)


@login_required
def data_table_upload(request):
    if request.method == 'POST':

        table_form = DataTableUploadForm(request.POST, request.FILES)
        if table_form.is_valid():
            f = request.FILES['table_file']

            pmid = request.POST['pmid']
            table_name = request.POST['table_name']
            table_title = request.POST['table_title']
            table_legend = request.POST['table_legend']
            associated_text = request.POST['associated_text']
            user = request.user

            article_query = m.Article.objects.filter(pmid = pmid)
            if article_query:
                a = article_query[0]
                table_html = process_uploaded_table(f, table_name, table_title, table_legend, associated_text)

                table_ob = add_table_ob_to_article(table_html, a, text_mine = True, uploading_user = user)
                if table_ob:
                    parse_success = True
                    table_ob_pk = table_ob.pk
                    response_message = 'Table parsing succeeded!'
                else:
                    response_message = 'Something failed in the table parsing'
                    table_ob_pk = None
    else:
        table_form = DataTableUploadForm()
        table_ob_pk = None
        response_message = 'No table uploaded'

    return_dict = {'table_form': table_form, 'response_message' : response_message, 'table_pk' : table_ob_pk}
    return render('neuroelectro/data_table_upload.html', return_dict, request)


#This function really sucks @SuppressWarnings
def neuron_article_curate_list(request, neuron_id):
    n = get_object_or_404(m.Neuron, pk=neuron_id)
    min_mentions_nam_1 = 20
    min_mentions_nam_2 = 3
#     max_un_articles = 50
    articles_ex = m.Article.objects.filter(datatable__datasource__neuronconceptmap__neuron = n, datatable__datasource__neuronephysdatamap__isnull = False).distinct()
    for art in articles_ex:
        dts = m.DataTable.objects.filter(article = art, datasource__ephysconceptmap__isnull = False).distinct()
        art.datatables = dts
#     robot_user = get_robot_user()
    # articles_robot = m.Article.objects.filter(Q(neuronarticlemap__neuron = n, 
    #     neuronarticlemap__num_mentions__gte = min_mentions_nam, 
    #     datatable__datasource__neuronephysdatamap__isnull = True,
    #     datatable__datasource__ephysconceptmap__isnull = False)).distinct()
    articles_robot = m.Article.objects.filter(Q(neuronarticlemap__neuron = n, 
        neuronarticlemap__num_mentions__gte = min_mentions_nam_1)).distinct()
        # metadata__name = 'ElectrodeType')
    if articles_robot.count() < 5:
        articles_robot = m.Article.objects.filter(Q(neuronarticlemap__neuron = n, 
            neuronarticlemap__num_mentions__gte = min_mentions_nam_2)).distinct()
            # metadata__name = 'ElectrodeType')
    articles_robot.exclude(datatable__datasource__neuronconceptmap__times_validated__gte = 1)
#     articles_human = m.Article.objects.filter(Q(neuronarticlemap__neuron = n,  
#         datatable__datasource__neuronephysdatamap__isnull = True)).exclude(neuronarticlemap__added_by=robot_user).distinct()
    # articles_un = set(articles_robot).difference(set(articles_human) )
    articles_un = articles_robot.exclude(pk__in = articles_ex)
    # articles_un = articles_human.exclude(pk__in = articles_robot)
    # if articles_un.count() > max_un_articles:
    #     articles_un = articles_un[0:max_un_articles]
    # annotate(num_mentions = Count('neuronarticlemap__neuron = n, neuronarticlemap__num_mentions'))
    for art in articles_un:
        # dts = DataTable.objects.filter(article = art, datasource__ephysconceptmap__isnull = False).distinct()
        dts = m.DataTable.objects.filter(article = art).distinct()
        dts = dts.annotate(num_unique_ephys = Count('datasource__ephysconceptmap__ephys_prop__id'))
        dts = dts.filter(num_unique_ephys__gte = 2)
        #dts = DataTable.objects.filter(article = art).distinct()
        art.datatables = dts
        nam = m.NeuronArticleMap.objects.filter(article = art, neuron = n)[0]
        art.neuron_mentions = nam.num_mentions
        if art.neuron_mentions is None:
            art.neuron_mentions = 0
        #art.how_added = '%s %s' % (nam.added_by.first_name, nam.added_by.last_name)
        if nam.added_by:
            art.how_added = '%s %s' % (nam.added_by.first_name, nam.added_by.last_name)
        else:
            art.how_added = 'Anon'
    #articles_un = articles_un.order_by('-neuron_mentions')
    returnDict = {'articles_ex':articles_ex, 'articles_un':articles_un, 'neuron': n}
    return render('neuroelectro/neuron_article_curate_list.html', returnDict, request)
    
def neuron_curator_ask(request, neuron_id):
    n = get_object_or_404(m.Neuron, pk=neuron_id)
    returnDict = {'neuron': n}
    return render('neuroelectro/neuron_curator_ask.html', returnDict, request)

@login_required
def neuron_become_curator(request, neuron_id):
    n = get_object_or_404(m.Neuron, pk=neuron_id)
    user = request.user
    user_inst_default = ''
    if user.institution:
        user_inst_default = user.institution.name
    if request.POST:
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
            i = m.Institution.objects.get_or_create(name = institution)[0]
            user.institution = i
            user.save()

            # stuff to send email to site admins
            subject = 'User %s curating %s neuron in NeuroElectro' % (user.last_name, n.name)
            message = 'User: %s, \nNeuron:%s' % (user, n.name)
            try:
                mail_admins(subject, message)
            except BadHeaderError:
                legend = "Please make sure all fields are filled out"
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
    return render('neuroelectro/neuron_become_curator.html', returnDict, request)


@login_required
def neuron_name_conversion(request):
    if request.POST:
        if 'NeuronName' in request.POST:
            neuron_name = request.POST['NeuronName'].strip()
            try:
                sherlok_instance = Sherlok('neuroner')
                r = sherlok_instance.annotate(neuron_name)
                annot_dict = clean_annotations(r.annotations, neuron_name, return_dict = True)
                #annot_list = normalize_annots(al, shorten = False)
                # if check_strain(neuron_name):
                #     al.append(check_strain(neuron_name))

                annot_dict = annot_dict
                query = neuron_name
            except ConnectionError:
                query = 'No Connection to Sherlok on server!'
                annot_dict = ''
    else:
        annot_dict = ''
        query = ''
    returnDict = {'annot_dict' : annot_dict, 'neuron_query' : query}
    returnDict['form'] = NeuronConversionForm
    return render('neuroelectro/neuron_name_conversion.html', returnDict, request)


@login_required
def neuron_search(request):
    if request.POST:
        if 'NeuronName' in request.POST:
            neuron_name = request.POST['NeuronName'].strip()
            try:
                sherlok_instance = Sherlok('neuroner')
                r = sherlok_instance.annotate(neuron_name)
                #annot_dict = clean_annotations(r.annotations, neuron_name, return_dict = True)
                annot_list = clean_annotations(r.annotations)
                #annot_list = normalize_annots(al, shorten = False)
                # if check_strain(neuron_name):
                #     al.append(check_strain(neuron_name))

                query = neuron_name
            except ConnectionError:
                query = 'No Connection to Sherlok on server!'
                annot_dict = ''

            concept_maps = m.NeuronConceptMap.objects.filter(times_validated__gte = 0)
            concept_maps = concept_maps.exclude(source__data_table__irrelevant_flag = True)

            concept_maps = list(concept_maps)
            KEEP_THRESHOLD = .3
            keep_concept_maps = []
            for cm in concept_maps:
                neuroner_annots = cm.get_neuroner()
                cm.sim_value = calculate_neuroner_similarity(annot_list,neuroner_annots, symmetric = False, use_inter_similarity = False)
                if cm.sim_value > KEEP_THRESHOLD:
                    keep_concept_maps.append(cm)

            concept_maps = keep_concept_maps
            #concept_maps = concept_maps.filter(sim_value__gte = .3).order_by('-sim_value')
            #concept_maps.order_by('-sim_value')
    else:
        annot_list = ''
        query = ''
        concept_maps = []

    returnDict = {'annot_list' : annot_list, 'neuron_query' : query, 'concept_maps': concept_maps}
    returnDict['form'] = NeuronConversionForm
    return render('neuroelectro/neuron_search.html', returnDict, request)


def nlex_neuron_id_list(request):
    neurons = m.Neuron.objects.filter(nlex_id__isnull = False)
    neurons = neurons.filter(neuronsummary__num_articles__gte = 1)
    outStr = ''
    for n in neurons:
        outStr += '%s,%s,%s' % (n.nlex_id, n.id, n.name)
        outStr += '<br>'
    return render('neuroelectro/nlex_neuron_id_list.html', {'display_str': outStr}, request)
    
def ephys_prop_ontology(request):
    ephys_prop_list = get_ephys_prop_ordered_list()
    returnDict = {'ephys_prop_list': ephys_prop_list}
    return render('neuroelectro/ephys_prop_ontology.html', returnDict, request)
    
def concept_map_to_validate_list(request):
    concept_maps = m.NeuronConceptMap.objects.filter(times_validated__gte = 0)
    concept_maps = concept_maps.exclude(source__data_table__irrelevant_flag = True)
    REMOVE_ROBOT_ADDED = True
    exclude_pks = []
    new_cm_list = []
    for cm in concept_maps:
        curated_list = [hcm.changed_by for hcm in cm.history.all()]
        curated_list = [x[0] for x in groupby(curated_list)]
        curated_list = [unicode(c) for c in curated_list]
        cm.curated_list = '; '.join(curated_list)
        if REMOVE_ROBOT_ADDED and cm.curated_list == u'robot ':
            exclude_pks.append(cm.pk)
            continue
        article = cm.get_article()
        if article.get_full_text_stat():
            cm.metadata_human_assigned = article.get_full_text_stat().metadata_human_assigned
        else:
            cm.metadata_human_assigned = False
        #cm.neuroner_id_str = cm.get_neuroner()
        new_cm_list.append(cm)
    return render('neuroelectro/concept_map_to_validate_list.html', {'concept_maps': new_cm_list}, request)
    
def data_table_to_validate_list(request):
    dts = m.DataTable.objects.all()
    # dts = DataTable.objects.exclude(needs_expert = True)
    # dts = dts.filter(datasource__ephysconceptmap__isnull = False, datasource__neuronconceptmap__isnull = False)
    
    dts = dts.filter(datasource__ephysconceptmap__isnull = False)
    #dts = dts.filter(article__articlemetadatamap__metadata__value__in = valid_species).distinct()
    
    #dts = dts.exclude(needs_expert = True)
    
    dts = dts.annotate(times_validated = Max('datasource__ephysconceptmap__times_validated'))
#     dts = dts.annotate(min_validated = Min('datasource__ephysconceptmap__times_validated'))
    dts = dts.exclude(times_validated__gt = 1 )
    dts = dts.exclude(irrelevant_flag = True)
    dts = dts.distinct()
    dts = dts.annotate(num_ecms=Count('datasource__ephysconceptmap__ephys_prop', distinct = True))
    dts = dts.annotate(num_ncms=Count('datasource__neuronconceptmap__neuron', distinct = True))
    dts = dts.order_by('-num_ecms')
    dts = dts.exclude(num_ecms__lte = 1)
    
    # robot_user = m.get_robot_user()
    # for dt in dts:
    #     # who has curated article
    #     user_list = dt.get_curating_users()
    #     if robot_user in user_list:
    #         user_list.remove(robot_user)
    #     dt.curated_by = user_list
#         concept_maps = dt.get_concept_maps()
#         curated_on_dates = []
#         for cm in concept_maps:
#             curated_on = cm.history.latest().history_date
#             curated_on_dates.append(curated_on) 
#         dt.curated_on = max(curated_on_dates)

        
    return render('neuroelectro/data_table_to_validate_list.html', {'data_table_list': dts}, request)


def data_table_to_review_list(request):

    articles_needing_metadata_review = m.Article.objects.filter(articlefulltext__articlefulltextstat__metadata_needs_expert = True)
    dts = m.DataTable.objects.filter(
        Q(needs_expert = True) |
        Q(complex_neurons = True) |
        Q(note__isnull = False) |
        Q(article__in_ = articles_needing_metadata_review)
    ).distinct()

    dts = dts.annotate(times_validated = Max('datasource__ephysconceptmap__times_validated'))
    dts = dts.annotate(num_ecms=Count('datasource__ephysconceptmap__ephys_prop', distinct = True))
    dts = dts.annotate(num_ncms=Count('datasource__neuronconceptmap__neuron', distinct = True))
#     dts = dts.annotate(min_validated = Min('datasource__ephysconceptmap__times_validated'))
    dts = dts.exclude(irrelevant_flag = True)
    dts = dts.exclude(num_ncms__lt = 1)
    dts = dts.distinct()

    for dt in dts:
        if dt.article in articles_needing_metadata_review:
            dt.metadata_needs_expert = True
        else:
            dt.metadata_needs_expert = False
    #dts.filter(article__in_ = articles_needing_metadata_review).annotate(metadata_needs_expert = True)

    # robot_user = m.get_robot_user()
    # for dt in dts:
    #     # who has curated article
    #     user_list = dt.get_curating_users()
    #     if robot_user in user_list:
    #         user_list.remove(robot_user)
    #     dt.curated_by = user_list
    #     concept_maps = dt.get_concept_maps()
    #     curated_on_dates = []
    #     for cm in concept_maps:
    #         curated_on = cm.history.latest().history_date
    #         curated_on_dates.append(curated_on)
    #     dt.curated_on = max(curated_on_dates)

    return render('neuroelectro/data_table_to_review_list.html', {'data_table_list': dts}, request)

def data_table_no_neuron_list(request):
    dts = m.DataTable.objects.filter(datasource__ephysconceptmap__isnull = False, datasource__neuronconceptmap__isnull = True).distinct()
    dts = dts.annotate(min_validated = Min('datasource__ephysconceptmap__times_validated'))
    dts = dts.exclude(min_validated__gt = 0)
    dts = dts.distinct()
    dts = dts.annotate(num_ecms=Count('datasource__ephysconceptmap__ephys_prop', distinct = True))
    dts = dts.filter(num_ecms__gte = 4)
    dts = dts.order_by('-num_ecms')
    return render('neuroelectro/data_table_no_neuron_list.html', {'data_table_list': dts}, request)

def data_table_expert_list(request):
    dts = m.DataTable.objects.filter(needs_expert = True).distinct()
    dts = dts.annotate(num_ecms=Count('datasource__ephysconceptmap__ephys_prop', distinct = True))
    dts = dts.order_by('-num_ecms')
    return render('neuroelectro/data_table_to_validate_list.html', {'data_table_list': dts}, request)
    
def article_list(request):
    articles = m.Article.objects.filter(Q(datatable__datasource__neuronconceptmap__times_validated__gte = 1) | 
        Q(usersubmission__datasource__neuronconceptmap__times_validated__gte = 1)).distinct()
    #articles = articles.filter(articlefulltext__articlefulltextstat__metadata_human_assigned = True ).distinct()
    articles = articles.filter(articlesummary__num_nedms__gte = 1)
    returnDict = {'article_list':articles}
    return render('neuroelectro/article_list.html', returnDict, request)

def article_metadata_list(request):
    articles = m.Article.objects.filter(Q(datatable__datasource__neuronconceptmap__times_validated__gte = 1) | 
    Q(usersubmission__datasource__neuronconceptmap__times_validated__gte = 1)).distinct()
    #articles = articles.filter(articlefulltext__articlefulltextstat__metadata_human_assigned = True ).distinct()
    
    nom_vars = ['Species', 'Strain', 'ElectrodeType', 'PrepType', 'JxnPotential']
    #cont_vars  = ['RecTemp', 'AnimalAge', 'AnimalWeight']
    cont_vars  = ['ExternalSolution', 'InternalSolution', 'JxnOffset', 'RecTemp', 'AnimalAge', ]
    metadata_table = []
    for a in articles:
        amdms = m.ArticleMetaDataMap.objects.filter(article = a)
        curr_metadata_list = [None]*(len(nom_vars) + len(cont_vars))
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
            curr_metadata_list[i+len(nom_vars)] = curr_str
        a.metadata_list = curr_metadata_list
        if a.get_full_text_stat():
            a.metadata_human_assigned = a.get_full_text_stat().metadata_human_assigned
            a.methods_tag_found = a.get_full_text_stat().methods_tag_found
            a.metadata_needs_expert = a.get_full_text_stat().metadata_needs_expert
        else:
            a.metadata_human_assigned = False
            a.methods_tag_found = False
            a.metadata_needs_expert = False
        neuron_list = m.Neuron.objects.filter(Q(neuronconceptmap__times_validated__gte = 1) & 
        ( Q(neuronconceptmap__source__data_table__article = a) | Q(neuronconceptmap__source__user_submission__article = a))).distinct()     
        #neuron_list = m.Neuron.objects.filter(neuronconceptmap__source__data_table__article = a, neuronconceptmap__times_validated__gte = 1).distinct()
        neuron_list = [n.name for n in neuron_list]
        a.neuron_list = ', '.join(neuron_list)
    header_list = nom_vars + cont_vars
    returnDict = {'article_list':articles, 'metadata_table' : metadata_table, 'header_list': header_list}
    return render('neuroelectro/article_metadata_list.html', returnDict, request)
    
def nedm_comment_box(request):
    successBool = False
    if request.POST:
        message = ''
        if 'neuron_name' in request.POST and 'ephys_name' in request.POST and 'article_name' in request.POST:
            neuron_name = request.POST['neuron_name']
            ephys_name = request.POST['ephys_name']
            article_name = request.POST['article_name']
            message += 'Neuron Name: %s \nEphys Property: %s \nArticle Info: %s \n' % (neuron_name, ephys_name, article_name)
            legend = 'Thanks for your submission!'
        else:
            legend = "Please make sure all fields are filled out"
        if 'comments' in request.POST:
            comments = request.POST['comments']
            message += 'Comments : %s \n' % comments
        if 'email_address' in request.POST:
            email_address = request.POST['email_address']
            message += 'Email : %s \n' % email_address

        subject = 'Data note made to %s and %s in NeuroElectro' % (neuron_name, ephys_name)
        try:
            mail_admins(subject, message)
        except BadHeaderError:
            legend = "Please make sure all fields are filled out"

    else:
        legend = "Please add a comment/note identifying the miscurated data"

    # stuff for prepopulating form fields
    neuron_default_name = ''
    ephys_default_name  = ''
    article_default_name = ''
    if 'HTTP_REFERER' in request.META:
        if request.META['HTTP_REFERER'] is not None:
            citing_link = request.META['HTTP_REFERER']
            pk_search = re.search('/\d+/', citing_link)
            if pk_search:
                object_pk = int(pk_search.group()[1:-1])
            neuron_search = re.search('/neuron/', citing_link)
            ephys_search = re.search('/ephys_prop/', citing_link)
            data_table_search = re.search('/data_table/', citing_link)
            article_search = re.search('/article/', citing_link)
            if neuron_search:
                neuron_ob = m.Neuron.objects.get(pk = object_pk)
                neuron_default_name  = neuron_ob.name
            elif ephys_search:
                ephys_ob = m.EphysProp.objects.get(pk = object_pk)
                ephys_default_name  = ephys_ob.name
            elif article_search or data_table_search:
                if article_search:
                    article_ob = m.Article.objects.get(pk = object_pk)
                if data_table_search:
                    dt_ob = m.DataTable.objects.get(pk = object_pk)
                    article_ob = dt_ob.article
                pmid = article_ob.pmid
                author_name = article_ob.author_list_str.split()[0]
                pub_year = article_ob.pub_year
                article_default_name = '%s et al, %d; PMID: %d' % (author_name, pub_year, pmid)
    user = request.user
    if user is not None:
        user = m.get_anon_user()
        
    class NedmCommentForm(forms.Form):
        neuron_name = forms.CharField(
            label = "Neuron Type",
            required = True,
            initial = neuron_default_name,
        )
        ephys_name = forms.CharField(
            label = "Electrophysiological Property",
            max_length = 100,
            required = True,
            initial = ephys_default_name,
        )
        article_name = forms.CharField(
            label = "Article Information (e.g., Smith et al., 2000)",
            max_length = 200,
            required = True,
            initial = article_default_name,
        )
        comments = forms.CharField(
            widget = forms.Textarea(),
            label = 'Comments',
            max_length = 500,
            required = False,
        )
        email_address = forms.EmailField(
            label = "Contact Email <br>(we can contact you when the issue is resolved)",
            max_length = 200,
            required = False,
            #initial = str(user.email),
        )
        def __init__(self, *args, **kwargs):
            self.helper = FormHelper()
            self.helper.form_id = 'id-nedmCommentForm'
            self.helper.form_class = 'blueForms'
            self.helper.form_method = 'post'
            self.helper.form_action = ''
            #self.helper.add_input(Submit('submit', 'Submit'))
            self.helper.layout = Layout(
                Fieldset(
                    "<p align='left'>%s</p>" % legend,
                    'neuron_name',
                    'ephys_name',
                    'article_name',
                    'comments',
                    'email_address'
                    ),
                FormActions(
                    Submit('submit', 'Submit Information',align='middle'),
                    )
                )
            super(NedmCommentForm, self).__init__(*args, **kwargs)
    returnDict = {}
    returnDict['form'] = NedmCommentForm
    returnDict['successBool'] = successBool
    return render('neuroelectro/nedm_comment_box.html', returnDict, request)

# TODO: Spend some time on this function, why doesn't it work?
def neuron_add(request):
    region_list = m.BrainRegion.objects.all()
    returnDict = {'region_list':region_list}
    if request.POST:
        if 'neuron_name' in request.POST and request.POST['neuron_name'] and 'region_id' in request.POST:
            neuron_name = request.POST['neuron_name']
            region_id = int(request.POST['region_id'])
            # article_id = int(request.POST['article_id'])
            
            # artOb = m.Article.objects.get(pk = article_id)
            neuronOb = m.Neuron.objects.get_or_create(name = neuron_name,
                                                    added_by = 'human',
                                                    )[0]
            if region_id is not 0:
                regionOb = m.BrainRegion.objects.get(pk = region_id)
                neuronOb.regions.add(regionOb)
            # neuronOb.defining_articles.add(artOb)
            neuronSynOb = m.NeuronSyn.objects.get_or_create(term = neuron_name)[0]
            neuronOb.synonyms.add(neuronSynOb)
            neuronOb.save()
            urlStr = '/neuroelectro/neuron/%d/' % int(neuronOb.pk)
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
                article_query = m.Article.objects.filter(datatable__pk = dt_pk)
                if article_query.count() > 0:
                    citing_article = article_query[0]
                    returnDict['citing_article'] = citing_article        
    return render('neuroelectro/neuron_add.html', returnDict, request) 
        
def display_meta(request):
    values = request.META.items()
    values.sort()
    html = []
    #return HttpResponse("Welcome to the page at %s" % request.is_secure())
    for k, v in values:
        html.append('<tr><td>%s</td><td>%s</td></tr>' % (k, v))
    return HttpResponse('<table>%s</table>' % '\n'.join(html))  

# def neuron_search_form(request):
#     return render('neuroelectro/neuron_search_form.html')
   
def navbar(request):
    return render('neuroelectro/navbar.html')    

# def neuron_search(request):
#     if 'q' in request.GET and request.GET['q']:
#         q = request.GET['q']
#         neurons = m.Neuron.objects.filter(name__icontains=q)
#         return render('neuroelectro/neuron_search_results.html',
#             {'neurons': neurons, 'query': q})
#     else:
#         return HttpResponse('Please submit a search term.')
