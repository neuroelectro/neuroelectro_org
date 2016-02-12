from django.conf import settings

import ace
from ace.review_downloaded_articles import download_misdownloaded_articles

__author__ = 'stripathy'


def review_full_text_dirs():
    """Adds full texts from directory to DB based on rules specified in full_text_pipeline"""

    if hasattr(settings, 'FULL_TEXTS_LOCAL_DIRECTORY'):
        full_text_dir = settings.FULL_TEXTS_LOCAL_DIRECTORY
    else:
        full_text_dir = settings.FULL_TEXTS_DIRECTORY
    #matching_journ_str = 'Hippocampus'

    #journal_review_list = ['Brain Research', 'Cell', 'Neurobiol Dis', 'Neuroscience', 'Neuroscience Letters']
    #journal_review_list = ['Cell']
    journal_review_list = ['Frontiers in Behavioral Neuroscience', 'Frontiers in Cellular Neuroscience', 'Frontiers in Computational Neuroscience',
                            'Frontiers in Human Neuroscience', 'Frontiers in Integrative Neuroscience', 'Frontiers in Molecular Neuroscience',
                            'Frontiers in Molecular Neuroscience', 'Frontiers in Neural Circuits', 'Frontiers in Neuroanatomy', 'Frontiers in Neuroscience',
                            'Frontiers in Systems Neuroscience', 'Frontiers in Synaptic Neuroscience',
                            'Frontiers in Neurodegeneration',  'Frontiers in Neurogenomics', 'Frontiers in Neuroendocrine Science',
                            'Frontiers in Neurogenesis', 'Frontiers in Neuropharmacology,'
                            ]

    for j in journal_review_list:
        print 'reviewing and redownloading journal %s' % j
        journal_dir = full_text_dir + j
        download_misdownloaded_articles(journal_dir)

def run():
    review_full_text_dirs()
