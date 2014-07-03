
# Methods to restore the database after the migration. applied by Rick.  
import sys
import pickle
import neuroelectro.models as m
import xlrd
import re
from db_add import add_single_article_full
from full_text_pipeline import add_multiple_full_texts_all, ephys_table_identify
from full_text_pipeline import apply_neuron_article_maps, apply_article_metadata
from compute_field_summaries import *

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
	    
def update_ephys_defs():
    print 'Updating ephys defs'
    table, nrows, ncols = load_ephys_defs()
    for i in range(1,nrows):
        ephysProp = table[i][0]
    	rawSyns = table[i][2]
    	ephysDef = table[i][1]
    	unit = table[i][3]
    	unit_main = table[i][4]
    	unit_sub = table[i][5]
    	ephysOb = m.EphysProp.objects.get_or_create(name = ephysProp)[0]
    	if unit_main != '':
            u = m.Unit.objects.get_or_create(name = '%s' % unit_main, prefix = '%s' % unit_sub)[0]
    	    ephysOb.units = u
    	if ephysDef != '':
             ephysOb.definition = ephysDef
    	print u.pk,ephysDef
        ephysOb.save()
        synList = [ephysProp]
        for s in rawSyns.split(','):
            s = re.sub('<[\w/]+>', '', s)
            s = s.strip()
            synList.append(s)
        synList= list(set(synList))
        for s in synList:
            print s
            ephysSynOb = m.EphysPropSyn.objects.get_or_create(term = s)[0]
            ephysOb.synonyms.add(ephysSynOb)
        print synList

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
	
def load_ephys_defs():
    print 'Loading ephys defs'
    book = xlrd.open_workbook("data/Ephys_prop_definitions_3.xlsx")
    #os.chdir('C:\Python27\Scripts\Biophys')
    sheet = book.sheet_by_index(0)
    ncols = sheet.ncols
    nrows = sheet.nrows

    table= [ [ 0 for i in range(ncols) ] for j in range(nrows ) ]
    for i in range(nrows):
        for j in range(ncols):
            table[i][j] = sheet.cell(i,j).value
    return table, nrows, ncols

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


def add_full_texts():
    wiley_path = '/home/shreejoy/full_texts/wiley_html'
    elsevier_path = '/home/shreejoy/full_texts/elsevier_xml'
    highwire_path = '/home/shreejoy/full_texts/neuro_full_texts'
    print 'adding highwire full texts'
    add_multiple_full_texts_all(highwire_path)
    print 'adding wiley full texts'
    add_multiple_full_texts_all(wiley_path)
    print 'adding elsevier full texts'
    add_multiple_full_texts_all(elsevier_path)


def annotate_full_texts():
    print 'adding neuron article maps'
    apply_neuron_article_maps()
    print 'annotating data table ephys props'
    ephys_table_identify()
    print 'annotating articles for metadata'
    apply_article_metadata()

def convert_article_metadata_maps():
    articles = m.Article.objects.filter(metadata__isnull = False)
    num_articles = articles.count()
    for i,a in enumerate(articles):
        prog(i, num_articles)
        md_obs = a.metadata.all()
        for md in md_obs:
            a.metadata.remove(md)
            amdm = m.ArticleMetaDataMap.objects.get_or_create(article = a, metadata = md, added_by = md.added_by)[0]

def update_summary_fields():
    print 'updating field summaries'
    computeNeuronEphysSummariesAll()
    computeEphysPropSummaries()
    computeEphysPropValueSummaries()
    computeNeuronSummaries()
    computeArticleSummaries()

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
    