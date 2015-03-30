# -*- coding: utf-8 -*-
# Create your views here.
from django.shortcuts import render,render_to_response, get_object_or_404
from django.db.models import Q
import neuroelectro.models as m
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.conf import settings
from django.db.models import Count, Min
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.signals import user_logged_in
from django.core.context_processors import csrf
from django.core.exceptions import ObjectDoesNotExist
from django import middleware
from bs4 import BeautifulSoup
import re

from article_text_mining.html_table_decode import isHeader, assignDataValsToNeuronEphys
from db_functions import add_ephys_nedm 
from helpful_functions import trunc
from db_functions.compute_field_summaries import computeArticleSummaries, computeNeuronEphysSummary, computeNeuronEphysSummariesAll
from article_text_mining.html_process_tools import getMethodsTag
from article_text_mining.pubmed_functions import add_single_article
from article_text_mining.resolve_data_float import resolve_data_float 

from itertools import groupby
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import json
import textwrap
import numpy as np
from django import forms
from django.core.mail import BadHeaderError, mail_admins
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout,Fieldset,Submit
from django.forms.formsets import DELETION_FIELD_NAME
from crispy_forms.bootstrap import FormActions
from django.forms.models import BaseInlineFormSet, inlineformset_factory
from django.template.response import TemplateResponse
from ckeditor.widgets import CKEditorWidget

# Overrides Django's render_to_response.  
# Obsolete now that 'render' exists. render_to_response(x,y,z) equivalent to render(z,x,y).  
def render(template,inDict,request):
    return render_to_response(template,inDict,context_instance=RequestContext(request))

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
            
def unsubscribe(request):
    if request.POST:
        email = request.POST['email']
        if validateEmail(email):
            if (MailingListEntry.objects.filter(email = email).exists()):
                MailingListEntry.objects.filter(email = email).delete()
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
    myDict = {}
    myDict['form'] = MailingListForm(request)
    return render('neuroelectro/splash_page.html',myDict,request)

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
# TODO: [@Dmitry] email all subs button, one way of adding it
#         layout = Layout(
#             FormActions(
#                 Submit('redirect', 'Email all subscribers',align='middle'),
#             )
#         )
#         if request.user.is_staff:
#             self.helper.add_layout(layout) 
        super(MailingListForm, self).__init__(*args, **kwargs)

def mailing_list_form_post(request):
    if 'email' in request.POST:
        email = request.POST['email']
        if validateEmail(email):
            name = request.POST['name']
            #comments = request.POST['comments']
            legend = "Your email has been successfully added! "
            mailing_list_entry_ob = MailingListEntry.objects.get_or_create(email = email)[0]
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
    output_message = legend
    message = {}
    message['response'] = output_message
    return HttpResponse(json.dumps(message), mimetype='application/json')

def send_email(TO, SUBJECT, TEXT):
    # TO must be a list
    gmail_user = "neuroelectro.test@gmail.com"
    gmail_pwd = "neuroelectron"
    FROM = gmail_user

    # Prepare actual message
    message = MIMEMultipart('alternative')
    message['Subject'] = SUBJECT
    message['From'] = FROM
    message['To'] = ", ".join(TO)
    message.attach(MIMEText(TEXT, 'plain'))
    message.attach(MIMEText(TEXT, 'html'))
    
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.ehlo()
        server.starttls()
        server.login(gmail_user, gmail_pwd)
        server.sendmail(FROM, TO, message.as_string())
        server.close()
        print('Successfully sent the email')
    except:
        print("Failed to send the email")

@user_passes_test(lambda u: u.is_staff)        
def admin_list_email(request):
    legend = "Type the body of the email in the text box and choose a title. Click submit to email all subscribers."
    if request.POST:
        text = request.POST['text']
        title = request.POST['title']
        if (text and title):
            mailingList = [o.email for o in MailingListEntry.objects.all()]
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
            #widget=TinyMCE(attrs={'cols': 40, 'rows': 20}),
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
            mailing_list_entry_ob = MailingListEntry.objects.get_or_create(email = email)[0]
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
            except ObjectDoesNotExist:
                mean_val = None
                sd_val = None
            if mean_val is None:
                mean_val = 0
            if sd_val is None:
                sd_val = 0
            num_articles = nes.num_articles
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

def ephys_prop_detail(request, ephys_prop_id):
    e = get_object_or_404(m.EphysProp, pk=ephys_prop_id)
    nedm_list = m.NeuronEphysDataMap.objects.filter(ephys_concept_map__ephys_prop = e, val_norm__isnull = False).order_by('neuron_concept_map__neuron__name')
    if e.id == 16:
        nedm_list = m.NeuronEphysDataMap.objects.filter(ephys_concept_map__ephys_prop__id__in = [16, 19], val_norm__isnull = False).order_by('neuron_concept_map__neuron__name')
    data_list_validated, data_list_unvalidated, neuronNameList, value_list_all = ephys_prop_to_list2(nedm_list)
    neuron_list = [m.Neuron.objects.get(name = nName) for nName in neuronNameList]
    log_ephys_axis_names = ['input resistance', 'rheobase', 'cell capacitance']
    if e.name in log_ephys_axis_names:
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
    valid_pk_list = list(range(2,8))
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

def ephys_prop_to_list2(nedm_list):
    data_list_validated = []
    data_list_unvalidated = []
    cnt = 0
    neuronCnt = 0
    value_list_all = []
    oldNeuronName = []
    neuronNameList = oldNeuronName
    #main_ephys_prop_ids = [2, 3, 4, 5, 6, 7]
    main_ephys_prop_ids = list(range(1, 28))
    for nedm in nedm_list:
        val = nedm.val_norm
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
    for datatable in article.datatable_set.all():
        nedm_list_temp = datatable.datasource_set.get().neuronephysdatamap_set.all().order_by('neuron_concept_map__neuron__name', 'ephys_concept_map__ephys_prop__name')
        nedm_list.extend(nedm_list_temp)
    for usersubmission in article.usersubmission_set.all():
        nedm_list_temp = usersubmission.datasource_set.get().neuronephysdatamap_set.all().order_by('neuron_concept_map__neuron__name', 'ephys_concept_map__ephys_prop__name')
        nedm_list.extend(nedm_list_temp)
    returnDict = {'article': article, 'metadata_list':metadata_list, 'nedm_list':nedm_list}
    return render('neuroelectro/article_detail.html', returnDict, request)

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
                        amdm.times_validated = amdm.times_validated + 1
                        amdm.save()
                    else:
                        amdm = m.ArticleMetaDataMap.objects.create(article = article, metadata = metadata_ob, added_by = user, times_validated = 1)
                for amdm in amdms_old:
                    amdm.delete()
            else:
                amdms = m.ArticleMetaDataMap.objects.filter(article = article, metadata__name = o)
                amdms.delete()
        for c in cont_list_names:
            if c in request.POST:
                entered_string = str(request.POST[c])
                if len(entered_string) > 0:
                    retDict = resolve_data_float(entered_string)
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
                        cont_value_ob = m.ContValue.objects.get_or_create(mean = retDict['value'], min_range = min_range,
                                                                          max_range = max_range, stderr = stderr)[0]
                        metadata_ob = m.MetaData.objects.get_or_create(name=c, cont_value=cont_value_ob)[0]
                        # check if amdm ob already exists, if it does, just update pointer for amdm, but leave old md intact
                        amdmQuerySet = m.ArticleMetaDataMap.objects.filter(article = article, metadata__name = c)
                        if amdmQuerySet.count() > 0:
                            amdm = amdmQuerySet[0]
                            amdm.metadata = metadata_ob
                            amdm.times_validated = amdm.times_validated + 1
                            amdm.save()
                        else:
                            amdm = m.ArticleMetaDataMap.objects.create(article = article, metadata = metadata_ob, added_by = user, times_validated = 1)
                else:
                    amdms = m.ArticleMetaDataMap.objects.filter(article = article, metadata__name = c)
                    amdms.delete()
        
        # if no full text object in DB, create one
        aft = m.ArticleFullText.objects.get_or_create(article=article)[0]
        afts = m.ArticleFullTextStat.objects.get_or_create(article_full_text = aft)[0]

        # note that the article metadata has now been checked and validated by a human
        afts.metadata_human_assigned = True
        afts.save()
    metadata_list = m.MetaData.objects.filter(articlemetadatamap__article = article).distinct()
    if article.get_full_text_stat():
        if article.get_full_text_stat().methods_tag_found:
            methods_html = getMethodsTag(article.get_full_text().get_content(), article)
            methods_html = str(methods_html)
        else:
            methods_html = None
    else:
        methods_html = None
    returnDict = {'article': article, 'metadata_list':metadata_list, 'methods_html': methods_html}
    initialFormDict = {}
    for md in metadata_list:
        if md.value:
            if md.name in initialFormDict:
                initialFormDict[md.name].append(str(md.id))
            else:
                initialFormDict[md.name] = [str(md.id)]
        else:
            initialFormDict[md.name] = str(md.cont_value)

    returnDict['form'] = ArticleMetadataForm(initial=initialFormDict)
    return render('neuroelectro/article_metadata.html', returnDict, request)


class ArticleMetadataForm(forms.Form):
    AnimalAge = forms.CharField(
        required = False,
        label = 'Age (days, e.g. 5-10; P46-P94)'
    )
    AnimalWeight = forms.CharField(
        required = False,
        label = 'Weight (grams, e.g. 150-200)'
    )
    RecTemp = forms.CharField(
        required = False,
        label = 'Temp (°C, e.g. 33-45°C)'

    )
    JxnOffset = forms.CharField(
        required = False,
        label = 'Junction Offset (mV, e.g. -11 mV)'

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
                'JxnPotential',
                'JxnOffset',
                ),
            FormActions(
                Submit('submit', 'Submit Information', align='middle'),
                )
            )
        super(ArticleMetadataForm, self).__init__(*args, **kwargs)
        self.fields['Species'] = forms.MultipleChoiceField(
            choices= [(md.id, md.value) for md in m.MetaData.objects.filter(name = 'Species')], 
            required = False,
        )
        self.fields['Strain'] = forms.MultipleChoiceField(
            choices=[ (md.id, md.value) for md in m.MetaData.objects.filter(name = 'Strain')],
            required = False,
        )
        self.fields['ElectrodeType'] = forms.MultipleChoiceField(
            choices=[ (md.id, md.value) for md in m.MetaData.objects.filter(name = 'ElectrodeType')],
            required = False,
        )
        self.fields['JxnPotential'] = forms.MultipleChoiceField(
            choices=[ (md.id, md.value) for md in m.MetaData.objects.filter(name = 'JxnPotential')],
            required = False,
        )
        self.fields['PrepType'] = forms.MultipleChoiceField(
            choices=[ (md.pk, md.value) for md in m.MetaData.objects.filter(name = 'PrepType')],
            required = False,
        )

def data_table_detail(request, data_table_id):
    datatable = get_object_or_404(DataTable, pk=data_table_id)
    if request.method == 'POST':
        if 'validate_all' in request.POST:
            ecmObs = datatable.datasource_set.all()[0].ephysconceptmap_set.all()
            ncmObs = datatable.datasource_set.all()[0].neuronconceptmap_set.all()
            nedmObs = datatable.datasource_set.all()[0].neuronephysdatamap_set.all()
            #neurons = m.Neuron.objects.filter(neuronconceptmap__in = ncmObs)
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
        elif 'remove_all' in request.POST:
            ecmObs = datatable.datasource_set.all()[0].ephysconceptmap_set.all().delete()
            ncmObs = datatable.datasource_set.all()[0].neuronconceptmap_set.all().delete()
            nedmObs = datatable.datasource_set.all()[0].neuronephysdatamap_set.all().delete()
        if 'expert' in request.POST:
            datatable.needs_expert = True
        else:
            datatable.needs_expert = False
        if 'data_table_note' in request.POST:
            note = request.POST['data_table_note'] 
            if len(note) > 0:
                note = re.sub('_', ' ', note)
                datatable.note = note
        datatable.save()
        articleQuerySet = m.Article.objects.filter(datatable = datatable)
        computeArticleSummaries(articleQuerySet)
    nedm_list = datatable.datasource_set.get().neuronephysdatamap_set.all().order_by('neuron_concept_map__neuron__name', 'ephys_concept_map__ephys_prop__name')
    #inferred_neurons = list(set([str(nel.neuron.name) for nel in nel_list]))
    csrf_token = middleware.csrf.get_token(request)
    if request.user.is_authenticated():
        validate_bool = True
        enriched_html_table = enrich_ephys_data_table(datatable, csrf_token, validate_bool)
        returnDict = {'datatable': datatable, 'nedm_list': nedm_list,
                        'enriched_html_table':enriched_html_table}  
        if datatable.note:
            note_str = re.sub('\s', '_', datatable.note)
            returnDict['data_table_note'] = note_str
        return render('neuroelectro/data_table_detail_validate.html', returnDict, request)
    enriched_html_table = enrich_ephys_data_table(datatable, csrf_token)
    returnDict = {'datatable': datatable, 'nedm_list': nedm_list,
                    'enriched_html_table':enriched_html_table}      
    return render('neuroelectro/data_table_detail.html', returnDict, request)

def data_table_detail_no_annotation(request, data_table_id):
    datatable = get_object_or_404(DataTable, pk=data_table_id)
    returnDict = {'datatable': datatable}      
    return render('neuroelectro/data_table_detail_no_annotation.html', returnDict, request)

def ephys_concept_map_detail(request, ephys_concept_map_id):
    ecm = get_object_or_404(m.EphysConceptMap, pk=ephys_concept_map_id)
    return render('neuroelectro/ephys_concept_map_detail.html', {'ephys_concept_map': ecm}, request)
    
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

    EphysPropFormSet = inlineformset_factory(m.NeuronData, m.EphysProperty, extra=1, formfield_callback = ephysprop_callback)

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
        
    NeuronDataFormSet = inlineformset_factory(m.NeuronDataAddMain, m.NeuronData, formset=BaseNeuronFormSet, extra=1, formfield_callback = neurondata_callback)
    
    if request.POST:
        neuron_data_formset = NeuronDataFormSet(request.POST, prefix='neurondata')
        
        if neuron_data_formset.is_valid():
            pubmed_id = request.POST["pubmed_id"]
            
            dictOfPrefixes = {}
            data = neuron_data_formset.data
            
            for (key, value) in list(data.items()):
                if re.match('EPHYS_PROP_\d+$', key.encode('ascii','ignore')) is not None:
                    dictOfPrefixes[key.encode('ascii','ignore')] = value.encode('ascii','ignore')
            
            neuron_type_list = []
            ephys_prop_list = []                    
            for (ephys_prefix, neuron_index) in list(dictOfPrefixes.items()):
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
            # SJT NOTE - note updating neuron or ephys summaries cause they take too long
            computeArticleSummaries(article)
            computeNeuronEphysSummariesAll(neuron_type_list, ephys_prop_list)
            #computeNeuronSummaries(neuron_type_list)
            #computeEphysPropSummaries(ephys_prop_list)
            
            # mail admins for notification of data addition
            message = 'user %s added data for %s \nfrom %s' % (request.user, neuron_type_list, article.title)
            subject = 'User %s added data to NeuroElectro' %request.user
            mail_admins(subject, message)

# TODO: Look at this, why does this fail on Shreejoy's machine?
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
    email_message = 'Neuron name: %s \nArticle Title: %s \nPumed Link: %s \nUser: %s \n' % (n.name, article.title, pmid_link, user)
    try:
        mail_admins(subject, email_message)
    except BadHeaderError:
        # TODO: why is legend not used here?
        legend = "Please make sure all fields are filled out"
    output_message = 'article suggested!'
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
    try:
        mail_admins(subject, email_message)
    except BadHeaderError:
        # TODO: why is legend not used here?
        legend = "Please make sure all fields are filled out"
    output_message = 'article suggested!'
    message = {}
    message['response'] = output_message
    return HttpResponse(json.dumps(message), mimetype='application/json')

#This function really sucks @SuppressWarnings
def neuron_article_curate_list(request, neuron_id):
    n = get_object_or_404(m.Neuron, pk=neuron_id)
    min_mentions_nam_1 = 20
    min_mentions_nam_2 = 3
#     max_un_articles = 50
    articles_ex = m.Article.objects.filter(datatable__datasource__neuronconceptmap__neuron = n, datatable__datasource__neuronephysdatamap__isnull = False).distinct()
    for art in articles_ex:
        dts = DataTable.objects.filter(article = art, datasource__ephysconceptmap__isnull = False).distinct()
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
        dts = DataTable.objects.filter(article = art).distinct()
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
    
def fancybox_test(request):
    return render('neuroelectro/fancybox_test.html', {}, request)
    
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
            dt.top_neuron_total_num = m.NeuronConceptMap.objects.filter(neuron = dt.top_neuron, times_validated__gte = 1).count()
        else:
            dt.top_neuron = None
            dt.top_neuron_total_num = None
        # dt.num_ecms = m.EphysProp.objects.filter(ephysconceptmap__source__data_table = dt).distinct().count()
    return render('neuroelectro/data_table_to_validate_list.html', {'data_table_list': dts}, request)

def data_table_no_neuron_list(request):
    dts = DataTable.objects.filter(datasource__ephysconceptmap__isnull = False, datasource__neuronconceptmap__isnull = True).distinct()
    dts = dts.annotate(min_validated = Min('datasource__ephysconceptmap__times_validated'))
    dts = dts.exclude(min_validated__gt = 0)
    dts = dts.distinct()
    dts = dts.annotate(num_ecms=Count('datasource__ephysconceptmap__ephys_prop', distinct = True))
    dts = dts.filter(num_ecms__gte = 4)
    dts = dts.order_by('-num_ecms')
    return render('neuroelectro/data_table_no_neuron_list.html', {'data_table_list': dts}, request)

def data_table_expert_list(request):
    dts = DataTable.objects.filter(needs_expert = True).distinct()
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
    cont_vars  = ['JxnOffset', 'RecTemp', 'AnimalAge', ]
    metadata_table = []
    for a in articles:
        amdms = m.ArticleMetaDataMap.objects.filter(article = a)
        curr_metadata_list = [None]*(len(nom_vars) + len(cont_vars))
        for i,v in enumerate(nom_vars):
            valid_vars = amdms.filter(metadata__name = v)
            temp_metadata_list = [vv.metadata.value for vv in valid_vars]
            curr_metadata_list[i] = ', '.join(temp_metadata_list)
        for i,v in enumerate(cont_vars):
            valid_vars = amdms.filter(metadata__name = v)
            curr_str = ''
            for vv in valid_vars:
                cont_value_ob = vv.metadata.cont_value
                curr_str += str(cont_value_ob)
            curr_metadata_list[i+len(nom_vars)] = curr_str
        a.metadata_list = curr_metadata_list
        if a.get_full_text_stat():
            a.metadata_human_assigned = a.get_full_text_stat().metadata_human_assigned
            a.methods_tag_found = a.get_full_text_stat().methods_tag_found
        else:
            a.metadata_human_assigned = False
            a.methods_tag_found = False      
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
    if 'HTTP_REFERER' in request.META:
        if request.META['HTTP_REFERER'] is not None:
            citing_link = request.META['HTTP_REFERER']
            pk_search = re.search('/\d+/', citing_link)
            if pk_search:
                object_pk = int(pk_search.group()[1:-1])
            neuron_search = re.search('/neuron/', citing_link)
            ephys_search = re.search('/ephys_prop/', citing_link)
            if neuron_search:
                neuron_ob = m.Neuron.objects.get(pk = object_pk)
                neuron_default_name  = neuron_ob.name
            elif ephys_search:
                ephys_ob = m.EphysProp.objects.get(pk = object_pk)
                ephys_default_name  = ephys_ob.name
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

def neuron_concept_map_modify(request):
    user = request.user
    if request.user.is_anonymous():
        user = m.get_anon_user()
    if 'data_table_id' in request.POST and 'box_id' in request.POST and 'neuron_dropdown' in request.POST and 'neuron_note' in request.POST: 
        dt_pk = int(request.POST['data_table_id'])
        dtOb = DataTable.objects.get(pk = dt_pk)
        dsOb = DataSource.objects.get(data_table = dtOb)
        urlStr = "/neuroelectro/data_table/%d" % dt_pk
        box_id = request.POST['box_id']
        neuron_note = request.POST['neuron_note']
        selected_neuron_name = request.POST['neuron_dropdown']
        if selected_neuron_name == "None selected":
            ncm_pk = int(request.POST['ncm_id'])
            ncmOb = m.NeuronConceptMap.objects.get(pk= ncm_pk)
            ncmOb.delete()
            return HttpResponseRedirect(urlStr)
        neuron_ob = m.Neuron.objects.get(name = selected_neuron_name)
        # modifying an already existing ncm
        if 'ncm_id' in request.POST: 
            ncm_pk = int(request.POST['ncm_id'])
            ncmOb = m.NeuronConceptMap.objects.get(pk= ncm_pk)
            # only modify ecm if not the same as original
            if ncmOb.neuron != neuron_ob:
                ncmOb.neuron = neuron_ob
                ncmOb.added_by = user
            elif len(neuron_note) > 0:
                ncmOb.note = re.sub('_', ' ', neuron_note)
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
            ncmOb = m.NeuronConceptMap.objects.get_or_create(ref_text = ref_text,
                                                          neuron = neuron_ob,
                                                          # ephys_prop_syn = ephysSynOb,
                                                          source = dsOb,
                                                          dt_id = box_id,
                                                          #match_quality = matchVal,
                                                          added_by = user)[0]
            if len(neuron_note) > 0:
                ncmOb.note = re.sub('_', ' ', neuron_note)
                ncmOb.save()
        # since ncm changed, run data val mapping function on this data table
        assignDataValsToNeuronEphys(dtOb)                                                
        
        return HttpResponseRedirect(urlStr)
    else:
        message = 'null'
        return HttpResponse(message)

def ephys_concept_map_modify(request):
    #ecm = get_object_or_404(EphysConceptMap, pk=ephys_concept_map_id)
    user = request.user
    if request.user.is_anonymous():
        user = m.get_anon_user()
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
            ecmOb = m.EphysConceptMap.objects.get(pk= ecm_pk)
            ecmOb.delete()
            return HttpResponseRedirect(urlStr)
        ephys_prop_ob = m.EphysProp.objects.get(name = selected_ephys_prop_name)
        # modifying an already existing ecm
        if 'ecm_id' in request.POST: 
            ecm_pk = int(request.POST['ecm_id'])
            ecmOb = m.EphysConceptMap.objects.get(pk= ecm_pk)
            # only modify ecm if not the same as original
            if ecmOb.ephys_prop != ephys_prop_ob:
                ecmOb.ephys_prop = ephys_prop_ob
                ecmOb.added_by = user
            elif len(ephys_note) > 0:
                ecmOb.note = re.sub('_', ' ', ephys_note)
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
            ecmOb = m.EphysConceptMap.objects.get_or_create(ref_text = ref_text,
                                                          ephys_prop = ephys_prop_ob,
                                                          #ephys_prop_syn = ephysSynOb,
                                                          source = dsOb,
                                                          dt_id = box_id,
                                                          #match_quality = matchVal,
                                                          added_by = user)[0]
            if len(ephys_note) > 0:
                ecmOb.note = re.sub('_', ' ', ephys_note)
                ecmOb.save()
        # since ecm changed, run data val mapping function on this data table
        assignDataValsToNeuronEphys(dtOb, user)        
        return HttpResponseRedirect(urlStr)
    else:
        message = 'null'
        return HttpResponse(message)
        
def display_meta(request):
    values = list(request.META.items())
    values.sort()
    html = []
    #return HttpResponse("Welcome to the page at %s" % request.is_secure())
    for k, v in values:
        html.append('<tr><td>%s</td><td>%s</td></tr>' % (k, v))
    return HttpResponse('<table>%s</table>' % '\n'.join(html))  

def neuron_search_form(request):
    return render('neuroelectro/neuron_search_form.html')    
   
def navbar(request):
    return render('neuroelectro/navbar.html')    

def neuron_search(request):
    if 'q' in request.GET and request.GET['q']:
        q = request.GET['q']
        neurons = m.Neuron.objects.filter(name__icontains=q)
        return render('neuroelectro/neuron_search_results.html',
            {'neurons': neurons, 'query': q})
    else:
        return HttpResponse('Please submit a search term.')
    # try:
        
    # nel_list = datatable.neuronephyslink_set.all()
    # inferred_neurons = list(set([str(nel.neuron.name) for nel in nel_list]))
    # enriched_html_table = enrich_ephys_data_table(datatable)
    # returnDict = {'datatable': datatable, 'inferred_neurons': inferred_neurons, 'nel_list': nel_list,
                    # 'enriched_html_table':enriched_html_table}
    # return render('neuroelectro/data_table_detail.html', returnDict, request)

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
        if 'id' in list(td_tag.attrs.keys()):
            tag_id = str(td_tag['id'])
        else: 
            tag_id = '-1'
        if len(tdText) > 0 or tag_id in matchingDTIds or tag_id in matchingNeuronDTIds:
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
            elif isHeader(tdText) == False:
                continue
            else:
                if validate_bool == True:
                    dropdownTag = ephys_neuron_dropdown(csrf_token, dataTableOb, tag_id, None, None, anmObs, validate_bool)
                
                    td_tag.append(dropdownTag)

    tableStr = str(soup)
    tableStr = tableStr.replace('##160;', '') # hack to fix imperfect transfer of xml -> html
    enriched_html_table = tableStr

    return enriched_html_table   

def change_add_tag(baseTagAddStr,  ecmOb = None, ncmOb = None):
    tagSoup = BeautifulSoup(baseTagAddStr)
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
        #ncmTag = BeautifulSoup('''<input type="hidden" name="ncm_id" value=%d />''' % (int(ncmOb.pk)))
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
    for ephys_prop in m.EphysProp.objects.all():
        ephys_name = str(ephys_prop.name)
        chunk += '''<option value=%r>%r</option>''' % (ephys_name, ephys_name)
    chunk+= '''</select>'''
    return chunk
    
def genNeuronListDropdown2(neuronNameList = None):
    chunk = '''<select class="neuron_dropdown" name ="neuron_dropdown">'''
    if neuronNameList is not None:
        for name in neuronNameList:
            neuron_name = str(name)
            chunk += '''<option value=%r>%r</option>''' % (neuron_name, neuron_name)
    chunk += '''<option value=%r>%r</option>''' % ('None selected', 'None selected')
    for neuron in m.Neuron.objects.all():
        neuron_name = str(neuron.name)
        chunk += '''<option value=%r>%r</option>''' % (neuron_name, neuron_name)
    chunk+= '''</select>'''
    return chunk    
     
def genEphysListDropdown(defaultSelected = None):
    chunk = '''<select class="ephys_dropdown" name ="ephys_dropdown">'''
    chunk += '''<option value=%r>%r</option>''' % ('None selected', 'None selected')
    for ephys_prop in m.EphysProp.objects.all():
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
    for neuron in m.Neuron.objects.all():
        neuron_name = str(neuron.name)
        if neuron_name == defaultSelected:
            chunk += '''<option selected="selected" value=%r name = %r>%r</option>''' % (neuron_name, neuron_name, neuron_name)
        else:
            chunk += '''<option value=%r>%r</option>''' % (neuron_name, neuron_name)
    chunk+= '''</select>'''
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
    chunk = re.sub(r'>[\s]+<', '> <', chunk)
    return BeautifulSoup(chunk)
