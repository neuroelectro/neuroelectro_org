
# Methods to restore the database after the migration. applied by Rick.  
import sys
import pickle
import neuroelectro.models as m
import xlrd
import re
from db_add import add_single_article_full
from full_text_pipeline import add_multiple_full_texts_all, ephys_table_identify
from full_text_pipeline import apply_neuron_article_maps, apply_article_metadata

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