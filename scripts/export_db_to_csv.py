__author__ = 'stripathy'

from db_functions.export_db_data import export_db_to_data_frame
import pandas
from django.conf import settings

def run():
    print "Initiating data file creation"
    file_name = settings.STATICFILES_DIRS[0] + "src/article_ephys_metadata_curated.csv"
    df_pooled, df_unpooled = export_db_to_data_frame()
    df_pooled.to_csv(file_name, sep='\t', encoding='utf-8')

    unpooled_file_name = settings.STATICFILES_DIRS[0] + "src/article_ephys_metadata_unpooled.csv"
    df_pooled.to_csv(unpooled_file_name, sep='\t', encoding='utf-8')
    print "done"
