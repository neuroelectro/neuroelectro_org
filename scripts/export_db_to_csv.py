__author__ = 'stripathy'

from db_functions.export_db_data import export_db_to_data_frame
import pandas
from django.conf import settings

def run():
    print "Initiating data file creation"
    file_name = settings.OUTPUT_FILES_DIRECTORY + "article_ephys_metadata_curated.csv"
    df = export_db_to_data_frame()
    df.to_csv(file_name, sep='\t', encoding='utf-8')
    print "done"
