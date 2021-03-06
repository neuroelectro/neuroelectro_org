from article_text_mining.full_text_pipeline import add_full_texts_from_mult_dirs, add_full_texts_from_directory
from django.conf import settings
__author__ = 'stripathy'


def add_full_texts():
    """Adds full texts from directory to DB based on rules specified in full_text_pipeline"""

    if hasattr(settings, 'FULL_TEXTS_LOCAL_DIRECTORY'):
        full_text_dir = settings.FULL_TEXTS_LOCAL_DIRECTORY
    else:
        full_text_dir = settings.FULL_TEXTS_DIRECTORY

    # matching_journ_str = 'PLoS'
    # print 'Adding full texts from %s journals' % matching_journ_str
    # add_full_texts_from_mult_dirs(full_text_dir, matching_journ_str)
    #
    # matching_journ_str = 'Frontiers'
    # print 'Adding full texts from %s journals' % matching_journ_str
    # add_full_texts_from_mult_dirs(full_text_dir, matching_journ_str)
    # add_full_texts_from_mult_dirs(full_text_dir, 'PLoS Comput Biol')
    #
    # add_full_texts_from_mult_dirs(full_text_dir, 'Glia')
    # add_full_texts_from_mult_dirs(full_text_dir, 'Hippocampus')
    # add_full_texts_from_mult_dirs(full_text_dir, 'Cereb Cortex')
    # add_full_texts_from_mult_dirs(full_text_dir, 'J Comp Neurol')
    # add_full_texts_from_mult_dirs(full_text_dir, 'J Neurosci Res')
    # add_full_texts_from_mult_dirs(full_text_dir, 'eNeuro')
    # add_full_texts_from_mult_dirs(full_text_dir, 'Physiol Rep')
    # add_full_texts_from_mult_dirs(full_text_dir, 'J Neurophysiol')
    #add_full_texts_from_mult_dirs(full_text_dir, 'J Neurosci')
    # add_full_texts_from_mult_dirs(full_text_dir, 'Synapse')

    add_full_texts_from_directory(full_text_dir + 'Cereb Cortex/')
    add_full_texts_from_directory(full_text_dir + 'J Neurosci/')
    # add_full_texts_from_directory(full_text_dir + 'Neuroscience Letters/')
    # add_full_texts_from_directory(full_text_dir + 'Neuron/')
    # add_full_texts_from_directory(full_text_dir + 'Neuroscience/')
    # add_full_texts_from_directory(full_text_dir + 'Neurobiol Dis/')
    # add_full_texts_from_directory(full_text_dir + 'Brain Research/')
    # add_full_texts_from_directory(full_text_dir + 'Cell/')

def run():
    add_full_texts()
