#!/usr/bin/env bash
python manage.py runscript update_concept_maps
python manage.py runscript update_db_summary_fields
python manage.py runscript database_maintenance
