
# Methods to restore the database after the migration. applied by Rick.  
import sys
import pickle
import simplejson
import re
import numpy as np

import xlrd

from db_functions.pubmed_functions import add_single_article_full
# from article_text_mining.full_text_pipeline import ephys_table_identify
# from article_text_mining.full_text_pipeline import apply_neuron_article_maps, apply_article_metadata
from article_text_mining.assign_metadata import update_amd_obj
from db_functions.compute_field_summaries import normalizeNedms
from neuroelectro import models as m
from neuroelectro.data_migration_scripts.update_ephys_props_and_ecms import update_ephys_defs
from scripts.update_db_summary_fields import update_summary_fields
from article_text_mining.mine_ephys_prop_in_table import get_units_from_table_header
from db_functions.normalize_ephys_data import normalize_nedm_val, check_data_val_range

sys.path.append('code')

def main():
    update_concept_maps()
    update_ephys_defs()
    assign_robot()
    update_articles()
    assign_journal_publishers()

    # update_articles() # this one will take a while and prob fail

def prog(num,denom):
    fract = float(num)/denom
    hyphens = int(round(50*fract))
    spaces = int(round(50*(1-fract)))
    sys.stdout.write('\r%.2f%% [%s%s]' % (100*fract,'-'*hyphens,' '*spaces))
    sys.stdout.flush() 

def update_concept_maps():
    ncm_fields, ecm_fields, nedm_fields = load()
    datatables = m.DataTable.objects.all()
    print 'Getting or creating data sources'
    for i,x in enumerate(datatables):
        prog(i,datatables.count())
        m.DataSource.objects.get_or_create(data_table=x)
    
    anon_user = m.get_anon_user()
    robot_user = m.get_robot_user()
    print 'Updating nedm fields'
    for i,nedm_field in enumerate(nedm_fields):
        prog(i, len(nedm_fields))
        nedm=m.NeuronEphysDataMap.objects.get(pk=nedm_field['pk'])
        data_source = m.DataSource.objects.get(data_table=nedm_field['fields']['data_table'])
        nedm.source = data_source
        # if nedm.added_by_old == 'human':
        #     nedm.added_by = anon_user
        # else:
        #     nedm.added_by = robot_user
        nedm.save()

    print 'Updating ncm fields'
    for i,ncm_field in enumerate(ncm_fields):
        prog(i, len(ncm_fields))
        ncm=m.NeuronConceptMap.objects.get(pk=ncm_field['pk'])
        data_source = m.DataSource.objects.get(data_table=ncm_field['fields']['data_table'])
        ncm.source = data_source
        # if ncm.added_by_old == 'human':
        #     ncm.added_by = anon_user
        # else:
        #     ncm.added_by = robot_user
        ncm.save()
    
    print 'Updating ecm fields'

    for ecm_field in ecm_fields:
        prog(i, len(ecm_fields))

        ecm=m.EphysConceptMap.objects.get(pk=ecm_field['pk'])
        data_source = m.DataSource.objects.get(data_table=ecm_field['fields']['data_table'])
        ecm.source = data_source
        # if ecm.added_by_old == 'human':
        #     ecm.added_by = anon_user
        # else:
        #     ecm.added_by = robot_user
        ecm.save()
        
def assign_robot():
    nams = m.NeuronArticleMap.objects.all()
    u = m.get_robot_user()
    for nam in nams:
        nam.added_by = u
        nam.save()
        
def update_articles():
    print 'Updating articles'
    all_arts = m.Article.objects.all()
    pmid_list = [a.pmid for a in all_arts]
    pmid_list_len = len(pmid_list)
    for i,pmid in enumerate(pmid_list):
        prog(i, pmid_list_len)
        a = m.Article.objects.filter(pmid=pmid)[0]
        if a.author_list_str is None:
            add_single_article_full(pmid)

def load():
    print 'Loading files'
    pkl_file = open('user_contrib_data', 'rb')
    myData = pickle.load(pkl_file)
    pkl_file.close()
    ncm_fields, ecm_fields, nedm_fields = myData
    return (ncm_fields, ecm_fields, nedm_fields)
    
def assign_journal_publishers():
    print 'Assigning publishers'
    book = xlrd.open_workbook("data/journal_publisher_list.xlsx")
    sheet = book.sheet_by_index(0)
    ncols = sheet.ncols
    nrows = sheet.nrows

    table= [ [ 0 for i in range(ncols) ] for j in range(nrows ) ]
    for i in range(nrows):
        for j in range(ncols):
            table[i][j] = sheet.cell(i,j).value
    for i in range(1,nrows):
        journal_name = table[i][0]
        publisher_name = table[i][1]
        journalOb = m.Journal.objects.get_or_create(title = journal_name)[0]
        publisherOb = m.Publisher.objects.get_or_create(title = publisher_name)[0]
        journalOb.publisher = publisherOb
        journalOb.save()

def load_metadata():
    print 'Assigning metadata'
    book = xlrd.open_workbook("data/metadata_key_value_pairs.xlsx")
    sheet = book.sheet_by_index(0)
    ncols = sheet.ncols
    nrows = sheet.nrows

    table= [ [ 0 for i in range(ncols) ] for j in range(nrows ) ]
    for i in range(nrows):
        for j in range(ncols):
            table[i][j] = sheet.cell(i,j).value
    for i in range(1,nrows):
        key = table[i][0]
        value = table[i][1]
        metadataOb = m.MetaData.objects.get_or_create(name = key, value = value)[0]


# def add_full_texts():
#     wiley_path = '/home/shreejoy/full_texts/wiley_html'
#     elsevier_path = '/home/shreejoy/full_texts/elsevier_xml'
#     highwire_path = '/home/shreejoy/full_texts/neuro_full_texts'
#     print 'adding highwire full texts'
#     add_multiple_full_texts_all(highwire_path)
#     print 'adding wiley full texts'
#     add_multiple_full_texts_all(wiley_path)
#     print 'adding elsevier full texts'
#     add_multiple_full_texts_all(elsevier_path)

#
# def annotate_full_texts():
#     print 'adding neuron article maps'
#     apply_neuron_article_maps()
#     print 'annotating data table ephys props'
#     ephys_table_identify()
#     print 'annotating articles for metadata'
#     apply_article_metadata()

def convert_article_metadata_maps():
    articles = m.Article.objects.filter(metadata__isnull = False)
    num_articles = articles.count()
    for i,a in enumerate(articles):
        prog(i, num_articles)
        md_obs = a.metadata.all()
        for md in md_obs:
            a.metadata.remove(md)
            amdm = m.ArticleMetaDataMap.objects.get_or_create(article = a, metadata = md, added_by = md.added_by)[0]

def remove_duplicated_ephysconceptmaps():
    dts = m.DataTable.objects.filter(datasource__ephysconceptmap__isnull = False).distinct()
    num_dts = dts.count()
    print 'checking %d data tables' % num_dts
    for i,dt in enumerate(dts):
        prog(i, num_dts)
        ecms = dt.datasource_set.all()[0].ephysconceptmap_set.all()
        for ecm in ecms:
            curr_dt_id = ecm.dt_id
            if curr_dt_id is not None:
                ecm_duplicated_set = ecms.filter(dt_id = curr_dt_id).order_by('-times_validated')
                if ecm_duplicated_set.count() > 0:
                    for ecm in ecm_duplicated_set[1:]:
                        ecm.delete()

def write_old_article_metadata_maps():
    arts = m.Article.objects.filter(metadata__isnull = False).distinct()
    num_arts = arts.count()
    with open ('data/old_article_metadata_maps.txt', 'a') as f:
        for i,a in enumerate(arts):
            prog(i, num_arts)
            for md in a.metadata.all():
                f.write ('[%d , %d]\n' % (a.pk, md.pk))

def assign_old_article_metadata_maps():
    with open ('data/old_article_metadata_maps.txt', 'r') as f:
        content = f.readlines()
    num_amdms = len(content)
    print 'repopulating %d article metadata maps' % num_amdms
    robot_user = m.get_robot_user()
    for i,line in enumerate(content):
        prog(i, num_amdms)
        [art_pk_str, md_pk_str] = re.findall('\d+', line)
        # print (art_pk_str, md_pk_str)
        # print line
        a = m.Article.objects.get(pk = int(art_pk_str))
        md = m.MetaData.objects.get(pk = int(md_pk_str))
        amdm = m.ArticleMetaDataMap.objects.get_or_create(article = a,
            metadata = md, added_by = robot_user)[0]
            
def assign_neuron_clustering():
    print 'Assigning neuron cluster PCA vals'
    book = xlrd.open_workbook("data/neuron_clustering_data_vals.xlsx")
    sheet = book.sheet_by_index(0)
    ncols = sheet.ncols
    nrows = sheet.nrows

    table= [ [ 0 for i in range(ncols) ] for j in range(nrows ) ]
    for i in range(nrows):
        for j in range(ncols):
            table[i][j] = sheet.cell(i,j).value
    
    # first null out current cluster values
    nsObsAll = m.NeuronSummary.objects.all()
    for nsOb in nsObsAll:
        nsOb.cluster_xval = None
        nsOb.cluster_yval = None
        nsOb.save()
    
    for i in range(1,nrows):
        neuron_name_str = table[i][0]
        xInd = table[i][1]
        yInd = table[i][2]
        neuron_name = str(neuron_name_str).strip()
        #print neuron_name
        n = m.Neuron.objects.get(name = neuron_name)
        nsOb = m.NeuronSummary.objects.get(neuron = n)
        nsOb.cluster_xval = xInd
        nsOb.cluster_yval = yInd
        nsOb.save()

def assign_ephys_nlex_ids():
    print 'Assigning nlex ids to ephys props'
    book = xlrd.open_workbook("data/Ephys_prop_definitions_4.xlsx")
    sheet = book.sheet_by_index(0)
    ncols = sheet.ncols
    nrows = sheet.nrows

    table= [ [ 0 for i in range(ncols) ] for j in range(nrows ) ]
    for i in range(nrows):
        for j in range(ncols):
            table[i][j] = sheet.cell(i,j).value
    
    for i in range(1,nrows):
        ephys_prop = table[i][0]
        ephys_prop_id = table[i][6]
        nlex_id = table[i][7]
        #print neuron_name
        e = m.EphysProp.objects.get(name = ephys_prop, id = ephys_prop_id)
        e.nlex_id = nlex_id
        e.save()

def assign_neuron_neuron_db_ids():
    print 'Assigning neuron db ids to neurons'
    book = xlrd.open_workbook("data/neurondb2neuroelectro_v2.xlsx")
    sheet = book.sheet_by_index(0)
    ncols = sheet.ncols
    nrows = sheet.nrows

    table= [ [ 0 for i in range(ncols) ] for j in range(nrows ) ]
    for i in range(nrows):
        for j in range(ncols):
            table[i][j] = sheet.cell(i,j).value
    
    for i in range(1,nrows):
        neuron_db_id = table[i][0]
        neuron_id = table[i][4]
        neuron_db_name = table[i][1]
        neuron = m.Neuron.objects.get(pk=neuron_id)
        print neuron_db_name, neuron.name
        #print neuron_name
        neuron.neuron_db_id = neuron_db_id
        neuron.save()

def assign_ephys_norm_criteria():
    print 'Assigning Ephys defs and normalization criteria'
    book = xlrd.open_workbook("data/Ephys_prop_normalization_criteria.xlsx")
    sheet = book.sheet_by_index(0)
    ncols = sheet.ncols
    nrows = sheet.nrows

    table= [ [ 0 for i in range(ncols) ] for j in range(nrows ) ]
    for i in range(nrows):
        for j in range(ncols):
            table[i][j] = sheet.cell(i,j).value
    
    for i in range(1,nrows):
        ephys_name = table[i][0]
        ephys_def = table[i][1]
        ephys_norm_criteria = table[i][2]
        ephys_prop = m.EphysProp.objects.get(name=ephys_name)
        print ephys_name, ephys_prop.name

        ephys_prop.definition = ephys_def
        ephys_prop.norm_criteria = ephys_norm_criteria
        ephys_prop.save()
        #print neuron_name
        # neuron.neuron_db_id = neuron_db_id
        # neuron.save()

def update_adaptation_ratios():
    print 'Assigning Ephys defs and normalization criteria'
    book = xlrd.open_workbook("data/adaptation_ratio_normalization.xlsx")
    sheet = book.sheet_by_index(0)
    ncols = sheet.ncols
    nrows = sheet.nrows

    table= [ [ 0 for i in range(ncols) ] for j in range(nrows ) ]
    for i in range(nrows):
        for j in range(ncols):
            table[i][j] = sheet.cell(i,j).value
    
    for i in range(1,nrows):
        val_norm = table[i][2]
        nedm_pk = table[i][3]
        nedm = m.NeuronEphysDataMap.objects.get(pk=nedm_pk)
        print nedm.pk, val_norm
        if val_norm == 'None':
            val_norm = None

        nedm.val_norm = val_norm
        nedm.save()

def clean_nedms_post_review():
    normalizeNedms()
    # need to manually clean up adaptation ratio, rheobase
    update_summary_fields()
    e = m.EphysProp.objects.get(pk = 19)
    e.name = 'fast AHP amplitude'
    e.save()
    e = m.EphysProp.objects.get(pk = 21)
    e.name = 'slow AHP amplitude'
    e.save()
    e = m.EphysProp.objects.get(pk = 20)
    e.name = 'fast AHP duration'
    e.save()
    e = m.EphysProp.objects.get(pk = 22)
    e.name = 'slow AHP duration'
    e.save()
    u = m.Unit.objects.create(name='ratio', prefix = '')
    e = m.EphysProp.objects.get(name='sag ratio')
    e.units = u
    e.save()
    e = m.EphysProp.objects.get(name='adaptation ratio')
    e.units = u
    e.save()
    e = m.EphysProp.objects.get(name='Spontaneous firing rate')
    e.name = 'spontaneous firing rate'
    e.save()
    u = m.Unit.objects.create(name='Hz/nA', prefix = '')
    e = m.EphysProp.objects.get(name='FI slope')
    e.units = u
    e.save()
    assign_neuron_neuron_db_ids()

    # goes through tables and removes algorithmically mis-tagged elements
    dts = m.DataTable.objects.filter(datasource__ephysconceptmap__isnull = False)
    filt_dts = dts.filter(datasource__ephysconceptmap__times_validated__gte = 1).distinct()
    for dt in filt_dts:
        ecms = m.EphysConceptMap.objects.filter(source__data_table = dt, times_validated__lt = 1).distinct()
        for ecm in ecms:
            ecms.delete()

def fix_neurolex_ids():
    """
    Fixes for NeuroLex ids that have been deprecated or whose Ephys_prop_definitions_4
    have changed.  
    """

    # nifext_53 has been deprecated in favor of nifext_52.  
    neurons = m.Neuron.objects.filter(nlex_id='nifext_53')
    for neuron in neurons:
        neuron.nlex_id = 'nifext_52'
        neuron.save()

    # Some sao2128417084 should be nifext_50 because the former used to be
    # erroneously described as being part of layer 5/6, when only the latter is
    # actually restricted to layer 5/6.  
    #neurons = n.objects.filter(nlex_id='sao2128417084')
    #for neuron in neurons:
    #    pass
    
    # terminal command for dumping fields from db: python manage.py dumpdata neuroelectro.neuronconceptmap neuroelectro.ephysconceptmap neuroelectro.neuronephysdatamap neuroelectro.expfactconceptmap neuroelectro.user neuroelectro.uservalidation --indent 2  > concept_map_dump.json 

# required for updating concept_map_histories
def fix_db_fields_pre_historical_records():
    initialize_concept_map_fields()
    make_unique_dt_ids_from_usersubmission()
    make_unique_dt_ids_from_data_table()
    
def get_old_shreejoy_user_list():
    old_shreejoy_user_list = list(m.User.objects.filter(email='stripat3@gmail.com'))
    old_shreejoy_user_list.append(m.User.objects.get(username = 'neuronJoy'))
    old_shreejoy_user_list.append(m.get_anon_user())

    return old_shreejoy_user_list
    
# updates HistoricalRecord fields on concept maps
def update_concept_map_histories():
    with open("concept_map_dump.json") as f:
        filecontents = simplejson.load(f)
        
    # read user and user validation objects from json dumpfile
    user_dict = {}
    user_validation_dict = {}
    len_file_contents = len(filecontents)
    for i,f in enumerate(filecontents):
        if f["model"] == "neuroelectro.user":
            user_dict[f["pk"]] = f["fields"]
        if f["model"] == "neuroelectro.uservalidation":
            user_validation_dict[f["pk"]] = f["fields"]
    
    stripat3_user = m.User.objects.get(pk = 96)
    
    old_shreejoy_user_list = get_old_shreejoy_user_list()
    # go through every concept map object and populate history objects
    for i,f in enumerate(filecontents):
        prog(i, len_file_contents)
        if f["model"] == "neuroelectro.neuronconceptmap":
            pk = f["pk"]
            try:
                cm_object = m.NeuronConceptMap.objects.get(pk = pk)
                update_concept_map_with_user(f, cm_object, user_validation_dict, stripat3_user, old_shreejoy_user_list)
            except Exception:
                continue
        if f["model"] == "neuroelectro.ephysconceptmap":
            pk = f["pk"]
            try:
                cm_object = m.EphysConceptMap.objects.get(pk = pk)
                update_concept_map_with_user(f, cm_object, user_validation_dict, stripat3_user, old_shreejoy_user_list)
            except Exception:
                continue
        if f["model"] == "neuroelectro.expfactconceptmap":
            pk = f["pk"]
            try:
                cm_object = m.ExpFactConceptMap.objects.get(pk = pk)
                update_concept_map_with_user(f, cm_object, user_validation_dict, stripat3_user, old_shreejoy_user_list)
            except Exception:
                continue
        if f["model"] == "neuroelectro.neuronephysdatamap":
            pk = f["pk"]
            try:
                cm_object = m.NeuronEphysDataMap.objects.get(pk = pk)
                update_concept_map_with_user(f, cm_object, user_validation_dict, stripat3_user, old_shreejoy_user_list)
            except Exception:
                continue
    

# function to update concept maps, used in update_concept_map_histories
def update_concept_map_with_user(cm_json, cm_object, user_validation_dict, stripat3_user, old_shreejoy_user_list):
    validated_by = cm_json["fields"]["validated_by"]
    if len(validated_by) == 0 and cm_json["fields"]["times_validated"] > 0:
        cm_object.changed_by = stripat3_user
        cm_object.save()
    elif len(validated_by) > 0:
        for uv in validated_by:
            user_pk = user_validation_dict[uv]['user']
            user = m.User.objects.get(pk = user_pk)
            # harmonize old shreejoy accounts to a single user
            if user in old_shreejoy_user_list:
                user = stripat3_user
            cm_object.changed_by = user
            cm_object.save()
            
def make_unique_dt_ids_from_usersubmission():
    uses = m.UserSubmission.objects.all()
    for us in uses:
        cnt = 0
        ncms = m.NeuronConceptMap.objects.filter(source__user_submission = us)
        for ncm in ncms:
            ncm.dt_id = 'th-%d' % cnt
            ncm.save()
            cnt += 1
        ecms = m.EphysConceptMap.objects.filter(source__user_submission = us)
        for ecm in ecms:
            ecm.dt_id = 'th-%d' % cnt
            ecm.save()
            cnt += 1
        cnt = 0
        nedms = m.NeuronEphysDataMap.objects.filter(source__user_submission = us)
        for nedm in nedms:
            nedm.dt_id = 'td-%d' % cnt
            nedm.save()
            cnt += 1

def make_unique_dt_ids_from_data_table():
    #make_unique_dt_ids_from_usersubmission()
    cms = m.NeuronEphysDataMap.objects.all()
    for cm in cms:
        qs = m.NeuronEphysDataMap.objects.filter(source = cm.source, dt_id = cm.dt_id).order_by('-date_mod')
        if qs[0].source.user_submission:
            continue
        for q in qs[1:]:
            q.delete()
    cms = m.EphysConceptMap.objects.all()
    for cm in cms:
        qs = m.EphysConceptMap.objects.filter(source = cm.source, dt_id = cm.dt_id).order_by('-date_mod')
        if qs[0].source.user_submission:
            continue
        for q in qs[1:]:
            q.delete()
    cms = m.NeuronConceptMap.objects.all()
    for cm in cms:
        qs = m.NeuronConceptMap.objects.filter(source = cm.source, dt_id = cm.dt_id).order_by('-date_mod')
        if qs[0].source.user_submission:
            continue
        for q in qs[1:]:
            q.delete()    
            
def initialize_concept_map_fields():
    stripat3_user = m.User.objects.get(pk = 96)
    old_shreejoy_user_list = get_old_shreejoy_user_list()

    for cm in m.NeuronConceptMap.objects.all():
        initialize_concept_map(cm, stripat3_user, old_shreejoy_user_list)
    for cm in m.EphysConceptMap.objects.all():
        initialize_concept_map(cm, stripat3_user, old_shreejoy_user_list)
    for cm in m.NeuronEphysDataMap.objects.all():
        initialize_concept_map(cm, stripat3_user, old_shreejoy_user_list)
    for cm in m.NeuronEphysDataMap.objects.all():
        initialize_concept_map(cm, stripat3_user, old_shreejoy_user_list)
        
    
def initialize_concept_map(cm, stripat3_user, old_shreejoy_user_list):
    field_changed_flag = False
    if cm.note:
        cm.note = re.sub('_', ' ', cm.note)
        field_changed_flag = True
    if hasattr(cm, 'neuron_long_name'):
        if cm.neuron_long_name:
            cm.neuron_long_name = re.sub('_', ' ', cm.neuron_long_name)
            field_changed_flag = True
    adding_user = cm.added_by
    if adding_user in old_shreejoy_user_list:
        cm.added_by = stripat3_user
        field_changed_flag = True
    if field_changed_flag:
        cm.save()


def identify_ephys_units():
    """Iterates through ephys concept map objects and assigns an identified_unit field if found"""
    ecms = m.EphysConceptMap.objects.all()
    ecm_count = ecms.count()
    print "adding units to ephys concept maps"
    for i,ecm in enumerate(ecms):
        prog(i,ecm_count)
        ref_text = ecm.ref_text
        identified_unit = get_units_from_table_header(ref_text)
        try:
            if identified_unit:
                ecm.identified_unit = identified_unit
                ecm.save()
        except Exception:
            pass


def normalize_all_nedms():
    """Iterate through all neuroelectro NeuronEphysDataMap objects and normalize for differences in units"""
    nedms = m.NeuronEphysDataMap.objects.filter(neuron_concept_map__times_validated__gt = 0)
    nedm_count = nedms.count()
    for i,nedm in enumerate(nedms):
        prog(i, nedm_count)
        norm_dict = normalize_nedm_val(nedm)
        if nedm.val_norm is None:
            # if no normalized value
            nedm.val_norm = norm_dict['value']
            nedm.err_norm = norm_dict['error']
            nedm.save()
        elif np.isclose(nedm.val, nedm.val_norm):
            # if there is a normalized value, but it's the same as the unnormalized value
            # so it may need to be updated
            norm_value = norm_dict['value']

            if norm_value is None:
                # can't normalize value but there's an existing one in the database
                # so keep it as long as it's in an appropriate range

                if check_data_val_range(nedm.val_norm, nedm.ephys_concept_map.ephys_prop) is False:
                    print 'deleting pre-normalized value of %s because out of appropriate range for %s ' % (nedm.val_norm, nedm.ephys_concept_map.ephys_prop )
                    nedm.val_norm = None
                    nedm.err_norm = None
                    nedm.save()
                pass
            elif np.isclose(norm_value, nedm.val_norm):
                # new normalized value same as old normalized value, so do nothing
                pass
                # nedm.err_norm = norm_dict['error']
                # nedm.save()
            else:
                # save nedm value
                nedm.val_norm = norm_value
                nedm.err_norm = norm_dict['error']
                nedm.save()
                # normalizing basically failed for some reason
        else:
            # there's a normalized value but it's different from what the algorithm suggests, so it's likely manually added
            if check_data_val_range(nedm.val_norm, nedm.ephys_concept_map.ephys_prop) is False:
                print 'deleting pre-normalized value of %s because out of appropriate range for %s ' % (nedm.val_norm, nedm.ephys_concept_map.ephys_prop )
                nedm.val_norm = None
                nedm.err_norm = None
                nedm.save()
            else:
                nedm.err_norm = norm_dict['error']
                nedm.save()

        #print nedm.pk, nedm.val, nedm.val_norm, nedm.err, nedm.err_norm


def assign_expert_validated():
    """Iterate through all concept maps and assign whether an expert has curated them"""

    cm_expert_list = []

    ncms = m.NeuronConceptMap.objects.filter(times_validated__gt = 0)
    for ncm in ncms:
        if check_for_expert_curator(ncm):
            cm_expert_list.append(ncm)
    ecms = m.EphysConceptMap.objects.filter(times_validated__gt = 0)
    for ecm in ecms:
        if check_for_expert_curator(ecm):
            cm_expert_list.append(ecm)
    efcms = m.ExpFactConceptMap.objects.filter(times_validated__gt = 0)
    for efcm in efcms:
        if check_for_expert_curator(efcm):
            cm_expert_list.append(efcm)

    # for neuron ephys data maps, expert validated if in right range and also curated by an expert
    nedms = m.NeuronEphysDataMap.objects.filter(neuron_concept_map__times_validated__gt = 0)
    for nedm in nedms:
        # nedm check works if curator valided neuron concept
        if check_for_expert_curator(nedm.neuron_concept_map):
            if nedm.val_norm:
                cm_expert_list.append(nedm)
        else:
            nedm.expert_validated = False
            nedm.save()

    # actually update objects
    cm_expert_list_len = len(cm_expert_list)
    for i,cm in enumerate(cm_expert_list):
        prog(i,cm_expert_list_len)
        if cm.expert_validated:
            continue
        else:
            cm.expert_validated = True
            # don't actually update the changed date
            hcm = cm.history.all()[0]
            cm._history_date = hcm.history_date
            cm.save(new_history_time = True)


def check_for_expert_curator(concept_map_ob):
    """Takes a single neuroelectro.models conceptmap object and checks if it's been curated by an expert"""

    # TODO: could be more sophisitcated, like checking if expert curators actually curated concept map when it had same identity

    # expert curators are Brenna and Shreejoy
    expert_curators = m.User.objects.filter(first_name__in = ['Shreejoy', 'Brenna'])

    changing_users = concept_map_ob.get_changing_users()
    if len(set(changing_users).intersection(set(expert_curators))) > 0:
        return True
    else:
        return False

    #
    # for hcm in concept_map_ob.history.all():
    #     if hcm.changed_by in expert_curators:
    #         return True
    # return False


def add_unreported_to_jxn_potential():
    """Adds the field 'Unreported' to metadata property JxnPotential"""

    md = m.MetaData.objects.get_or_create(name = 'JxnPotential', value = 'Unreported')[0]

    human_curated_articles = m.Article.objects.filter(articlefulltext__articlefulltextstat__metadata_human_assigned = True)
    article_count = human_curated_articles.count()
    for i, a in enumerate(human_curated_articles):
        prog(i, article_count)
        curr_jxn_amdms = m.ArticleMetaDataMap.objects.filter(article = a, metadata__name = 'JxnPotential')
        if curr_jxn_amdms.count() == 0:
            # print 'saving object %s to %s, %s' % (md, a, a.pk)
            # update
            update_amd_obj(a, md)

