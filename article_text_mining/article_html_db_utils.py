__author__ = 'shreejoy'


from bs4 import BeautifulSoup
from article_text_mining.mine_ephys_prop_in_table import assocDataTableEphysVal, find_ephys_headers_in_table
from article_text_mining.article_text_processing import remove_spurious_table_headers

import neuroelectro.models as m


def add_table_ob_to_article(table_html, article_ob, text_mine = True):
    table_soup = BeautifulSoup(table_html)
    table_html_cleaned = str(table_soup)
    table_html_cleaned = add_id_tags_to_table(table_html_cleaned)
    table_text = table_soup.get_text()
    table_text = table_text[0:min(9999,len(table_text))]
    data_table_ob = m.DataTable.objects.get_or_create(article = article_ob, table_html = table_html_cleaned, table_text = table_text)[0]
    data_table_ob = remove_spurious_table_headers(data_table_ob) # takes care of weird header thing for elsevier xml tables
    ds = m.DataSource.objects.get_or_create(data_table=data_table_ob)[0]

    # apply initial text mining of ephys concepts to table
    if text_mine:
        assocDataTableEphysVal(data_table_ob)

    return data_table_ob


def add_id_tags_to_table(table_html):
    """Adds unique html id elements to each cell within html data table"""

    try:
        soup = BeautifulSoup(table_html)
    except:
        return
    if len(soup.find_all(id=True)) < 5:
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