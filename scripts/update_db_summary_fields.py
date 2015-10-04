from db_functions.compute_field_summaries import computeNeuronEphysSummariesAll, computeEphysPropSummaries, \
    computeEphysPropValueSummaries, computeNeuronSummaries, computeArticleSummaries

__author__ = 'stripathy'


def update_summary_fields():
    """Updates database summary fields like how many articles associated with a neuron type,
    mean ephys values associated with a neuron type, etc"""

    print 'updating field summaries'
    computeNeuronEphysSummariesAll()
    computeEphysPropSummaries()
    computeEphysPropValueSummaries()
    computeNeuronSummaries()
    computeArticleSummaries()


def run():
    update_summary_fields()