from db_functions.add_neuroner_annotations import assign_neuroner_ids
from db_functions.identify_error_type import assign_error_type_to_data_tables
from scripts.dbrestore import normalize_all_nedms, assign_expert_validated

__author__ = 'stripathy'


def update_cms():
    """Updates neuroelectro NeuronEphysDataMap objects with normalized value and assigns expert validated bool
    to all neuroelectro ConceptMap objects"""

    print 'updating concept maps for normalization, expert validation, and neuroNER IDs'
    normalize_all_nedms()
    assign_expert_validated()
    assign_neuroner_ids()
    assign_error_type_to_data_tables()

def run():
    update_cms()
