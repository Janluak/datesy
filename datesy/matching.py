from difflib import SequenceMatcher
from pandas import DataFrame
from collections import OrderedDict
import re, os, logging

__doc__ = "All actions of mapping data to other data as well as the functions helpful for that are to be found here"
__all__ = ["simplify_strings", "ease_match_similar", "match_comprehensive", "match_similar_with_manual_selection"]


def simplify_strings(to_simplify, lower_case=True, simplifier=True):
    """
    Simplify a `string`, `set(strings)`, `list(strings)`, `keys in dict`
    Options for simplifying include: lower capitals, separators, both (standard), own set of simplifier

    Parameters
    ----------
    to_simplify : list, set, string
        the string(s) to simplify presented by itself or as part of another data format
    lower_case : bool, optional
        if the input shall be converted to only lower_case (standard: `True`)
    simplifier : str, optional
        the chars to be removed from the string. if type bool and True, standard chars ``_ , | \\n ' & " % * - \\`` used

    Returns
    -------
    dict
        simplified values ``{simplified_value: input_value}``
    """

    # PreProcessing the input
    if isinstance(simplifier, bool) and simplifier:
        simplifier = "[_, | \n ' & \" % \\ * -]"
    elif simplifier:
        simplifier = f"[{simplifier}]"

    if isinstance(to_simplify, str):
        to_simplify = [to_simplify]
    elif isinstance(to_simplify, set):
        to_simplify = list(to_simplify)
    elif isinstance(to_simplify, dict):
        to_simplify = list(to_simplify.keys())

    if not isinstance(to_simplify, list):
        raise TypeError("to_simplify needs to be either of type str, list, set or dict")

    simplified = dict()
    not_unique = set()

    def add_to_simplified(key, value):
        if key in simplified:
            not_unique.add(simplified[key])
            not_unique.add(value)
        else:
            simplified[key] = value

    for key in to_simplify:
        if simplifier and lower_case:
            add_to_simplified("".join(re.split(simplifier, key)).lower(), key)
        elif simplifier:
            add_to_simplified("".join(re.split(simplifier, key)), key)
        elif lower_case:
            add_to_simplified(key.lower(), key)
        else:
            raise ValueError("either simplifier or lower_case must be set")

    if not_unique:
        raise ValueError(f"simplification made the following entries not unique anymore."
                         f"please provide different simplification method.\n{not_unique}")
    return simplified


def match_comprehensive(
        list_for_matching,
        list_to_be_matched_to,
        simplified=False,
):
    """
    Return a dictionary with ``list_for_matching`` as keys and ``list_to_be_matched_to`` as values based on most similarity.
    All values of both iterables get compared to each other and highest similarities are picked.
    Slower than `datesy.matching.ease_match_similar` but more precise.

    Parameters
    ----------
    list_for_matching : list, set
        Iterable of strings which shall be matched
    list_to_be_matched_to : list, set
        Iterable of stings which shall be matched to
    simplified : False, "capital", "separators", "all", list, str, optional
        For reducing the values by all small letters or unifying & deleting separators `separators`
        or any other list of strings provided

    Returns
    -------
    match : dict
        `{value_for_matching: value_to_be_mapped_to}`
    no_match : set
        A set of all values from `list_for_matching` that could not be matched

    """
    match, no_match = __match_handler(
        list_for_matching,
        list_to_be_matched_to,
        simplified,
        "comprehensive"
    )
    return match, no_match


def match_similar_with_manual_selection(
        list_for_matching,
        list_to_be_matched_to,
        simplified=False,
        minimal_distance_for_automatic_matching=0.1,
        print_auto_matched=False,
        similarity_limit_for_manual_checking=0.6,
):
    """
    Return a dictionary with ``list_for_matching`` as keys and ``list_to_be_matched_to`` as values based on most similarity.
    All possible matches not matched automatically (set limit with `minimal_distance_for_automatic_matching`) can be handled interactively.
    Similarity distance for stopping the matching is set by `distance_for_automatic_vs_manual_matching`.

    Parameters
    ----------
    list_for_matching : list, set
        Iterable of strings which shall be matched
    list_to_be_matched_to : list, set
        Iterable of stings which shall be matched to
    simplified : False, "capital", "separators", "all", list, str, optional
        For reducing the values by all small letters or unifying & deleting separators `separators`
        or any other list of strings provided
    print_auto_matched : bool, optional
        Printing the matched entries during process (most likely for debugging)
    minimal_distance_for_automatic_matching : float, optional
        If there is a vast difference between the most and second most matching value, automatically matching is provided
        This parameter provides the similarity distance to be reached for automatically matching
    similarity_limit_for_manual_checking : float, optional
        For not showing/matching the most irrelevant match which could exist

    Returns
    -------
    match : dict
        `{value_for_matching: value_to_be_mapped_to}`
    no_match : set
        A set of all values from `list_for_matching` that could not be matched

    """
    match, no_match = __match_handler(
        list_for_matching,
        list_to_be_matched_to,
        simplified,
        "manual_selection",
        minimal_distance_for_automatic_matching=minimal_distance_for_automatic_matching,
        print_auto_matched=print_auto_matched,
        similarity_limit_for_manual_checking=similarity_limit_for_manual_checking
    )
    return match, no_match


def ease_match_similar(
        list_for_matching,
        list_to_be_matched_to,
        simplified=False,
        similarity_limit_for_matching=0.6,
        print_auto_matched=False,
):
    """
    Return a dictionary with ``list_for_matching`` as keys and ``list_to_be_matched_to`` as values based on most similarity.
    Matching twice to the same value is possible!
    Similarity distance for stopping the matching is set by `distance_for_automatic_vs_manual_matching`.
    Faster than `datesy.matching.match_comprehensive` but when having very similar strings more likely to contain errors.

    Parameters
    ----------
    list_for_matching : list, set
        Iterable of strings which shall be matched
    list_to_be_matched_to : list, set
        Iterable of stings which shall be matched to
    simplified : False, "capital", "separators", "all", list, str, optional
        For reducing the values by all small letters or unifying & deleting separators `separators`
        or any other list of strings provided
    print_auto_matched : bool, optional
        Printing the matched entries during process (most likely for debugging)
    similarity_limit_for_matching : float, optional
        For not matching the most irrelevant match which could exist

    Returns
    -------
    match : dict
        `{value_for_matching: value_to_be_mapped_to}`
    no_match : set
        A set of all values from `list_for_matching` that could not be matched

    """
    match, no_match = __match_handler(
        list_for_matching,
        list_to_be_matched_to,
        simplified,
        "ease",
        similarity_limit_for_manual_checking=similarity_limit_for_matching,
        print_auto_matched=print_auto_matched
    )
    return match, no_match


def _check_uniqueness_of_entries(data_set, data_set_name=None, raise_exception=True):
    """
    Check if all entries in iterable are unique in iterable

    Parameters
    ----------
    data_set : [list, set]
        iterable containing the entries to test for uniqueness
    data_set_name : str, optional
        the name of the data_set for displaying in exception
    raise_exception : bool, optional
        if raising an exception or returning `False` on non-uniqueness

    """
    if len(set(data_set)) != len(data_set):
        entries = set()
        doubles = set()

        for entry in data_set:
            if entry in entries:
                doubles.add(entry)
            entries.add(entry)
        if data_set_name:
            error_message = f"following {len(doubles)} entries of {data_set_name} are not unique: {doubles}"
        else:
            error_message = f"following {len(doubles)} entries are not unique in provided data: {doubles}"

        if raise_exception:
            raise ValueError(error_message)
        else:
            return False
    return True


def _find_direct_matches(list_for_matching, list_to_be_matched_to):
    """
    Find all 100% matches between the values of the two iterables

    Parameters
    ----------
    list_for_matching : list, set
        iterable containing the keys
    list_to_be_matched_to : list, set
        iterable containing the values to match to the keys

    Returns
    -------

    matched : dict
        all 100% matches

    """
    matches = dict()

    for entry_a in list_for_matching.copy():
        if entry_a in list_to_be_matched_to:
            matches[entry_a] = entry_a
            list_for_matching.remove(entry_a)
            list_to_be_matched_to.remove(entry_a)

    return matches


def _calculate_similarities_listed_by_list_for_matching_entry(list_for_matching, list_to_be_matched_to):
    """
    Calculate the similarities between the iterable entries; return based on the entries of the `list_for_matching`

    Parameters
    ----------
    list_for_matching : [set, list]
        iterable containing the strings which shall be matched
    list_to_be_matched_to : [set, list]
        iterable containing the strings to be matched to

    Returns
    -------

    OrderedDict
        ``{value1_list_for_matching: {highest_similarity_match: [value1_list_to_be_matched_to]}, ...,
        {lowest_similarity_match: ...}}``

    """
    all_similarities_per_entry_a = dict()
    ordered_similarity_per_entry_a = dict()

    for entry_a in list_for_matching:
        all_similarities_per_entry_a[entry_a] = dict()

        for entry_b in list_to_be_matched_to:
            similarity = SequenceMatcher(None, entry_a, entry_b).ratio()

            if similarity not in all_similarities_per_entry_a[entry_a]:
                all_similarities_per_entry_a[entry_a][similarity] = list()
            all_similarities_per_entry_a[entry_a][similarity].append(entry_b)

        ordered_similarities = sorted(all_similarities_per_entry_a[entry_a].keys(), reverse=True)

        ordered_similarity_per_entry_a[entry_a] = OrderedDict()
        for similarity in ordered_similarities:
            ordered_similarity_per_entry_a[entry_a][similarity] = all_similarities_per_entry_a[entry_a][similarity]

    return ordered_similarity_per_entry_a


def _calculate_similarities_listed_by_similarity(list_for_matching, list_to_be_matched_to):
    """
    Calculate the similarities between the iterable entries; return based on the highest similarity values

    Parameters
    ----------
    list_for_matching : [set, list]
        iterable containing the strings which shall be matched
    list_to_be_matched_to : [set, list]
        iterable containing the strings to be matched to

    Returns
    -------

    OrderedDict
        ``{highest_similarity_match: [(a1, b1), (a2, b2), ...], ..., lowest_similarity_match: [...]}``

    """
    all_similarities_per_similarity_value = dict()
    ordered_similarities_per_value = OrderedDict()

    for entry_a in list_for_matching:

        for entry_b in list_to_be_matched_to:
            similarity = SequenceMatcher(None, entry_a, entry_b).ratio()

            if similarity not in all_similarities_per_similarity_value:
                all_similarities_per_similarity_value[similarity] = list()
            all_similarities_per_similarity_value[similarity].append((entry_a, entry_b))

    for similarity in sorted(all_similarities_per_similarity_value.keys(), reverse=True):
        ordered_similarities_per_value[similarity] = all_similarities_per_similarity_value[similarity]

    return ordered_similarities_per_value


def _create_similarity_dataframe(similarities):
    rows = list()

    for similarity in similarities:
        for match_set in similarities[similarity]:
            rows.append([similarity, match_set[0], match_set[1]])
    data_frame = DataFrame(
        rows,
        columns=["similarity", "entry_a", "entry_b"],
    )
    return data_frame


def __match_handler(
        list_for_matching,
        list_to_be_matched_to,
        simplified,
        variant,
        minimal_distance_for_automatic_matching=None,
        print_auto_matched=None,
        similarity_limit_for_manual_checking=None

):
    # Checking if entries for each data_set are unique
    for data_set in [list_for_matching, list_to_be_matched_to]:
        _check_uniqueness_of_entries(
            data_set, 'list_for_matching'
            if data_set == list_for_matching
            else 'list_to_be_matched_to'
        )

    if simplified:
        if simplified not in ["capital", "separators", "all"]:
            capital = False
        elif simplified == "capital":
            capital = True
            simplified = False
        elif simplified == "separators":
            capital = False
            simplified = True
        else:
            capital = True
            simplified = True

        dict_for_matching = simplify_strings(list_for_matching, capital, simplified)
        list_for_matching = list(dict_for_matching.keys())
        _check_uniqueness_of_entries(list_for_matching, "list_for_matching-simplified")

        dict_to_be_matched_to = simplify_strings(list_to_be_matched_to, True, simplified)
        list_to_be_matched_to = list(dict_to_be_matched_to.keys())
        _check_uniqueness_of_entries(list_to_be_matched_to, "list_to_be_matched_to-simplified")

    match = _find_direct_matches(list_for_matching, list_to_be_matched_to)

    if variant == "comprehensive":
        match, no_match = __match_comprehensive(list_for_matching, list_to_be_matched_to, match)
    elif variant == "manual_selection":
        match, no_match = __match_similar_with_manual_selection(
            list_for_matching,
            list_to_be_matched_to,
            match,
            minimal_distance_for_automatic_matching=minimal_distance_for_automatic_matching,
            print_auto_matched=False,
            similarity_limit_for_manual_checking=0.6,
        )
    else:
        match, no_match = __match_similar_with_manual_selection(
            list_for_matching,
            list_to_be_matched_to,
            match,
            minimal_distance_for_automatic_matching=0,
            print_auto_matched=print_auto_matched,
            similarity_limit_for_manual_checking=similarity_limit_for_manual_checking,
            no_manual=True
        )

    if simplified:
        match = {dict_for_matching[key]: dict_to_be_matched_to[value] for key, value in match.items()}
        no_match = {dict_for_matching[key] for key in no_match}

    return match, no_match


def __match_comprehensive(
        list_for_matching,
        list_to_be_matched_to,
        match
):

    similarities = _calculate_similarities_listed_by_similarity(list_for_matching, list_to_be_matched_to)

    df = _create_similarity_dataframe(similarities)

    old_length = 0

    while len(df.similarity) != 0 and len(df.similarity) != old_length:
        old_length = len(df.similarity)
        highest_similarity = df.similarity[0]
        if (
                len(df.similarity) > 1
                and highest_similarity != df.similarity[1]
                or len(df.similarity) == 0
        ):
            entry_a = df.entry_a[0]
            entry_b = df.entry_b[0]
            match[entry_a] = entry_b
            df = df[df.similarity != highest_similarity]
            df = df[df.entry_a != entry_a]
            df = df[df.entry_b != entry_b]
            df = df.reset_index(drop=True)
        else:
            indexes = list()
            index = -1
            for similarity in df.similarity:
                index += 1
                if highest_similarity == similarity:
                    indexes.append(index)
                else:
                    break

            # get all entries of un-unique similarity
            all_entries = list()
            all_entries_with_index = dict()
            for index in indexes:
                all_entries.append(df.entry_a[index])
                if df.entry_a[index] not in all_entries_with_index:
                    all_entries_with_index[df.entry_a[index]] = list()
                all_entries_with_index[df.entry_a[index]].append(index)

                all_entries.append(df.entry_b[index])
                if df.entry_b[index] not in all_entries_with_index:
                    all_entries_with_index[df.entry_b[index]] = list()
                all_entries_with_index[df.entry_b[index]].append(index)

            # get all entries which are doubled
            doubled_entries = all_entries.copy()
            for element in set(all_entries):
                doubled_entries.remove(element)

            unmatchable_indexes = list()
            for element in doubled_entries:
                for index in all_entries_with_index[element]:
                    indexes.remove(index)
                    unmatchable_indexes.append(index)

            if indexes:
                for index in indexes:
                    entry_a = df.entry_a[index]
                    entry_b = df.entry_b[index]
                    match[entry_a] = entry_b
                    df = df[df.entry_a != entry_a]
                    df = df[df.entry_b != entry_b]
                    df = df.reset_index(drop=True)

            else:
                # too similar strings: if for_matching doubled,
                # return all to_be_matched_to; otherwise add unmatched
                entry_a = df.entry_a[0]
                entry_b = df.entry_b[0]

                multiple_match = list()
                for element in doubled_entries:
                    for i, j in enumerate(list(df.entry_a)):
                        if i > index:
                            break
                        if j == element:
                            multiple_match.append(df.entry_b[i])
                if multiple_match:
                    match[entry_a] = multiple_match

                df = df[df.entry_a != entry_a]
                df = df[df.entry_b != entry_b]
                df = df.reset_index(drop=True)

    no_match = set(list_for_matching).difference(set(match))

    return match, no_match


def __match_similar_with_manual_selection(
        list_for_matching,
        list_to_be_matched_to,
        match,
        minimal_distance_for_automatic_matching=0.1,
        print_auto_matched=False,
        similarity_limit_for_manual_checking=0.6,
        no_manual=False
):
    def get_screen_width():
        try:
            _, columns = os.popen("stty size", "r").read().split()
            window_width = int(columns)
        except ValueError:
            window_width = 200
        return window_width

    def calculate_longest_string():
        longest_string_length = len(
            str(
                max(
                    [element[1] for element in decreasing_matches],
                    key=len,
                )
            )
        )
        return longest_string_length

    def get_print_setting():
        window_width = get_screen_width()
        longest_string = calculate_longest_string() + len(entry_a)

        minimal_string = 13
        max_number_to_show = int(window_width / (longest_string + 3))

        if max_number_to_show > int(window_width / minimal_string):
            max_number_to_show = int(window_width / minimal_string)

        number_to_show = (
            max_number_to_show
            if max_number_to_show < len(decreasing_matches)
            else len(decreasing_matches)
        )

        characters = (
            longest_string
            if longest_string > minimal_string - 5
            else minimal_string - 5
        )

        return number_to_show, characters, longest_string

    def first_print_statement():
        # print similarity values row
        print(
            "".join(
                [
                    "{}{}:  {:2.1f}% |".format(
                        "".join([" " for i in range(longest_string - 8)]),
                        n,
                        round(decreasing_matches[n][0], 3) * 100,
                    )
                    for n in range(number_to_show)
                ]
            )
        )

        # print entry_a row
        print(
            "".join(
                [
                    " {:>{}} |".format(entry_a, characters)
                    for i in range(number_to_show)
                ]
            )
        )

        # print possible matches row
        print(
            "".join(
                [
                    " {:>{}} |".format(
                        decreasing_matches[n][1],
                        characters,
                    )
                    for n in range(number_to_show)
                ]
            )
        )

    def further_print_statements(number_to_show):
        try:
            generator = (
                print(
                    "{}: {:2.1f}% | {} - {}: fit? ".format(
                        n + number_to_show,
                        round(
                            decreasing_matches[
                                n + number_to_show
                                ][0],
                            3,
                        ) * 100,
                        entry_a,
                        decreasing_matches[
                            n + number_to_show
                            ][1]

                    )
                )
                for n in range(len(decreasing_matches))
            )

            for _ in generator:
                result = input("match? ")
                if result == "":
                    match[entry_a] = decreasing_matches[
                        number_to_show
                    ][1]
                    break
                elif result == "break":
                    break
        except IndexError:
            pass

    no_match = set()
    similarities = _calculate_similarities_listed_by_list_for_matching_entry(list_for_matching, list_to_be_matched_to)

    if not no_manual:
        print(
            "If first entry matches, hit enter."
            "\nIf another entry matches, type correlating number and hit enter."
            "\nIf none match, press 'n' and enter."
            "\nFor stop matching a entry of list_for_matching, simply type 'break' and hit enter.\n"
        )
    for entry_a in similarities:
        similarities_of_entry_a = list(similarities[entry_a].keys())
        if len(similarities_of_entry_a) == 1:
            similarities_of_entry_a.insert(0, 1)
        if not (similarities_of_entry_a[0] - similarities_of_entry_a[1]) > minimal_distance_for_automatic_matching or \
                len(similarities[entry_a][similarities_of_entry_a[0]]) != 1:

            decreasing_matches = list()
            for similarity in similarities[entry_a]:
                for entry_b in similarities[entry_a][similarity]:
                    decreasing_matches.append((similarity, entry_b))

            if no_manual:
                identical_similarity = decreasing_matches[0][0]
                counter = 0
                match[entry_a] = list()
                while decreasing_matches[counter][0] == identical_similarity:
                    match[entry_a].append(decreasing_matches[counter][1])
                    counter += 1
                continue

            number_to_show, characters, longest_string = get_print_setting()

            first_print_statement()

            answer = input("match? ")
            if answer == "":
                match[entry_a] = decreasing_matches[0][1]
            elif answer == "break":
                continue

            else:
                try:
                    match[entry_a] = decreasing_matches[0][int(answer)]
                except ValueError:
                    # ToDo as for no_match, try again or further matching?
                    further_print_statements(number_to_show)

            continue

        matched_entry = similarities[entry_a][similarities_of_entry_a[0]].pop()
        if print_auto_matched:
            print(
                f"automatically matched: {entry_a} - {matched_entry}"
            )
        match[entry_a] = matched_entry

        if entry_a not in match:
            no_match.add(entry_a)
            logging.warning(
                f'no similarity for "{entry_a}" above {similarity_limit_for_manual_checking * 100}% similarity'
            )

    no_match = set(list_for_matching).difference(set(match))

    return match, no_match
