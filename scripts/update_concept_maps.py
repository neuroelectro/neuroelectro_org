from scripts.dbrestore import normalize_all_nedms, assign_expert_validated
from db_functions.add_neuroner_annotations import assign_neuroner_ids

__author__ = 'stripathy'


def update_cms():
    """Updates neuroelectro NeuronEphysDataMap objects with normalized value and assigns expert validated bool
    to all neuroelectro ConceptMap objects"""

    print 'updating concept maps for normalization, expert validation, and neuroNER IDs'
    normalize_all_nedms()
    assign_expert_validated()
    assign_neuroner_ids()

def run():
    update_cms()
