from article_text_mining.full_text_pipeline import add_full_texts_from_mult_dirs
__author__ = 'stripathy'


def add_full_texts():
    """Adds full texts from directory to DB based on rules specified in full_text_pipeline"""
    full_text_dir = '/data/downloaded_html/html/'
    matching_journ_str = 'PLoS'

    print 'Adding full texts from %s journals' % matching_journ_str
    add_full_texts_from_mult_dirs(full_text_dir, matching_journ_str)

def run():
    add_full_texts()
