'''
Created on Jul 16, 2014

@author: stripathy
'''

def dict_pop_multiple(input_dict, dict_keys_to_pop):
    '''removes/pops multiple keys from a dictionary'''
    for k in dict_keys_to_pop:
        input_dict.pop(k)
    return input_dict