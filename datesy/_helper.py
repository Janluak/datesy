

def _dictionize(sub_dict):
    """
    Create normal dictionaries from a sub_dictionary containing orderedDicts

    Parameters
    ----------
    sub_dict : dict
        a dictionary with unlimited handling structure depth and types

    Returns
    -------
    dict
        the same structure as `sub_dict` just with dicts instead of  orderedDicts


    """
    from collections import OrderedDict

    normalized_dict = dict()
    for key in sub_dict:
        if isinstance(sub_dict[key], OrderedDict):
            normalized_dict[key] = _dictionize(sub_dict[key])
        elif isinstance(sub_dict[key], list):
            normalized_dict[key] = list()
            for element in sub_dict[key]:
                if isinstance(element, (list, dict, set)):
                    normalized_dict[key].append(_dictionize(element))
                else:
                    normalized_dict[key] = sub_dict[key]

        else:
            normalized_dict[key] = sub_dict[key]

    return normalized_dict


def _reduce_lists(sub_dict, list_for_reduction, manual_selection, depth_in_list=0):
    raise NotImplemented
