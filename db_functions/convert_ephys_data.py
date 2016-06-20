import numpy as np
import pandas as pd


def add_ephys_props_by_conversion(df):
    """Adds ephys vals to data frame through conversion of other provided ephys props"""

    conv_df = df.copy()

    # normalize ap amplitude by conversion of ap peak and ap thr
    naninds = pd.isnull(conv_df['apamp'])
    conv_df.loc[naninds, 'apamp'] = conv_df.loc[naninds, 'appeak'] - conv_df.loc[naninds, 'apthr']
    conv_df.loc[naninds, 'apamp_err'] = conv_df.loc[naninds, 'appeak_err']
    conv_df.loc[naninds, 'apamp_sd'] = conv_df.loc[naninds, 'appeak_sd']
    conv_df.loc[naninds, 'apamp_n'] = conv_df.loc[naninds, 'appeak_n']

    # convert amplitudes reported using rmp as baseline
    conv_df = convert_all_amps_from_resting(conv_df)

    # convert ahp voltages to ahp amplitudes
    conv_df = convert_all_ahp_volt_vals(conv_df)

    # normalize ahp amplitude by replacing with fAHPamp if available
    naninds = pd.isnull(conv_df['ahpamp'])
    conv_df.loc[naninds, 'ahpamp'] = conv_df.loc[naninds, 'fahpamp']
    conv_df.loc[naninds, 'ahpamp_err'] = conv_df.loc[naninds, 'fahpamp_err']
    conv_df.loc[naninds, 'ahpamp_sd'] = conv_df.loc[naninds, 'fahpamp_sd']
    conv_df.loc[naninds, 'ahpamp_n'] = conv_df.loc[naninds, 'fahpamp_n']

    # has ap peak and ap amplitude but no ap threshold (should be rare...)
    # http://dev.neuroelectro.org/data_table/1722/

    # pool different adaptation ratios to same property
    conv_df = pool_adapt_ratio(conv_df)

    # go through every property in dataframe and finally check if it is in the right range

    return conv_df


def convert_resting_amp_to_threshold(data_frame, val_name):
    if 'ahp' in val_name:
        ahp_flag = True
    else:
        ahp_flag = False

    new_data_frame = data_frame.copy()
    val_name_rest = val_name + 'rest'
    val_name_rest_err = val_name_rest + '_err'
    val_name_rest_n = val_name_rest + '_n'
    val_name_rest_sd = val_name_rest + '_sd'

    val_name_err = val_name + '_err'
    val_name_n = val_name + '_n'
    val_name_sd = val_name + '_sd'
    val_name_note = val_name + '_note'

    # has amplitude measured from resting - try converting to amp from threshold
    # requires measurement of apthr and rmp

    naninds = pd.isnull(data_frame[val_name])

    relative_threshold = data_frame.loc[naninds, 'apthr'] - data_frame.loc[naninds, 'rmp']
    vals_from_resting = data_frame.loc[naninds, val_name_rest]

    if ahp_flag:
        converted_vals = vals_from_resting + relative_threshold
    else:
        converted_vals = vals_from_resting - relative_threshold

    # only change values if conversion worked
    if len(converted_vals.dropna()) == 0:
        return data_frame
    corrected_inds = naninds & converted_vals.notnull()

    new_data_frame.loc[corrected_inds, val_name] = converted_vals
    new_data_frame.loc[corrected_inds, val_name_err] = data_frame.loc[naninds, val_name_rest_err]
    new_data_frame.loc[corrected_inds, val_name_sd] = data_frame.loc[naninds, val_name_rest_sd]
    new_data_frame.loc[corrected_inds, val_name_n] = data_frame.loc[naninds, val_name_rest_n]
    new_data_frame.loc[corrected_inds, val_name_note] = 'Converted from other ephys properties'

    return new_data_frame


def convert_all_amps_from_resting(data_frame):
    new_data_frame = convert_resting_amp_to_threshold(data_frame, 'apamp')
    new_data_frame = convert_resting_amp_to_threshold(new_data_frame, 'ahpamp')
    new_data_frame = convert_resting_amp_to_threshold(new_data_frame, 'fahpamp')
    new_data_frame = convert_resting_amp_to_threshold(new_data_frame, 'sahpamp')
    new_data_frame = convert_resting_amp_to_threshold(new_data_frame, 'mahpamp')

    return new_data_frame


def convert_all_ahp_volt_vals(data_frame):
    new_data_frame = convert_ahp_voltage_to_amp(data_frame, 'ahp')
    new_data_frame = convert_ahp_voltage_to_amp(new_data_frame, 'fahp')
    new_data_frame = convert_ahp_voltage_to_amp(new_data_frame, 'sahp')
    new_data_frame = convert_ahp_voltage_to_amp(new_data_frame, 'mahp')

    return new_data_frame



def convert_ahp_voltage_to_amp(data_frame, val_name):

    new_data_frame = data_frame.copy()
    val_name_volt = val_name + 'volt'
    val_name_volt_err = val_name_volt + '_err'
    val_name_volt_n = val_name_volt + '_n'
    val_name_volt_sd = val_name_volt + '_sd'

    val_name_err = val_name + 'amp_err'
    val_name_n = val_name + 'amp_n'
    val_name_sd = val_name + 'amp_sd'
    val_name_note = val_name + 'amp_note'

    # has amplitude measured from resting - try converting to amp from threshold
    # requires measurement of apthr and rmp

    naninds = pd.isnull(data_frame[val_name + 'amp'])

    thr_vals = data_frame.loc[naninds, 'apthr']
    ahp_volt_vals = data_frame.loc[naninds, val_name_volt]

    converted_vals = thr_vals - ahp_volt_vals
    if len(converted_vals.dropna()) == 0:
        return data_frame

    # only change values if conversion worked
    corrected_inds = naninds & converted_vals.notnull()

    new_data_frame.loc[corrected_inds, val_name + 'amp'] = converted_vals
    new_data_frame.loc[corrected_inds, val_name_err] = data_frame.loc[naninds, val_name_volt_err]
    new_data_frame.loc[corrected_inds, val_name_sd] = data_frame.loc[naninds, val_name_volt_sd]
    new_data_frame.loc[corrected_inds, val_name_n] = data_frame.loc[naninds, val_name_volt_n]
    new_data_frame.loc[corrected_inds, val_name_note] = 'Converted from other ephys properties'

    return new_data_frame


def pool_adapt_ratio(data_frame):

    new_data_frame = data_frame.copy()

    # get list of all adaptation ratio names
    names = ['adratio', 'adratioinv', 'adpct', 'adpctinv', 'adratiominus', 'adpctminus', 'adpctother']

    val_inds = pd.notnull(data_frame['adratioinv'])
    observed_vals = new_data_frame.loc[val_inds, 'adratioinv']
    converted_vals = 1/observed_vals
    new_data_frame.loc[val_inds, 'adratio'] = converted_vals

    val_inds = pd.notnull(data_frame['adpct'])
    observed_vals = new_data_frame.loc[val_inds, 'adpct']
    converted_vals = observed_vals / 100
    new_data_frame.loc[val_inds, 'adratio'] = converted_vals

    val_inds = pd.notnull(data_frame['adpctinv'])
    observed_vals = new_data_frame.loc[val_inds, 'adpctinv']
    converted_vals = 1/observed_vals
    new_data_frame.loc[val_inds, 'adratio'] = converted_vals

    val_inds = pd.notnull(data_frame['adratiominus'])
    observed_vals = new_data_frame.loc[val_inds, 'adratiominus']
    converted_vals = 1 - observed_vals
    new_data_frame.loc[val_inds, 'adratio'] = converted_vals

    val_inds = pd.notnull(data_frame['adpctminus'])
    observed_vals = new_data_frame.loc[val_inds, 'adpctminus']
    converted_vals = 1 - (observed_vals / 100)
    new_data_frame.loc[val_inds, 'adratio'] = converted_vals


    # goal is to get all properties to be a ratio of early ISI / late ISI

    return new_data_frame


def pool_ephys_props_across_tables(ne_table, grouping_fields):
    '''Pool ephys properties across different tables but from the same article based on common metadata in grouping_fields'''

    cleaned_df = ne_table.copy()
    col_names = ne_table.columns.values.tolist()
    #print col_names

    # need to generate a random int for coercing NaN's to something - required for pandas grouping
    rand_int = -abs(np.random.randint(20000))
    cleaned_df.loc[:, grouping_fields[0]:grouping_fields[-1]] = \
        ne_table.loc[:, grouping_fields[0]:grouping_fields[-1]].fillna(rand_int)


    # grouping_fields.remove('TableID')
    #
    # grouping_fields.remove('NeuroNERAnnots')
    cleaned_df_grouped = cleaned_df.groupby(by = grouping_fields)

    # taking this mean drops non-numeric columns
    cleaned_df = cleaned_df_grouped.mean()

    cleaned_df_first = cleaned_df_grouped.first()
    #cleaned_df_last = cleaned_df_grouped.last()

    cleaned_df.replace(to_replace = rand_int, value = np.nan, inplace=True)
    cleaned_df.reset_index(inplace=True)
    cleaned_df.sort_values(by = ['PubYear', 'Pmid', 'NeuronPrefName'], ascending=[False, True, True], inplace=True)
    cleaned_df.index.name = "Index"

    # calculate the same data frame, but taking the first instance of each group, rather than mean
    cleaned_df_first.replace(to_replace = rand_int, value = np.nan, inplace=True)
    cleaned_df_first.reset_index(inplace=True)
    cleaned_df_first.sort_values(by = ['PubYear', 'Pmid', 'NeuronPrefName'], ascending=[False, True, True], inplace=True)
    cleaned_df_first.index.name = "Index"

    cleaned_df['TableID'] = cleaned_df_first['TableID']

    # pick up the dropped columns and add them back in from "first" version of this data frame
    dropped_col_names = list(set(col_names).difference(set(cleaned_df.columns.values.tolist())))
    cleaned_df[dropped_col_names] = cleaned_df_first[dropped_col_names]

    cleaned_df = cleaned_df[col_names]
    cleaned_df.replace(to_replace = rand_int, value = np.nan, inplace=True)

    return cleaned_df