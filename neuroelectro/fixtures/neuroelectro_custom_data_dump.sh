# shell script for outputing json dump of validated neuroelectro data

# dumps validated neuronephysdatamaps, articlemetadatamaps, and summary objects
python manage.py dump_object neuroelectro.neuronephysdatamap --query '{"ephys_concept_map__times_validated__gte": 1}' > neuroelectro/fixtures/nedms.json
python manage.py dump_object neuroelectro.articlemetadatamap --query '{"times_validated__gte": 1}' > neuroelectro/fixtures/amdms.json
python manage.py dumpdata neuroelectro.neuronephyssummary neuroelectro.neuronsummary neuroelectro.ephyspropsummary neuroelectro.articlesummary > neuroelectro/fixtures/summaries.json

# merges intermediate json files and reorders them for easy import by loaddata function
python manage.py merge_fixtures neuroelectro/fixtures/nedms.json neuroelectro/fixtures/amdms.json neuroelectro/fixtures/summaries.json > neuroelectro/fixtures/merged_data.json
python manage.py reorder_fixtures neuroelectro/fixtures/merged_data.json > neuroelectro/fixtures/validated_data.json

rm neuroelectro/fixtures/summaries.json neuroelectro/fixtures/amdms.json neuroelectro/fixtures/nedms.json neuroelectro/fixtures/merged_data.json
# function to load data into a database with just the schema
# python manage.py loaddata neuroelectro/fixtures/validated_data.json