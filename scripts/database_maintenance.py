'''
Neuroelectro database maintenance script (can be run nightly)
'''
__author__ = 'dtebaykin'

from django.db import connection

# Delete amdm's with metadata ids that point to NULL entries in the metadata table (metadata that was deleted)
def remove_unused_amdms():
    cursor = connection.cursor()
    cursor.execute("DELETE FROM neuroelectro_articlemetadatamap WHERE NOT EXISTS (SELECT 1 FROM neuroelectro_metadata WHERE id = metadata_id);")
    
def run():
    print "Running database_maintenance.py"
    remove_unused_amdms()
    print "Finished running database_maintenance.py"