import pandas as pd
import neuroelectro.models as m

__author__ = 'shreejoy'


def assign_error_type_to_data_tables():
    '''uses computational method to assign standard deviation error types to each data table and user submission object'''

    # for articles with some nedms and has a data table
    data_tables = m.DataTable.objects.filter(datasource__neuronephysdatamap__isnull = False).distinct()
    for dt in data_tables:
        nedm_list = dt.datasource_set.all()[0].neuronephysdatamap_set.all()

        # use computational method to assign error type based on values
        calculated_error_type_bool = identify_stdev(nedm_list) # returns true if stdev

        # check existing dt error type and calculated error type
        if dt.error_type is not 'sd' and calculated_error_type_bool:
            print 'assigning error type sd to data table %s' % dt.pk
            dt.error_type = 'sd'
            dt.save()

    # for articles with some nedms and has a data table
    user_subs = m.UserSubmission.objects.filter(datasource__neuronephysdatamap__isnull = False).distinct()
    for us in user_subs:
        nedm_list = us.datasource_set.all()[0].neuronephysdatamap_set.all()

        # use computational method to assign error type based on values
        calculated_error_type_bool = identify_stdev(nedm_list) # returns true if stdev

        # check existing us error type and calculated error type
        if us.error_type is not 'sd' and calculated_error_type_bool:
            print 'assigning error type sd to user submission %s with article pk %s' % (us.pk, us.article.pk)
            us.error_type = 'sd'
            us.save()


def identify_stdev(nedm_list):
    '''A computational method to identify whether error terms on neuron ephys data maps are standard deviations,
        relies on idea that standard deviations are typically large relative to the mean vs standard errors'''

    mean_list = [nedm.val_norm for nedm in nedm_list]
    err_list = [nedm.err_norm for nedm in nedm_list]

    sd_ratio = .175 # ratio of mean to error above which a SD is assumed
    fract_greater = .5 # fraction of how many nedms need to have a higher error than expected?

    df = pd.DataFrame()
    df['means'] = mean_list
    df['errs'] = err_list

    greater_count = sum(df['errs'] / df['means'] > sd_ratio)
    total_count = df['errs'].count()

    if total_count <= 0:
        return False

    if float(greater_count) / total_count > fract_greater:
        return True
    else:
        return False