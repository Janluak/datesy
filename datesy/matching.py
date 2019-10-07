from difflib import SequenceMatcher
import re, os, logging

__doc__ = "All actions of mapping data to other data as well as the functions helpful for that are to be found here"
__all__ = ["simplify_strings", "match_similar"]


def _check_for_unique_similarity(simi, value, dict_entry):
    if simi in dict_entry:
        if not isinstance(dict_entry[simi], list):
            dict_entry[simi] = [dict_entry[simi]]
        dict_entry[simi].append(value)
    else:
        dict_entry[simi] = value


def simplify_strings(to_simplify, simplifier="standard"):
    """
    Simplify a string, set(strings), list(strings), dict(strings as keys)
    Options for simplifying include: lower capitals, separators, both (standard), own set of simplyfiers

    Parameters
    ----------
    to_simplify : list, dict, set, string
        the string(s) to simplify presented by itself or as part of another data format
    simplifier : list ['capital', chars, ], optional
        desired simplifiers can be specified. otherwise the standard ones will be selected

    Returns
    -------
    to_simplify : simplified values

    """
    standard_simplifiers = "[_, | \n ' & \" % \\ * -]"

    return to_simplify


def match_similar_with_manual_selection():
    return


def match_similar(
    list_for_matching,
    list_to_be_matched_to,
    simplify_with=False,
    auto_match_all=True,
    print_auto_match=False,
    single_match_only=True,
    enforce_comprehensive_check=False,
    minimal_distance_for_automatic_matching=0.1,
    similarity_limit_for_manual_checking=0.6,
):
    """
    Return a dictionary with ``list_for_matching`` as keys and ``list_to_be_matched_to`` as values based on most similarity.
    Matching twice to the same value is possible!
    If auto_match_all is set to False, human interface is able to decline a match. Similarity distance for switching
    between automatic matches and manual is set by `distance_for_automatic_vs_manual_matching`.

    Parameters
    ----------
    list_for_matching : list
        List of strings which shall be matched
    list_to_be_matched_to : list
        List of stings which shall be matched to
    simplify_with : False, "capital", "separators", "all", list, str
        For reducing the values by all small letters or unifying & deleting separators `separators`
        or any other list of strings provided
    auto_match_all : bool
        True if the most similar match shall just be used for matching, False if human wants to recheck
    print_auto_match : bool
        Especially for human rechecking: printing the automatically matched cases
    single_match_only : bool
        if mapping elements multiple times shall be used. otherwise unique sets are required
    enforce_comprehensive_check : bool
        if this flag is set, the function checks every single similarity between the sets and starts mapping with the strongest match.
        due to high complexity and good matching rate for sets if elements quite diverse, only use if similar sets
    minimal_distance_for_automatic_matching : float
        If there is a vast difference between the most and second most matching value, automatically matching is provided
        This parameter provides the similarity distance to be reached for automatically matching
    similarity_limit_for_manual_checking : float
        For not showing the most irrelevant match there could possibly exist

    Returns
    -------
    match : dict
        `{value_for_matching: value_to_be_mapped_to}`
    no_match : list
        A list of all values that could not be matched

    """
    if len(set(list_for_matching)) != len(list_for_matching):
        raise ValueError(
            "multiple strings with same value! please provide unique set of strings!"
        )

    if single_match_only:
        if len(set(list_for_matching)) != len(list_for_matching):
            raise ValueError(
                "multiple strings with same value! "
                "please provide unique set of strings for list_for_matching!"
            )
        if len(set(list_to_be_matched_to)) != len(list_to_be_matched_to):
            raise ValueError(
                "multiple strings with same value! "
                "please provide unique set of strings for list_to_be_matched_to!"
            )
    else:
        raise NotImplemented

    # translating to simpler value names #
    if simplify_with:
        if simplify_with not in ["capital", "separators", "all"]:
            separators = "".join(simplify_with)
        else:
            separators = "[_, | \n ' & \" % \\ * -]"
        dict_for_matching = dict()
        dict_to_be_matched_to = dict()
        if simplify_with not in ["all", "separators"]:
            dict_for_matching = {value.lower(): value for value in list_for_matching}
            list_for_matching = [value.lower() for value in list_for_matching.copy()]
            dict_to_be_matched_to = {
                value.lower(): value for value in list_to_be_matched_to
            }
            list_to_be_matched_to = [
                value.lower() for value in list_to_be_matched_to.copy()
            ]
        elif simplify_with != "capital":
            for entry_a in list_for_matching:
                dict_for_matching["".join(re.split(separators, entry_a))] = entry_a
                list_for_matching = list(dict_for_matching.keys())
            for entry_b in list_to_be_matched_to:
                dict_to_be_matched_to["".join(re.split(separators, entry_b))] = entry_b
                list_to_be_matched_to = list(dict_to_be_matched_to.keys())

    match = dict()
    no_match = list()
    most_similar = dict()
    ordered_most_similar = dict()
    all_similarities = dict()

    # if direct matches
    for entry_a in list_for_matching.copy():
        if entry_a in list_to_be_matched_to:
            match[entry_a] = entry_a
            list_for_matching.remove(entry_a)
            list_to_be_matched_to.remove(entry_a)

    # creating the most similar entries #
    for entry_a in list_for_matching:

        most_similar[entry_a] = dict()
        for entry_b in list_to_be_matched_to:

            similarity = SequenceMatcher(None, entry_a, entry_b).ratio()
            if similarity > similarity_limit_for_manual_checking:

                _check_for_unique_similarity(similarity, entry_b, most_similar[entry_a])
                if similarity not in all_similarities:
                    all_similarities[similarity] = list()
                if enforce_comprehensive_check:
                    all_similarities[similarity].append((entry_a, entry_b))

        ordered_most_similar[entry_a] = sorted(list(most_similar[entry_a].keys()))[::-1]
    if enforce_comprehensive_check:
        ordered_all_similarities = sorted(list(all_similarities.keys()))[::-1]

    # automatic matching all #
    if auto_match_all:
        if not enforce_comprehensive_check:
            for entry_a in list_for_matching.copy():
                try:
                    match[entry_a] = most_similar[entry_a][
                        ordered_most_similar[entry_a][0]
                    ]
                    list_for_matching.remove(entry_a)
                    if isinstance(
                        most_similar[entry_a][ordered_most_similar[entry_a][0]], list
                    ):
                        most_similar_list = most_similar[entry_a][
                            ordered_most_similar[entry_a][0]
                        ]
                        while most_similar_list:
                            list_to_be_matched_to.remove(most_similar_list[0])
                            most_similar_list = most_similar_list[1:]
                    else:
                        list_to_be_matched_to.remove(
                            most_similar[entry_a][ordered_most_similar[entry_a][0]]
                        )
                    if print_auto_match:
                        print(
                            f"automatically matched: {entry_a} - {most_similar[entry_a][ordered_most_similar[entry_a][0]]}"
                        )
                except IndexError:
                    pass
        else:
            from pandas import DataFrame

            similarities = list()
            entries_a = list()
            entries_b = list()
            for similarity in ordered_all_similarities:
                for match_set in all_similarities[similarity]:
                    similarities.append(similarity)
                    entries_a.append(match_set[0])
                    entries_b.append(match_set[1])
            df = DataFrame(
                {
                    "similarity": similarities,
                    "entry_a": entries_a,
                    "entry_b": entries_b,
                },
                columns=["similarity", "entry_a", "entry_b"],
            )
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
                                if j == element:
                                    multiple_match.append(df.entry_b[i])
                        if multiple_match:
                            match[entry_a] = multiple_match

                        df = df[df.entry_a != entry_a]
                        df = df[df.entry_b != entry_b]
                        df = df.reset_index(drop=True)

        no_match = set(list_for_matching).difference(set(match))

    # human interfering matching #
    else:
        print(
            "If first matches, press enter. If a number matches, press number and enter."
            " If none match, press 'n' and enter"
        )
        for entry_a in list_for_matching:
            if not most_similar[entry_a]:
                pass
            else:
                try:
                    if (
                        len(ordered_most_similar[entry_a]) == 1
                        and ordered_most_similar[entry_a][0]
                        > (1 - minimal_distance_for_automatic_matching)
                    ) or (
                        len(ordered_most_similar[entry_a]) > 1
                        and (
                            ordered_most_similar[entry_a][0]
                            - ordered_most_similar[entry_a][1]
                        )
                        > minimal_distance_for_automatic_matching
                    ):

                        if print_auto_match:
                            print(
                                f"automatically matched: {entry_a} - "
                                f"{most_similar[entry_a][ordered_most_similar[entry_a][0]]}"
                            )
                        match[entry_a] = most_similar[entry_a][
                            ordered_most_similar[entry_a][0]
                        ]

                except IndexError:
                    pass

                if entry_a not in match:
                    try:
                        _, columns = os.popen("stty size", "r").read().split()
                        window_width = int(columns)
                    except ValueError:
                        window_width = 200

                    largest_string = len(
                        str(
                            max(
                                list(most_similar[entry_a].values()) + [entry_a],
                                key=len,
                            )
                        )
                    )
                    minimal_string = 13
                    max_number_to_show = int(window_width / (largest_string + 3))
                    if max_number_to_show > int(window_width / minimal_string):
                        max_number_to_show = int(window_width / minimal_string)
                    characters = (
                        largest_string
                        if largest_string > minimal_string - 5
                        else minimal_string - 5
                    )

                    print(
                        "".join(
                            [
                                "{}{}:  {:2.1f}% |".format(
                                    "".join([" " for i in range(largest_string - 8)]),
                                    n,
                                    round(ordered_most_similar[entry_a][n], 3) * 100,
                                )
                                for n in range(
                                    len(
                                        ordered_most_similar[entry_a][
                                            :max_number_to_show
                                        ]
                                    )
                                )
                            ]
                        )
                    )

                    number_to_show = (
                        max_number_to_show
                        if max_number_to_show < len(ordered_most_similar[entry_a])
                        else len(ordered_most_similar[entry_a])
                    )
                    print(
                        "".join(
                            [
                                " {:>{}} |".format(entry_a, characters)
                                for i in range(number_to_show)
                            ]
                        )
                    )
                    print(
                        "".join(
                            [
                                " {:>{}} |".format(
                                    most_similar[entry_a][
                                        ordered_most_similar[entry_a][n]
                                    ],
                                    characters,
                                )
                                for n in range(number_to_show)
                            ]
                        )
                    )

                    answer = input("match? ")
                    if answer == "":
                        match[entry_a] = most_similar[entry_a][
                            ordered_most_similar[entry_a][0]
                        ]

                    else:
                        try:
                            match[entry_a] = most_similar[entry_a][
                                ordered_most_similar[entry_a][int(answer)]
                            ]
                        except ValueError:
                            try:
                                generator = (
                                    print(
                                        "{}: {:1.3f} | {} - {}: fit? ".format(
                                            n + number_to_show,
                                            round(
                                                ordered_most_similar[entry_a][
                                                    n + number_to_show
                                                ],
                                                3,
                                            ),
                                            entry_a,
                                            most_similar[entry_a][
                                                ordered_most_similar[entry_a][
                                                    n + number_to_show
                                                ]
                                            ],
                                        )
                                    )
                                    for n in range(len(ordered_most_similar[entry_a]))
                                )

                                for _ in generator:
                                    result = input("match? ")
                                    if result == "":
                                        match[entry_a] = most_similar[entry_a][
                                            ordered_most_similar[entry_a][
                                                number_to_show
                                            ]
                                        ]
                                        break
                                    else:
                                        number_to_show += 1
                            except IndexError:
                                pass

            if entry_a not in match:
                no_match.append(entry_a)
                logging.warning(
                    f'no similarity for "{entry_a}" above {similarity_limit_for_manual_checking * 100}% similarity'
                )

    # translating back to the original values #
    if simplify_with:
        match = {
            dict_for_matching[key]: dict_to_be_matched_to[match[key]]
            for key in match.keys()
        }
        no_match = {dict_for_matching[key] for key in no_match}

    return match, no_match
