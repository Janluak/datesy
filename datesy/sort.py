

def create_sorted_list_from_order(
    order, all_elements=None, main_element=None, main_element_position=None
):
    """
    Create a sorted list based on the values in order based on the key values.

    The function additionally allows to specify more elements for the sorted_list which don't matter in terms of order.
    Additionally, a main_element can be specified which has a leading position/is specified asides from order.

    Parameters
    ----------
    order : dict, list
        the dictionary with the positions (keys) and elements (values)
    all_elements : list, set
        all the strings which shall be put in order.
        if more keys in all_elements than in order: keys will be added in random order
        if less keys in all_elements than in order: only the keys in all_elements will be returned, additional ones get deleted
    main_element : str
        the main_element
    main_element_position : int
        the position of the main_element

    Returns
    -------
    list
        the sorted list with elements from all_elements and main_element
    """
    if (
        main_element
        and not main_element_position
        and main_element_position != 0
        or not main_element
        and main_element_position
    ):
        if main_element and main_element not in order:
            raise ValueError(
                "`main_element` defined but neither in `order` nor defined with `main_element_position`"
            )
        else:
            raise ValueError("`main_element_position` without `main_element` set")

    if all_elements and not isinstance(all_elements, list):
        try:
            all_elements = list(all_elements)
        except TypeError:
            raise TypeError(
                "if `all_elements` is set it must be a list or convertible to list."
                " {} given".format(type(all_elements))
            )

    if isinstance(order, dict):
        all_elements = set(all_elements)
        if main_element:
            all_elements.add(main_element)
        if not all(isinstance(order_no, int) for order_no in order.keys()):
            raise ValueError("all keys of order dictionary need to be of type int")
        if not len(set(order.values())) == len(order):
            raise ValueError("not all order keys unique")
        if not all(list(order.values())[i] in all_elements for i in range(len(order))):
            for key in order.copy():
                if order[key] not in all_elements:
                    del order[key]
            # formerly functionality: raising error if not all keys in order available in order.
            # raise ValueError(
            #     f"some additional keys in order which aren't in all keys: {set(order.values()) - all_elements}"
            # )

        if main_element:
            if (
                main_element_position in order.keys()
                and main_element != order[main_element_position]
            ):
                raise KeyError(
                    "The main_element_position '{}' is used by another key ('{}') "
                    "in the order dict!".format(
                        main_element_position, order[main_element_position]
                    )
                )
            if main_element not in order.values():
                order[main_element_position] = main_element

        placed_keys = set(order.values())
        sorted_list = list(all_elements - placed_keys)

        for order_no in sorted(list(order.keys())):
            sorted_list.insert(order_no, order[order_no])

        return sorted_list

    elif isinstance(order, list):
        if main_element:
            order.insert(main_element_position, main_element)
        if all_elements:
            order += all_elements
        return order

    else:
        raise TypeError(
            f"wrong type of order, {type(order)} given. only list and dict are allowed"
        )
