from scripts.dbrestore import normalize_all_nedms, assign_expert_validated

__author__ = 'stripathy'


def update_cms():
    """Updates neuroelectro NeuronEphysDataMap objects with normalized value and assigns expert validated bool
    to all neuroelectro ConceptMap objects"""

    print 'updating concept maps for normalization and expert validation'
    normalize_all_nedms()
    assign_expert_validated()

def run():
    update_cms()
