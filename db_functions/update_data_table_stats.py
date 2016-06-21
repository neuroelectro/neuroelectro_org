import neuroelectro.models as m
from scripts.dbrestore import prog


__author__ = 'shreejoy'


def assign_stat_object_to_data_tables():
    """go through each data table object and add info about who curated and when"""

    dts = m.DataTable.objects.filter(datasource__ephysconceptmap__isnull= False)

    num_dts = dts.count()
    for i,dt in enumerate(dts):
        print "updating data tables with summary objects"
        prog(i,num_dts)
        update_data_table_stat(dt)


def update_data_table_stat(data_table_object):
    """adds intermediate fields to data table stat object based on concept map objects associated
            with data table"""

    data_table_stat = m.DataTableStat.objects.get_or_create(data_table = data_table_object)[0]

    # assign curating users by looking at history concepts assoc with table
    robot_user = m.get_robot_user()
    user_list = data_table_object.get_curating_users()
    if robot_user in user_list:
        user_list.remove(robot_user)
    existing_users = data_table_stat.curating_users.all()
    for u in user_list:
        if u in existing_users:
            continue
        else:
            data_table_stat.curating_users.add(u)

    # assign last curated on by looking at curating users curation times and getting most recent
    concept_maps = data_table_object.get_concept_maps()
    if len(concept_maps) == 0:
        return
    curated_on_dates = []
    for cm in concept_maps:
        curated_on = cm.history.latest().history_date
        curated_on_dates.append(curated_on)
    curated_on = max(curated_on_dates)
    # update last curated on if different
    if data_table_stat.last_curated_on is not curated_on:
        data_table_stat.last_curated_on = curated_on

    # count number of unique ncms, ecms, nedms associated with table
    data_table_stat.num_ecms = m.EphysProp.objects.filter(ephysconceptmap__source__data_table = data_table_object).distinct().count()
    data_table_stat.num_ncms = m.Neuron.objects.filter(neuronconceptmap__source__data_table = data_table_object).distinct().count()
    data_table_stat.num_nedms = m.NeuronEphysDataMap.objects.filter(source__data_table = data_table_object).distinct().count()

    # define times validated here as min num of times validated per neuron concept map
    concept_maps = data_table_object.get_neuron_concept_maps()
    times_validated_per_neuron = []
    for cm in concept_maps:
        tv = cm.times_validated
        times_validated_per_neuron.append(tv)
    if len(times_validated_per_neuron) > 0:
        data_table_stat.times_validated = int(min(times_validated_per_neuron))

    data_table_stat.save()

    return data_table_stat