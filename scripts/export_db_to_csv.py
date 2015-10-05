__author__ = 'stripathy'

from db_functions.export_db_data import export_db_to_data_frame
import pandas

def run():
    file_name = "article_ephys_metadata_curated.csv"
    df = export_db_to_data_frame()
    df.to_csv(file_name, sep='\t', encoding='utf-8')
