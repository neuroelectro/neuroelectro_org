import csv
import re

from django.conf import settings
from django.db.models import Q
import numpy as np
import pandas as pd

from db_functions.compute_field_summaries import computeArticleNedmSummary
from neuroelectro import models as m
from db_functions.author_search import get_article_last_author
from db_functions.normalize_ephys_data import check_data_val_range, identify_stdev, add_ephys_props_by_conversion
from aba_functions.get_brain_region import get_neuron_region
from scripts.dbrestore import prog

__author__ = 'stripathy'


def export_db_to_data_frame():
    """Returns a nicely formatted pandas data frame of the ephys data and metadata for each stored article"""

    ncms = m.NeuronConceptMap.objects.all()#.order_by('-history__latest__history_date') # gets human-validated neuron mappings
    ncms = ncms.exclude(Q(source__data_table__irrelevant_flag = True) | Q(source__data_table__needs_expert = True)) # exclude
    ncm_count = ncms.count()
    ephys_props = m.EphysProp.objects.all().order_by('-ephyspropsummary__num_neurons')
    ephys_names = []
    for e in ephys_props:
        ephys_names.append(e.short_name)
        ephys_names.append(e.short_name + '_raw')
        ephys_names.append(e.short_name + '_err')
        ephys_names.append(e.short_name + '_n')
        ephys_names.append(e.short_name + '_sd')
        ephys_names.append(e.short_name + '_note')
    #ephys_names = [e.name for e in ephys_props]
    #ncms = ncms.sort('-changed_on')
    dict_list = []
    for kk, ncm in enumerate(ncms):
        prog(kk, ncm_count)

    # TODO: need to check whether nedms under the same ncm have different experimental factor concept maps
    #     # check if any nedms have any experimental factors assoc with them
    #     efcms = ne_db.ExpFactConceptMap.objects.filter(neuronephysdatamap__in = nedms)
    #     for efcm in efcms:
    #         nedms = ne_db.NeuronEphysDataMap.objects.filter(neuron_concept_map = ncm, exp_fact_concept_map = ).distinct()

        nedms = m.NeuronEphysDataMap.objects.filter(neuron_concept_map = ncm, expert_validated = True).distinct()
        if nedms.count() == 0:
            continue

        sd_errors = identify_stdev(nedms)

        temp_dict = dict()
        temp_metadata_list = []
        for nedm in nedms:
            e = nedm.ephys_concept_map.ephys_prop
            # check data integrity - value MUST be in appropriate range for property
            data_val =  nedm.val_norm
            data_raw_val = nedm.val
            err_val = nedm.err_norm
            n_val = nedm.n
            note_val = nedm.ephys_concept_map.note
            output_ephys_name = e.short_name
            output_ephys_raw_name = '%s_raw' % output_ephys_name
            output_ephys_err_name = '%s_err' % output_ephys_name
            output_ephys_sd_name = '%s_sd' % output_ephys_name
            output_ephys_n_name = '%s_n' % output_ephys_name
            output_ephys_note_name = '%s_note' % output_ephys_name

            # output raw vals and notes for all props
            temp_dict[output_ephys_raw_name] = data_raw_val
            temp_dict[output_ephys_note_name] = note_val

            if check_data_val_range(data_val, e):

                temp_dict[output_ephys_name] = data_val
                temp_dict[output_ephys_err_name] = err_val
                temp_dict[output_ephys_n_name] = n_val

                # do converting to standard dev from standard error if needed
                if sd_errors:
                    temp_dict[output_ephys_sd_name] = err_val
                else:
                    # need to calculate sd
                    if err_val and n_val:
                        sd_val = err_val * np.sqrt(n_val)
                        temp_dict[output_ephys_sd_name] = sd_val

            #temp_metadata_list.append(nedm.get_metadata())

        temp_dict['NeuronName'] =  ncm.neuron.name
        temp_dict['NeuronLongName'] =  ncm.neuron_long_name
        if ncm.neuron_long_name:
            temp_dict['NeuronPrefName'] = ncm.neuron_long_name
        else:
            temp_dict['NeuronPrefName'] = ncm.neuron.name
        article = ncm.get_article()

        brain_reg_dict = get_neuron_region(ncm.neuron)
        if brain_reg_dict:
            temp_dict['BrainRegion'] = brain_reg_dict['region_name']

        #article_metadata = normalize_metadata(article)

        metadata_list = nedm.get_metadata()
        out_dict = dict()
        for metadata in metadata_list:
            #print metadata.name
            if not metadata.cont_value:
                if metadata.name in out_dict:
                    out_dict[metadata.name] = '%s, %s' % (out_dict[metadata.name], metadata.value)
                else:
                    out_dict[metadata.name] = metadata.value
            elif metadata.cont_value and 'Solution' in metadata.name:
                article = nedm.get_article()
                amdm = m.ArticleMetaDataMap.objects.filter(article = article, metadata__name = metadata.name)[0]
                ref_text = amdm.ref_text
                out_dict[metadata.name] = ref_text.text.encode('utf8', "replace")
                out_dict[metadata.name + '_conf'] = metadata.cont_value.mean
            elif metadata.cont_value and 'AnimalAge' in metadata.name:
                # return geometric mean of age ranges, not arithmetic mean
                if metadata.cont_value.min_range and metadata.cont_value.max_range:
                    min_range = metadata.cont_value.min_range
                    max_range = metadata.cont_value.max_range
                    if min_range <= 0:
                        min_range = 1
                    geom_mean = np.sqrt(min_range * max_range)
                    out_dict[metadata.name] = geom_mean
                else:
                    out_dict[metadata.name] = metadata.cont_value.mean
            else:
                out_dict[metadata.name] = metadata.cont_value.mean

        # has article metadata been curated by a human?
        afts = article.get_full_text_stat()
        if afts and afts.metadata_human_assigned:
            metadata_curated = True
            metadata_curation_note = afts.metadata_curation_note
        else:
            metadata_curated = False
            metadata_curation_note = None

        if ncm.source.data_table:
            data_table_note = ncm.source.data_table.note
        else:
            data_table_note = None

        temp_dict2 = temp_dict.copy()
        temp_dict2.update(out_dict)
        temp_dict = temp_dict2
        temp_dict['Title'] = article.title
        temp_dict['Pmid'] = article.pmid
        temp_dict['PubYear'] = article.pub_year
        temp_dict['LastAuthor'] = unicode(get_article_last_author(article))
        temp_dict['TableID'] = ncm.source.data_table_id
        temp_dict['TableNote'] = data_table_note
        temp_dict['ArticleID'] = article.pk
        temp_dict['MetadataCurated'] = metadata_curated
        temp_dict['MetadataNote'] = metadata_curation_note
        #print temp_dict
        dict_list.append(temp_dict)

    base_names = ['Title', 'Pmid', 'PubYear', 'LastAuthor', 'ArticleID', 'TableID',
                  'NeuronName', 'NeuronLongName', 'NeuronPrefName', 'BrainRegion']
    nom_vars = ['MetadataCurated', 'Species', 'Strain', 'ElectrodeType', 'PrepType', 'JxnPotential']
    cont_vars  = ['JxnOffset', 'RecTemp', 'AnimalAge', 'AnimalWeight', 'FlagSoln']
    annot_notes = ['MetadataNote', 'TableNote']

    for i in range(0, 1):
        cont_vars.extend([ 'ExternalSolution', 'ExternalSolution_conf', 'external_%s_Mg' % i, 'external_%s_Ca' % i, 'external_%s_Na' % i, 'external_%s_Cl' % i, 'external_%s_K' % i, 'external_%s_pH' % i, 'InternalSolution', 'InternalSolution_conf', 'internal_%s_Mg' % i, 'internal_%s_Ca' % i, 'internal_%s_Na' % i, 'internal_%s_Cl' % i, 'internal_%s_K' % i, 'internal_%s_pH' % i])
        #cont_var_headers.extend(['External_%s_Mg' % i, 'External_%s_Ca' % i, 'External_%s_Na' % i, 'External_%s_Cl' % i, 'External_%s_K' % i, 'External_%s_pH' % i, 'External_%s_text' % i, 'Internal_%s_Mg' % i, 'Internal_%s_Ca' % i, 'Internal_%s_Na' % i, 'Internal_%s_Cl' % i, 'Internal_%s_K' % i, 'Internal_%s_pH' % i, 'Internal_%s_text' % i])

    col_names = base_names + nom_vars + cont_vars + annot_notes + ephys_names

    # set up pandas data frame for export
    df = pd.DataFrame(dict_list, columns = col_names)

    # perform collapsing of rows about same neuron types but potentially across different tables
    cleaned_df = df
    # need to generate a random int for coercing NaN's to something - required for pandas grouping
    rand_int = -abs(np.random.randint(20000))
    cleaned_df.loc[:, 'Pmid':'FlagSoln'] = df.loc[:, 'Pmid':'FlagSoln'].fillna(rand_int)
    grouping_fields = base_names + nom_vars + cont_vars
    grouping_fields.remove('TableID')
    cleaned_df.groupby(by = grouping_fields).mean()
    cleaned_df.replace(to_replace = rand_int, value = np.nan, inplace=True)
    cleaned_df.reset_index(inplace=True)
    cleaned_df.sort_values(by = ['PubYear', 'Pmid', 'NeuronName'], ascending=[False, True, True], inplace=True)
    cleaned_df.index.name = "Index"

    # add in extra ephys data from columns based on known relationships, e.g., AP amp from AP peak and AP thr
    cleaned_df = add_ephys_props_by_conversion(cleaned_df)

    return cleaned_df


def getAllArticleNedmMetadataSummary(getAllMetadata = False):
    """The old function for exporting the DB to a csv file, added here for reference"""
# TODO: uncomment and remove unnecessary metadata
#     articles = m.Article.objects.filter(Q(datatable__datasource__neuronconceptmap__times_validated__gte = 1) |
#         Q(usersubmission__datasource__neuronconceptmap__times_validated__gte = 1)).distinct()
#     articles = articles.filter(articlefulltext__articlefulltextstat__metadata_human_assigned = True ).distinct()
    articles = m.Article.objects.all()

    nom_vars = ['Species', 'Strain', 'ElectrodeType', 'PrepType', 'JxnPotential']
    cont_vars  = ['JxnOffset', 'RecTemp', 'AnimalAge', 'AnimalWeight', 'FlagSoln']
    cont_var_headers = ['JxnOffset', 'Temp', 'Age', 'Weight', 'FlagSoln']
    if getAllMetadata:
        for i in range(0, 5):
            cont_vars.extend(['external_%s_Mg' % i, 'external_%s_Ca' % i, 'external_%s_Na' % i, 'external_%s_Cl' % i, 'external_%s_K' % i, 'external_%s_pH' % i, 'external_%s_text' % i, 'internal_%s_Mg' % i, 'internal_%s_Ca' % i, 'internal_%s_Na' % i, 'internal_%s_Cl' % i, 'internal_%s_K' % i, 'internal_%s_pH' % i, 'internal_%s_text' % i])
            cont_var_headers.extend(['External_%s_Mg' % i, 'External_%s_Ca' % i, 'External_%s_Na' % i, 'External_%s_Cl' % i, 'External_%s_K' % i, 'External_%s_pH' % i, 'External_%s_text' % i, 'Internal_%s_Mg' % i, 'Internal_%s_Ca' % i, 'Internal_%s_Na' % i, 'Internal_%s_Cl' % i, 'Internal_%s_K' % i, 'Internal_%s_pH' % i, 'Internal_%s_text' % i])
    num_nom_vars = len(nom_vars)
    ephys_use_pks = range(1,28)

    ephys_list = m.EphysProp.objects.filter(pk__in = ephys_use_pks)
    ephys_headers = []
    for e in ephys_list:
        ephys_name_str = re.sub("[\s-]", "", e.name.title())
        ephys_headers.append(ephys_name_str)

    csvout = csv.writer(open(settings.OUTPUT_FILES_DIRECTORY + "article_ephys_metadata_curated.csv", "w+b"), delimiter = '\t')

    other_headers = ['NeuronType', 'Title', 'Journal', 'PubYear', 'PubmedLink', 'DataTableLinks', 'ArticleDataLink', 'LastAuthor']
    all_headers = other_headers
    all_headers.extend(ephys_headers)
    all_headers.extend(nom_vars + cont_var_headers)

    pubmed_base_link_str = 'http://www.ncbi.nlm.nih.gov/pubmed/%d/'
    table_base_link_str = 'http://neuroelectro.org/data_table/%d/'
    article_base_link_str = 'http://neuroelectro.org/article/%d/'

    csvout.writerow(all_headers)
    for a in articles:
        print "processing metadata for article: %s" % a.pk
        amdms = m.ArticleMetaDataMap.objects.filter(article = a)
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
                curr_metadata_list[i+num_nom_vars] = cont_value_ob
            else:
                # check if
                if v == 'RecTemp' and amdms.filter(metadata__value = 'in vivo').count() > 0:
                    curr_metadata_list[i+num_nom_vars] = 37.0
                elif 'text' in v and ('external' in v or 'internal' in v):
                    for j in range(i - 6, i - 1, 1):
                        conc_amdm = amdms.filter(metadata__name = cont_vars[j])
                        if len(conc_amdm) > 0:
                            curr_metadata_list[i+num_nom_vars] = conc_amdm[0].metadata.ref_text.text.encode('utf8', "replace")
                            break
                        else:
                            curr_metadata_list[i+num_nom_vars] = 'NaN'
                else:
                    curr_metadata_list[i+num_nom_vars] = 'NaN'

# TODO: uncomment these 2 lines
        neurons = m.Neuron.objects.filter(Q(neuronconceptmap__times_validated__gte = 1) &
            ( Q(neuronconceptmap__source__data_table__article = a) | Q(neuronconceptmap__source__user_submission__article = a))).distinct()
        neurons = m.Neuron.objects.filter( Q(neuronconceptmap__source__data_table__article = a) | Q(neuronconceptmap__source__user_submission__article = a)).distinct()

        pubmed_link_str = pubmed_base_link_str % a.pmid
        article_link_str = article_base_link_str % a.pk
        dts = m.DataTable.objects.filter(article = a, datasource__neuronconceptmap__times_validated__gte = 1).distinct()
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
            last_author_name = last_author_name.encode("utf8", "replace")
            # if grandfather_name is '':
            #     neuro_tree_node = get_neurotree_author(last_author)
            #     if neuro_tree_node is None:
            #         grandfather_name = 'Node not found'
        else:
            last_author_name = ''

        for n in neurons:
            curr_ephys_prop_list = []

            curr_ephys_prop_list.append(n.name)
            curr_ephys_prop_list.append((a.title).encode("utf8", "replace"))
            curr_ephys_prop_list.append(a.journal)
            curr_ephys_prop_list.append(a.pub_year)
            curr_ephys_prop_list.append(pubmed_link_str)
            curr_ephys_prop_list.append(dt_link_str)
            curr_ephys_prop_list.append(article_link_str)
            curr_ephys_prop_list.append(last_author_name)

            for e in ephys_list:
                curr_ephys_prop_list.append(computeArticleNedmSummary(a.pmid, n, e))

            curr_ephys_prop_list.extend(curr_metadata_list)
            #curr_ephys_prop_list.append(grandfather_name)

            csvout.writerow(curr_ephys_prop_list)
    return articles