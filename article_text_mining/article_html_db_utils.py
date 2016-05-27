import os

import pandas as pd
from django.conf import settings
from django.core.files import File
from article_text_mining import assign_metadata
from ace import database
from db_functions.pubmed_functions import add_single_article_full
from neuroelectro import models as m
from scripts.dbrestore import prog

__author__ = 'shreejoy'


from bs4 import BeautifulSoup
from article_text_mining.mine_ephys_prop_in_table import assocDataTableEphysVal, find_ephys_headers_in_table
from article_text_mining.article_text_processing import remove_spurious_table_headers

import neuroelectro.models as m


def add_table_ob_to_article(table_html, article_ob, text_mine = True, uploading_user = None):
    if uploading_user:
        user_uploaded = True
    else:
        user_uploaded = False
    table_soup = BeautifulSoup(table_html, 'lxml')
    table_html_cleaned = str(table_soup)
    table_html_cleaned = add_id_tags_to_table(table_html_cleaned)
    table_text = table_soup.get_text()
    table_text = table_text[0:min(9999,len(table_text))]
    data_table_ob = m.DataTable.objects.get_or_create(article = article_ob,
                                                      table_html = table_html_cleaned,
                                                      table_text = table_text,
                                                      uploading_user = uploading_user,
                                                      user_uploaded = user_uploaded
                                                      )[0]
    data_table_ob = remove_spurious_table_headers(data_table_ob) # takes care of weird header thing for elsevier xml tables
    ds = m.DataSource.objects.get_or_create(data_table=data_table_ob)[0]

    # apply initial text mining of ephys concepts to table
    if text_mine:
        assocDataTableEphysVal(data_table_ob)

    return data_table_ob


def add_id_tags_to_table(table_html):
    """Adds unique html id elements to each cell within html data table"""

    try:
        soup = BeautifulSoup(table_html, 'lxml')
    except:
        return
    if len(soup.find_all(id=True)) < 20:
        # contains no id tags, add them
        tdTags = soup.findAll('td')
        cnt = 1
        for tag in tdTags:
            tag['id'] = 'td-%d' % cnt
            cnt += 1
        thTags = soup.findAll('th')
        cnt = 1
        for tag in thTags:
            tag['id'] = 'th-%d' % cnt
            cnt += 1
        trTags = soup.findAll('tr')
        cnt = 1
        for tag in trTags:
            tag['id'] = 'tr-%d' % cnt
            cnt += 1

    table_html = str(soup)
    return table_html


def add_single_full_text(file_name_path, pmid_str, require_mined_ephys = True, require_sections = True, overwrite_existing = False):
    """Given a path to a html article full text, add pubmed ID, it to the database
        Will check if it has text-minable ephys properties in a data table and
        identifiable methods sections if prompted
    """

    # check if article is review article - only easy for Frontiers and PLoS
    # is_research_article = check_research_article(file_name)
    #
    # if not is_research_article:
    #     continue

    # make decision about whether to add article full text to database
    # for now, only add to DB if any table has a text-mining found ephys concept map
    # and article has a methods section that can be identified

    #print "checking article %s" % pmid_str
    # does article already have full text assoc with it?
    if m.ArticleFullText.objects.filter(article__pmid = pmid_str).count() > 0:
        aft = m.ArticleFullText.objects.get(article__pmid = pmid_str)
        if len(aft.get_content()) > 0:
            #print "Article %s full text already in db, skipping..." % pmid_str
            return aft.article

    has_ecm_in_table = False

    html_tables = []

    # access ACE database instance

    db = database.Database('sqlite')
    article_sections = db.file_to_sections(file_name_path, pmid_str, metadata_dir=None, source_name=None, get_tables = False)

    if require_sections:
        if article_sections is None :
            #print "can't identify publisher of article %s:" % pmid_str
            return
        elif 'methods' not in article_sections:
            #print "ACE not able to identify any sections in %s" % pmid_str
            return

    # use ACE to get data tables associated with article if they need to be downloaded
    if article_sections and 'table1' not in article_sections:
        article_sections = db.file_to_sections(file_name_path, pmid_str, metadata_dir=None, source_name=None, get_tables = True)

    if article_sections and len(article_sections) > 0:
        for key, value in iter(sorted(article_sections.iteritems())):   # iter on both keys and values
            if key.startswith('table'):
                html_tables.append(value)

    # check whether tables has a min number of ephys properties which can be mined
    if require_mined_ephys:
        ephys_concept_min_num = 2
        for t in html_tables:
            ephys_concept_dict = find_ephys_headers_in_table(t, early_stopping = True, early_stop_num = ephys_concept_min_num)
            if ephys_concept_dict and len(ephys_concept_dict.keys()) >= ephys_concept_min_num:
                has_ecm_in_table = True
                break

    if require_mined_ephys:
        if has_ecm_in_table:
            article_ob = add_article_full_text_from_file(file_name_path, pmid_str, html_tables, overwrite_existing)
            return article_ob
        else:
            #print "no ephys data found in tables"
            return
    else:
        article_ob = add_article_full_text_from_file(file_name_path, pmid_str, html_tables, overwrite_existing)
        return article_ob


def check_research_article(file_path):
    """Checks whether file is both a research article and has at least one 1 table within"""
    with open(file_path, 'rb') as o:
        html = o.read()
        soup = BeautifulSoup(html, 'lxml')
        article_tag = soup.find('article', attrs={"article-type": "research-article"})
        table_tag = soup.find('table')

        if article_tag and table_tag:
            return True


def add_article_full_text_from_file(abs_path, pmid, html_table_list, overwrite_existing = False):

    a = add_single_article_full(int(pmid), overwrite_existing)
    if a is None:
        return None

    # does article already have full text assoc with it?
    if m.ArticleFullText.objects.filter(article__pmid = pmid).count() > 0:
        aft = m.ArticleFullText.objects.get(article = a)
        if len(aft.get_content()) > 0:
            print "Article %s full text already in db, skipping..." % pmid
            return None

    try:
        print 'adding article %s' % (pmid)
        f = open(unicode(abs_path), 'r')
        file_ob = File(f)
        os.chdir(settings.PROJECT_BASE_DIRECTORY)
        aft = m.ArticleFullText.objects.get_or_create(article = a)[0]
        aft.full_text_file.save(pmid, file_ob)
        file_ob.close()

        for table in html_table_list:
            add_table_ob_to_article(table, a, text_mine = True)

        # text mine article level metadata
        apply_article_metadata(a)

    except Exception, e:
        # with open('failed_files.txt', 'a') as f:
        #     f.write('%s\\%s' % (file_name, e))
        print e
        print pmid
    finally:
        f.close()

    return a


def apply_article_metadata(article = None):
    if article:
        artObs = [article]
        num_arts = 1
    else:
    #    artObs = m.Article.objects.filter(metadata__isnull = True, articlefulltext__isnull = False).distinct()
        artObs = m.Article.objects.filter(articlefulltext__isnull = False).distinct()
    #    artObs = artObs.exclude(articlefulltext__articlefulltextstat__metadata_processed = True)


    #    artObs = m.Article.objects.filter(articlefulltext__isnull = False, articlefulltext__articlefulltextstat__methods_tag_found = True).distinct()
    #    artObs = artObs.exclude(articlefulltext__articlefulltextstat__metadata_processed = True)
    #    artObs = artObs.exclude(articlefulltext__articlefulltextstat__metadata_human_assigned = True)
        num_arts = artObs.count()
        print 'annotating %s articles for metadata...' % num_arts
    for i,art in enumerate(artObs):
        if not article:
            prog(i,num_arts)
        assign_metadata.assign_species(art)
        assign_metadata.assign_electrode_type(art)
        assign_metadata.assign_strain(art)
        assign_metadata.assign_rec_temp(art)
        assign_metadata.assign_prep_type(art)
        assign_metadata.assign_animal_age(art)
        assign_metadata.assign_jxn_potential(art)
        assign_metadata.assign_solution_concs(art)
        aft_ob = art.get_full_text()
        aftStatOb = m.ArticleFullTextStat.objects.get_or_create(article_full_text = aft_ob)[0]
        aftStatOb.metadata_processed = True
        aftStatOb.save()


def process_uploaded_table(table_file, table_name, table_title, table_legend, associated_text):
    """takes an uploaded data table and associated metadata like legend and title and creates an html
        data table"""
    # convert file to pandas data frame
    pd.set_option('display.max_colwidth', 100)
    df = pd.read_csv(table_file, prefix = '', encoding = 'utf-8', index_col=False)
    num_cols = len(df.columns)
    table_html = df.to_html(index = False,na_rep = '', sparsify = False)

    # now use beautiful soup to append the table metadata

    table_soup = BeautifulSoup(table_html)
    table_tag = table_soup.table

    title_tag = table_soup.new_tag("caption")
    title_tag.string = "%s: %s" % (table_name, table_title)
    table_tag.insert(0, title_tag)

    table_body_tag = table_soup.find("tbody")

    legend_str = "%s: %s" % (table_legend, associated_text)
    footer_tag = BeautifulSoup('<tfoot><tr><td colspan="%d">%s</td></tr></tfoot>' % (num_cols, legend_str))
    table_body_tag.insert_after(footer_tag)

    # iterate through all th tags and check if they contain a string like "Unnamed: 0" and remove
    thTags = table_soup.findAll('th')
    for tag in thTags:
        if 'Unnamed' in tag.string:
            tag.string = ''
    return str(table_soup)
