# shell script for outputing json dump of validated neuroelectro data

# dumps validated neuronephysdatamaps, articlemetadatamaps, and summary objects
python manage.py dump_object neuroelectro.neuronephysdatamap --query '{"ephys_concept_map__times_validated__gte": 1}' > neuroelectro/fixtures/nedms.json
python manage.py dump_object neuroelectro.articlemetadatamap --query '{"times_validated__gte": 1}' > neuroelectro/fixtures/amdms.json
python manage.py dump_object neuroelectro.neuronephyssummary '*' > neuroelectro/fixtures/neuronephyssummary.json
python manage.py dump_object neuroelectro.neuronsummary '*' > neuroelectro/fixtures/neuronsummary.json
python manage.py dump_object neuroelectro.ephyspropsummary '*' > neuroelectro/fixtures/ephyspropsummary.json
python manage.py dump_object neuroelectro.articlesummary '*' > neuroelectro/fixtures/articlesummary.json

# merges intermediate json files and reorders them for easy import by loaddata function
python manage.py merge_fixtures neuroelectro/fixtures/nedms.json neuroelectro/fixtures/amdms.json neuroelectro/fixtures/neuronephyssummary.json  neuroelectro/fixtures/neuronsummary.json neuroelectro/fixtures/ephyspropsummary.json neuroelectro/fixtures/articlesummary.json > neuroelectro/fixtures/merged_data.json
python manage.py reorder_fixtures neuroelectro/fixtures/merged_data.json > neuroelectro/fixtures/validated_data.json

rm neuroelectro/fixtures/neuronephyssummary.json neuroelectro/fixtures/neuronsummary.json neuroelectro/fixtures/articlesummary.json neuroelectro/fixtures/ephyspropsummary.json neuroelectro/fixtures/amdms.json neuroelectro/fixtures/nedms.json neuroelectro/fixtures/merged_data.json
# function to load data into a database with just the schema
# python manage.py loaddata neuroelectro/fixtures/validated_data.json

# Removes email addresses and passwords.  
python secure.py merged_data.json


