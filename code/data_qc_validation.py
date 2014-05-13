import numpy
from neuroelectro.models import Article, MeshTerm, Substance, Journal
from neuroelectro.models import Neuron, NeuronSyn, Unit, ArticleMetaDataMap
from neuroelectro.models import BrainRegion, InSituExpt, Protein, RegionExpr
from neuroelectro.models import DataTable, ArticleFullText, EphysConceptMap, MetaData
from neuroelectro.models import EphysProp, EphysPropSyn, NeuronArticleMap, get_robot_user
from neuroelectro.models import NeuronConceptMap, NeuronArticleMap, NeuronEphysDataMap
from neuroelectro.models import ArticleSummary, NeuronSummary, EphysPropSummary, NeuronEphysSummary
from neurotree.neuroelectro_integration import define_ephys_grandfathers
from neurotree.author_search import get_article_last_author, get_neurotree_author

from django.db.models import Count, Min, Q
from get_ephys_data_vals_all import filterNedm
import re
import numpy as np
import csv,codecs,cStringIO
import nltk
import random

def getAllArticleNedmMetadataSummary():
    
    articles = Article.objects.filter(Q(datatable__datasource__neuronconceptmap__times_validated__gte = 1) | 
        Q(usersubmission__datasource__neuronconceptmap__times_validated__gte = 1)).distinct()
    articles = articles.filter(articlefulltext__articlefulltextstat__metadata_human_assigned = True ).distinct()
    nom_vars = ['Species', 'Strain', 'ElectrodeType', 'PrepType', 'JxnPotential']
    cont_vars  = ['JxnOffset', 'RecTemp', 'AnimalAge', 'AnimalWeight']
    cont_var_headers = ['JxnOffset', 'Temp', 'Age', 'Weight']
    num_nom_vars = len(nom_vars)
    #ephys_use_pks = [2, 3, 4, 5, 6, 7]
    #ephys_headers = ['ir', 'rmp', 'tau', 'amp', 'hw', 'thresh']
    ephys_use_pks = range(1,28)

    ephys_list = EphysProp.objects.filter(pk__in = ephys_use_pks)
    ephys_headers = []
    for e in ephys_list:
        ephys_name_str = e.name
        ephys_name_str = ephys_name_str.title()
        ephys_name_str = ephys_name_str.replace(' ', '')
        ephys_name_str = ephys_name_str.replace('-', '')
        ephys_headers.append(ephys_name_str)

    #ephys_headers = [e.name for e in ephys_list]
#    metadata_table = []
#    metadata_table_nom = np.zeros([len(articles), len(nom_vars)])
#    metadata_table_nom = np.zeros([len(articles), len(cont_vars)])
    csvout = csv.writer(open("article_ephys_metadata_summary.csv", "wb"))
    
    
    #metadata_headers = ["Species", "Strain", "ElectrodeType", "PrepType", "Temp", "Age", "Weight"]
    metadata_headers = nom_vars + cont_var_headers
    other_headers = ['NeuronType', 'Title', 'PubYear', 'PubmedLink', 'DataTableLinks', 'ArticleDataLink', 'LastAuthor']
    all_headers = ephys_headers
    all_headers.extend(metadata_headers)
    all_headers.extend(other_headers)
    pubmed_base_link_str = 'http://www.ncbi.nlm.nih.gov/pubmed/%d/'
    table_base_link_str = 'http://neuroelectro.org/data_table/%d/'
    article_base_link_str = 'http://neuroelectro.org/article/%d/'

    csvout.writerow(all_headers)
    for j,a in enumerate(articles):
        amdms = ArticleMetaDataMap.objects.filter(article = a)
        curr_metadata_list = ['']*(len(nom_vars) + len(cont_vars))
        for i,v in enumerate(nom_vars):
            valid_vars = amdms.filter(metadata__name = v)
            temp_metadata_list = [vv.metadata.value for vv in valid_vars]
            if 'in vitro' in temp_metadata_list and 'cell culture' in temp_metadata_list:
                curr_metadata_list[i] = 'cell culture'
            elif v == 'Strain' and amdms.filter(metadata__value = 'Mice').count() > 0:
                 temp_metadata_list = 'C57BL'
                 curr_metadata_list[i] = 'C57BL'
            elif v == 'Strain' and amdms.filter(metadata__value = 'Guinea Pigs').count() > 0:
                 temp_metadata_list = 'Guinea Pigs'
                 curr_metadata_list[i] = 'Guinea Pigs'
            elif len(temp_metadata_list) == 0 and v == 'Strain':
                if amdms.filter(metadata__value = 'Rats').count() > 0:
                    if np.random.randn(1)[0] > 0:
                        curr_metadata_list[i] = 'Sprague-Dawley'
                    else:
                        curr_metadata_list[i] = 'Wistar'
            elif len(temp_metadata_list) > 1: 
                 temp_metadata_list = temp_metadata_list[0]
                 curr_metadata_list[i] = temp_metadata_list
            else:
                curr_metadata_list[i] = u'; '.join(temp_metadata_list)
        for i,v in enumerate(cont_vars):
            valid_vars = amdms.filter(metadata__name = v)
            if valid_vars.count() > 0:
                cont_value_ob = valid_vars[0].metadata.cont_value.mean
    #                curr_str = cont_value_ob
                curr_metadata_list[i+num_nom_vars] = cont_value_ob
            else:
                # check if 
                if v == 'RecTemp' and amdms.filter(metadata__value = 'in vivo').count() > 0:
                    curr_metadata_list[i+num_nom_vars] = 37.0
                else:
                    curr_metadata_list[i+num_nom_vars] = 'NaN'
                    
        neurons = Neuron.objects.filter(Q(neuronconceptmap__times_validated__gte = 1) & 
            ( Q(neuronconceptmap__source__data_table__article = a) | Q(neuronconceptmap__source__user_submission__article = a))).distinct()
            
        
        pmid = a.pmid    
        pubmed_link_str = pubmed_base_link_str % a.pmid
        article_link_str = article_base_link_str % a.pk
        dts = DataTable.objects.filter(article = a, datasource__neuronconceptmap__times_validated__gte = 1).distinct()
        if dts.count() > 0:
            dt_link_list = [table_base_link_str % dt.pk for dt in dts] 
            dt_link_str = u'; '.join(dt_link_list)
        else:
            dt_link_str = ''  
        
        #grandfather = define_ephys_grandfather(a)   
        # grandfather = None
        # if grandfather is not None:
        #     grandfather_name = grandfather.lastname
        #     grandfather_name = grandfather_name.encode("iso-8859-15", "replace")
        # else:
        #     grandfather_name = ''
        last_author = get_article_last_author(a)
        if last_author is not None:
            last_author_name = '%s %s' % (last_author.last, last_author.initials)
            last_author_name = last_author_name.encode("iso-8859-15", "replace")
            # if grandfather_name is '':
            #     neuro_tree_node = get_neurotree_author(last_author)
            #     if neuro_tree_node is None:
            #         grandfather_name = 'Node not found'
        else:
            last_author_name = ''
            
        for n in neurons:
            curr_ephys_prop_list = []
            for j,e in enumerate(ephys_list):
                curr_ephys_prop_list.append(computeArticleNedmSummary(pmid, n, e))
        
#            print curr_ephys_prop_list
            curr_ephys_prop_list.extend(curr_metadata_list)
            curr_ephys_prop_list.append(n.name)
            curr_ephys_prop_list.append((a.title).encode("iso-8859-15", "replace"))
            curr_ephys_prop_list.append(a.pub_year)
            curr_ephys_prop_list.append(pubmed_link_str)
            curr_ephys_prop_list.append(dt_link_str)
            curr_ephys_prop_list.append(article_link_str)
            curr_ephys_prop_list.append(last_author_name)
            #curr_ephys_prop_list.append(grandfather_name)
            csvout.writerow(curr_ephys_prop_list)
    return articles

def get_ephys_prop_ordered_list():
    ephys_props = EphysProp.objects.all()
    ephys_props = ephys_props.exclude(id__in = [15, 11, 12, 9, 25])
    ephys_props = ephys_props.order_by('-ephyspropsummary__num_nedms')
    return ephys_props

def write_validation_spreadsheet():
    
    csvout = csv.writer(open("validation_spreadsheet.csv", "wb"))

    with open('validation_spreadsheet.csv','wb') as fout:
        csvout = UnicodeWriter(fout,quoting=csv.QUOTE_ALL)


        pubmed_base_link_str = 'http://www.ncbi.nlm.nih.gov/pubmed/%d/'
        table_base_link_str = 'http://neuroelectro.org/data_table/%d/no_annotation'
        article_base_link_str = 'http://neuroelectro.org/article/%d/'

        nom_vars = ['Species', 'Strain', 'ElectrodeType', 'PrepType', 'JxnPotential']
        cont_vars  = ['JxnOffset', 'RecTemp', 'AnimalAge', 'AnimalWeight']
        num_nom_vars = len(nom_vars)

        curator_names = ['Shreejoy', 'Shawn', 'Rick', 'Matt']

        articles = Article.objects.filter(Q(datatable__datasource__neuronconceptmap__times_validated__gte = 1)).distinct()

        num_selected_articles = int(articles.count()*.1)

        random.seed(0)
        #print random.getstate()
        selected_articles = random.sample(articles, num_selected_articles)

        neuron_row_header = ['','Neuron type', 'Table header', 'Correct? (yes/no/ambiguous)', 'Note']
        ephys_row_header = ['','Ephys prop', 'Table header', 'Correct? (yes/no/ambiguous)', 'Replicable? (yes/no/ambiguous)', 'Note']
        nedm_row_header = ['','Neuron Type (header)', 'Ephys Prop (header)', 'Extracted val', 'Standardized val', 'Note']
        metadata_row_header = ['', 'Metadata property', 'Metadata value', 'Correct? (yes/no/ambiguous)', 'Note']
        for j,a in enumerate(selected_articles):

            pmid = a.pmid    
            pubmed_link_str = pubmed_base_link_str % a.pmid
            article_link_str = article_base_link_str % a.pk
            dts = DataTable.objects.filter(article = a, datasource__neuronconceptmap__times_validated__gte = 1).distinct()
            # if dts.count() > 0:
            #     dt_link_list = [table_base_link_str % dt.pk for dt in dts] 
            #     dt_link_str = u'; '.join(dt_link_list)
            # else:
            #     dt_link_str = ''  

            csvout.writerow(['Article title', (a.title).encode("iso-8859-15", "replace")])
            csvout.writerow(['Full text link', a.full_text_link])
            csvout.writerow([])
            
            for k,dt in enumerate(dts):
                csvout.writerow(['Data table link', table_base_link_str % dt.pk])
                
                # write info about neuron type
                csvout.writerow(neuron_row_header)

                ncms = NeuronConceptMap.objects.filter(Q(times_validated__gte = 1) & 
                    ( Q(source__data_table__article = a)) & Q(neuronephysdatamap__isnull = False) 
                    & Q(source__data_table = dt) ).distinct()
                for ncm in ncms:
                    neuron_name = ncm.neuron.name
                    ncm_ref_text = ncm.ref_text.strip()
                    curr_row = ['',neuron_name, ncm_ref_text]
                    # print curr_row
                    csvout.writerow(curr_row)

                csvout.writerow([])
                csvout.writerow(ephys_row_header)

                # write info about ephys type
                ecms = EphysConceptMap.objects.filter(Q(times_validated__gte = 1) & 
                    Q(source__data_table__article = a) & Q(ephys_prop__in = get_ephys_prop_ordered_list()) &
                    Q(neuronephysdatamap__isnull = False) & Q(source__data_table = dt) ).distinct()
                for ecm in ecms:
                    ephys_name = ecm.ephys_prop.name
                    ecm_ref_text = ecm.ref_text.strip()
                    curator_ind = j % 4
                    print str(j), str(curator_ind)
                    ephys_note = '%s, please add best property definition' % curator_names[curator_ind]
                    curr_row = ['',ephys_name, ecm_ref_text, '', '', ephys_note]
                    # print curr_row
                    csvout.writerow(curr_row)

                # write info about nedms 
                csvout.writerow([])
                csvout.writerow(nedm_row_header)

                nedms = NeuronEphysDataMap.objects.filter(neuron_concept_map__in = ncms, 
                    ephys_concept_map__in = ecms).distinct()
                nedms = nedms.order_by('-neuron_concept_map__pk')
                for nedm in nedms:
                    neuron_name = nedm.neuron_concept_map.neuron.name
                    ephys_name = nedm.ephys_concept_map.ephys_prop.name
                    ncm_ref_text = nedm.neuron_concept_map.ref_text.strip()
                    ecm_ref_text = nedm.ephys_concept_map.ref_text.strip()
                    #print ncm_ref_text, ecm_ref_text
                    curr_row =  ['','%s (%s)' % (neuron_name, ncm_ref_text)  , '%s (%s)' % (ephys_name , ecm_ref_text) ]
                    #print curr_row
                    csvout.writerow(curr_row)
                csvout.writerow([])

            csvout.writerow(metadata_row_header)
            amdms = ArticleMetaDataMap.objects.filter(article = a)
            curr_metadata_list = []

            for i,v in enumerate(nom_vars):
                valid_vars = amdms.filter(metadata__name = v)
                temp_metadata_list = [vv.metadata.value for vv in valid_vars]
                if 'in vitro' in temp_metadata_list and 'cell culture' in temp_metadata_list:
                    metadata_value = 'cell culture'
                elif len(temp_metadata_list) == 0 and v == 'Strain':
                    if amdms.filter(metadata__value = 'Rats').count() > 0:
                        if np.random.randn(1)[0] > 0:
                            metadata_value = 'Sprague-Dawley'
                        else:
                            metadata_value = 'Wistar'
                else:
                    metadata_value = temp_metadata_list
                print metadata_value
                if len(metadata_value) == 0:
                    continue
                csvout.writerow(['', v, ', '.join(metadata_value)])

            for i,v in enumerate(cont_vars):
                valid_vars = amdms.filter(metadata__name = v)
                if valid_vars.count() > 0:
                    cont_value_ob = valid_vars[0].metadata.cont_value
        #                curr_str = cont_value_ob
                    metadata_value = cont_value_ob
                else:
                    # check if 
                    if v == 'RecTemp' and amdms.filter(metadata__value = 'in vivo').count() > 0:
                        metadata_value = 37.0
                    else:
                        metadata_value = 'NaN'
                if metadata_value is 'NaN':
                    continue
                print metadata_value
                csvout.writerow(['', v, unicode(metadata_value)])



            # amdms = ArticleMetaDataMap.objects.filter(neuron_concept_map__in = ncms, ephys_concept_map__in = ecms).distinct()
            # nedms = nedms.order_by('-neuron_concept_map__pk')
            # for nedm in nedms:
            #     neuron_name = nedm.neuron_concept_map.neuron.name
            #     ephys_name = nedm.ephys_concept_map.ephys_prop.name
            #     ncm_ref_text = nedm.neuron_concept_map.ref_text.strip()
            #     ecm_ref_text = nedm.ephys_concept_map.ref_text.strip()
            #     #print ncm_ref_text, ecm_ref_text
            #     curr_row =  ['','%s (%s)' % (neuron_name, ncm_ref_text)  , '%s (%s)' % (ephys_name , ecm_ref_text) ]
            #     #print curr_row
            #     csvout.writerow(curr_row)
            csvout.writerow([])
            csvout.writerow([])



class UTF8Recoder:
    def __init__(self, f, encoding):
        self.reader = codecs.getreader(encoding)(f)
    def __iter__(self):
        return self
    def next(self):
        return self.reader.next().encode("utf-8")

class UnicodeReader:
    def __init__(self, f, dialect=csv.excel, encoding="utf-8-sig", **kwds):
        f = UTF8Recoder(f, encoding)
        self.reader = csv.reader(f, dialect=dialect, **kwds)
    def next(self):
        row = self.reader.next()
        return [unicode(s, "utf-8") for s in row]
    def __iter__(self):
        return self

class UnicodeWriter:
    def __init__(self, f, dialect=csv.excel, encoding="utf-8-sig", **kwds):
        self.queue = cStringIO.StringIO()
        self.writer = csv.writer(self.queue, dialect=dialect, **kwds)
        self.stream = f
        self.encoder = codecs.getincrementalencoder(encoding)()
    def writerow(self, row):
        self.writer.writerow([s.encode("utf-8") for s in row])
        data = self.queue.getvalue()
        data = data.decode("utf-8")
        data = self.encoder.encode(data)
        self.stream.write(data)
        self.queue.truncate(0)

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)