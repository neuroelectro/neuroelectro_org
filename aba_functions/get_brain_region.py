from allensdk.core.mouse_connectivity_cache import MouseConnectivityCache

__author__ = 'stripathy'


def get_major_brain_region(structure_path_str, onto):
    """ Returns a dictionary of region attributes given structure path from allensdk API
    :param structure_path_str: a region's structure path from the allensdk API
    :param onto: an ontology structure desribing the brain regions and relationships
    :return: a dictionary of region attributes
    """
    #structure_path_str = onto[r.allenid].structure_id_path.item()

    # list of acronyms corresponding to 12 major brain regions in structure atlas ontology
    big_reg_acros = ['Isocortex', 'OLF', 'STR', 'PAL', 'TH', 'HY', 'MB', 'PAL', 'MY', 'CB', 'HPF', 'CTXsp']

    region_path = structure_path_str.split('/')
    dataframe = onto.df
    ret_dict = {}
    for c in reversed(region_path):
        if len(c) > 0:
            #print c
            tdf = dataframe[dataframe.id == int(c)]
            #print tdf.acronym.item()
            if tdf.acronym.item() in big_reg_acros:
                #print tdf.acronym.item()
                #break
                ret_dict['acronym'] = tdf.acronym.item()
                ret_dict['region_name'] = tdf.safe_name.item()
                ret_dict['region_id'] = tdf.atlas_id.item()
                return ret_dict
    return None


def get_neuron_region(neuron_ob):
    """ Given a neuron object, return a dictionary describing its major brain region from the Allen Mouse Atlas
    :param neuron_ob: A neuroelectro.models Neuron object
    :return: returns a dictionary of region attributes
    """
    regs = neuron_ob.regions.all()
    mcc = MouseConnectivityCache()
    onto = mcc.get_ontology()

    if regs:
        r = regs[0]
        structure_path_str = onto[r.allenid].structure_id_path.item()
        region_dict = get_major_brain_region(structure_path_str, onto)
        return region_dict
    else:
        return None
        # if region_dict:
        #     print (n.name, region_dict['region_name'])
        # else:
        #     print 'No region found for %s' % n.name