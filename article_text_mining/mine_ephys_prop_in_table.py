# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup

from article_text_mining.text_mining_util_fxns import fuzzy_match_term_to_list, resolve_table_header, has_ascii_letters
from article_text_mining.unit_conversion import parse_units_from_str
from neuroelectro import models as m

__author__ = 'stripathy'


def match_ephys_header(header_str, ephys_synonym_list):
    """Given a data table header string, returns closest matching ephys prop object
        or None if no ephys synonym has a high match

    Args:
        header_str: header string from a data table
        ephys_synonym_list: the list of strings representing ephys synonyms

    Returns:
        An EphysProp neuroelectro.models object whose Ephys Synonym
        best matches the header_str if match is higher than threshold,
        or None otherwise
        example:

        <EphysProp: Input resistance>

    """
    synapse_stop_words = get_synapse_stop_words()  # a list of stop words relating to synapse terms

    (normHeader, insideParens, commaStr) = resolve_table_header(header_str)
    best_matching_ephys_syn = fuzzy_match_term_to_list(normHeader, ephys_synonym_list)
    if best_matching_ephys_syn: # if it's not None
        if any(substring in normHeader for substring in synapse_stop_words):
            # if header contains a synaptic plasticity term, then dont associate it to anything
            return None

        # find ephys prop matching synonym term
        ephysPropQuerySet = m.EphysProp.objects.filter(synonyms__term = best_matching_ephys_syn)
        if ephysPropQuerySet.count() > 0:
            ephysPropOb = ephysPropQuerySet[0]
            if ephysPropQuerySet.count() > 1:
                print 'Multiple ephys properties found matching synonym: %s' % best_matching_ephys_syn
            return ephysPropOb
        else:
            return None
    else:
        return None


def update_ecm_using_text_mining(ecm, ephys_synonym_list=None, verbose_output=True):
    """Updates an EphysConceptMap object using text mining rules

    Args:
        ecm: an EphysConceptMap object for the object to be updated
        ephys_synonym_list: the list of strings representing ephys synonyms
        verbose_output: a bool indicating whether function should print statements
    """
    if not ephys_synonym_list:
        ephysSyns = m.EphysPropSyn.objects.all()
        ephys_synonym_list = [e.term.lower() for e in ephysSyns]

    if not ecm.ref_text: # some light error checking to make sure there's some text for the ecm object
        return

    # get the closest matching ephys prop given the table header reference text
    matched_ephys_prop = match_ephys_header(ecm.ref_text, ephys_synonym_list)

    if matched_ephys_prop is None: # no ephys props matched
        if verbose_output:
            print 'deleting %s, prop: %s' % (ecm.ref_text, ecm.ephys_prop)
        ecm.delete() # remove the EphysConceptMap since none of the updated EphysProps matched it

    elif matched_ephys_prop != ecm.ephys_prop: # different found prop than existing one
        if verbose_output:
            print 'changing %s, to prop: %s, from prop: %s' %(ecm.ref_text, matched_ephys_prop, ecm.ephys_prop)

        ecm.ephys_prop = matched_ephys_prop # update the ecm
        ecm.changed_by = m.get_robot_user()
        ecm.save()


def get_synapse_stop_words():
    """Return a list of words which are common in synapse ephys terms"""
    synapse_stop_words = ['EPSP', 'IPSP', 'IPSC', 'EPSC', 'PSP', 'PSC']
    synapse_stop_words.extend([w.lower() for w in synapse_stop_words])
    return synapse_stop_words


def assocDataTableEphysVal(dataTableOb):
    """Associates a data table object with ephys concept map objects
    """
    dt = dataTableOb
    ds = m.DataSource.objects.get(data_table = dt)
    robot_user = m.get_robot_user()
    if dt.table_text is None:
        return

    ephysSyns = m.EphysPropSyn.objects.all()
    ephysSynList = [e.term.lower() for e in ephysSyns]

    tableTag = dt.table_html
    soup = BeautifulSoup(''.join(tableTag), 'lxml')
    headerTags = soup.findAll('th')
    tdTags = soup.findAll('td')
    allTags = headerTags + tdTags

    for tag in allTags:
        origTagText = tag.get_text()
        tagText = origTagText.strip()

        if 'id' in tag.attrs.keys():
            tag_id = str(tag['id'])
        else:
            tag_id = -1
        if len(tagText) == 0:
            continue
        if has_ascii_letters(tagText) is True:
            # SJT Note - Currently doesn't mine terms in synapse stop words list
            matched_ephys_ob = match_ephys_header(tagText, ephysSynList)

            if matched_ephys_ob:

                save_ref_text = origTagText[0:min(len(origTagText),199)]
                # create EphysConceptMap object
                ephysConceptMapOb = m.EphysConceptMap.objects.get_or_create(ref_text = save_ref_text,
                                                                          ephys_prop = matched_ephys_ob,
                                                                          source = ds,
                                                                          dt_id = tag_id,
                                                                          #match_quality = matchVal,
                                                                          changed_by = robot_user,
                                                                          times_validated = 0)[0]


def get_units_from_table_header(header_str):
    (a, comma_str, parens_str) = resolve_table_header(header_str)
    if parens_str:
        matched_units = parse_units_from_str(parens_str)
        if matched_units:
            return parens_str
    elif comma_str:
        matched_units = parse_units_from_str(parens_str)
        if matched_units:
            return comma_str
    else:
        # split header using whitespace and check if any are units
        for e in reversed(a.split()):
            matched_units = parse_units_from_str(e)
            if matched_units:
                return e
    return None


