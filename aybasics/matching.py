from difflib import SequenceMatcher
import re, os


def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()


def match_similar(list_for_matching, list_to_be_matched_to, simplify_with=False, auto_match_all=True,
                  print_auto_match=False, single_match_only=False,
                  minimal_distance_for_automatic_matching=0.1, similarity_limit_for_manual_checking=0.6):
    """
    Returns a dictionary with list_a as keys and list_b as values based on most similarity.
    Matching twice to the same value is possible!
    If auto_match_all is set to False, human interface is able to decline a match. Similarity distance for switching
    between automatic matches and manual is set by `distance_for_automatic_vs_manual_matching`.

    Parameters
    ----------
    list_for_matching : list
        List of strings which shall be matched
    list_to_be_matched_to : list
        List of stings which shall be matched to
    simplify_with : {False, "capital", "separators", "all", list, str}
        For reducing the values by all small letters or unifying & deleting separators `separators`
        or any other list of strings provided
    auto_match_all : bool
        True if the most similar match shall just be used for matching, False if human wants to recheck
    print_auto_match : bool
        Especially for human rechecking: printing the automatically matched cases
    single_match_only : bool
        if each element of to_be_matched_to shall only be available one time
    minimal_distance_for_automatic_matching : float
        If there is a vast difference between the most and second most matching value, automatically matching is provided
        This parameter provides the similarity distance to be reached for automatically matching
    similarity_limit_for_manual_checking : float
        For not showing the most irrelevant match there could possibly exist

    Returns
    -------
    match : dict
        {index_value_for_matching: index_value_to_be_mapped_to}
    no_match : list
        A list of all values that could not be matched

    """
    if len(set(list_for_matching)) != len(list_for_matching):
        raise ValueError("multiple strings with same value! please provide unique set of strings!")

    if single_match_only:
        raise NotImplemented

    # translating to simpler value names #
    if simplify_with:
        if simplify_with not in ["capital", "separators", "all"]:
            separators = "".join(simplify_with)
        else:
            separators = '[_, | \n \' & " % \\ * -]'
        if simplify_with not in ["all", "separators"]:
            list_for_matching = [element.lower() for element in list_for_matching.copy()]
            list_to_be_matched_to = [element.lower() for element in list_to_be_matched_to.copy()]
        elif simplify_with != "capital":
            list_for_matching = ["".join(re.split(separators, element)) for element in list_for_matching.copy()]
            list_to_be_matched_to = ["".join(re.split(separators, element)) for element in list_to_be_matched_to.copy()]

    match = dict()
    no_match = list()
    most_similar = dict()
    most_similar_reverse = dict()
    ordered_most_similar = dict()
    ordered_most_similar_reverse = dict()

    list_for_matching = list_for_matching.copy()
    list_to_be_matched_to = list_to_be_matched_to.copy()
    list_for_matching_index_copy = list_for_matching.copy()
    list_to_be_matched_to_index_copy = list_to_be_matched_to.copy()

    # if direct matches
    for entry_a in list_for_matching.copy():
        if entry_a in list_to_be_matched_to:
            try:
                [match[list_for_matching_index_copy.index(entry_a)]] = [i for i, j in enumerate(list_to_be_matched_to_index_copy) if j == entry_a]
            except ValueError:
                match[list_for_matching_index_copy.index(entry_a)] = [i for i, j in enumerate(list_to_be_matched_to_index_copy) if j == entry_a]
            list_for_matching.remove(entry_a)

    # creating the most similar entries #
    for entry_a in list_for_matching:
        most_similar[entry_a] = dict()
        for entry_b in list_to_be_matched_to:
            similarity = similar(entry_a, entry_b)
            if similarity > similarity_limit_for_manual_checking:
                if similarity in most_similar[entry_a]:
                    # ToDo create nicer way for handling multiple matches of same similarity
                    while True:
                        similarity *= 0.000000001
                        if similarity not in most_similar[entry_a]:
                            break
                most_similar[entry_a][similarity] = entry_b
                if entry_b not in most_similar_reverse:
                    most_similar_reverse[entry_b] = dict()
                # ToDo catch same values of similarity
                most_similar_reverse[entry_b][similarity] = entry_a

        ordered_most_similar[entry_a] = sorted(list(most_similar[entry_a].keys()))[::-1]
    for entry_b in most_similar_reverse:
        ordered_most_similar_reverse[entry_b] = sorted(list(most_similar_reverse[entry_b].keys()))[::-1]

    # automatic matching all #
    if auto_match_all:
        for entry_a in list_for_matching.copy():
            try:
                match[list_for_matching_index_copy.index(entry_a)] = list_to_be_matched_to_index_copy.index(most_similar[entry_a][ordered_most_similar[entry_a][0]])
                list_for_matching.remove(entry_a)
                if print_auto_match:
                    print("automatically matched: {} - {}".format(entry_a,
                                                                  most_similar[entry_a][
                                                                      ordered_most_similar[entry_a][0]]))
            except IndexError:
                pass
        no_match = set(list_for_matching).difference(set(match))

    # human interfering matching #
    else:
        print("If first matches, press enter. If a number matches, press number and enter."
              " If none match, press 'n' and enter")
        for entry_a in list_for_matching:
            if not most_similar[entry_a]:
                no_match.append(entry_a)
            else:
                try:
                    if (len(ordered_most_similar[entry_a]) == 1 and ordered_most_similar[entry_a][0] >
                        (1 - minimal_distance_for_automatic_matching)) \
                            or (len(ordered_most_similar[entry_a]) > 1 and
                                (ordered_most_similar[entry_a][0] - ordered_most_similar[entry_a][1])
                                > minimal_distance_for_automatic_matching):

                        if print_auto_match:
                            print("automatically matched: {} - {}".format(entry_a, most_similar[entry_a][
                                ordered_most_similar[entry_a][0]]))
                        match[list_for_matching_index_copy.index(entry_a)] = list_to_be_matched_to_index_copy.index(most_similar[entry_a][ordered_most_similar[entry_a][0]])

                except IndexError:
                    pass

                if list_for_matching_index_copy.index(entry_a) not in match:
                    try:
                        _, columns = os.popen('stty size', 'r').read().split()
                        window_width = int(columns)
                    except ValueError:
                        window_width = 200

                    largest_string = len(str(max(list(most_similar[entry_a].values()) + [entry_a], key=len)))
                    minimal_string = 13
                    max_number_to_show = int(window_width / (largest_string + 3))
                    if max_number_to_show > int(window_width / minimal_string):
                        max_number_to_show = int(window_width / minimal_string)
                    characters = largest_string if largest_string > minimal_string - 5 else minimal_string - 5

                    print("".join(["{}{}:  {:2.1f}% |".format("".join([" " for i in range(largest_string - 8)]), n,
                                                              round(ordered_most_similar[entry_a][n], 3) * 100)
                                   for n in range(len(ordered_most_similar[entry_a][:max_number_to_show]))]))

                    number_to_show = max_number_to_show if max_number_to_show < len(ordered_most_similar[entry_a]) \
                        else len(ordered_most_similar[entry_a])
                    print("".join([" {:>{}} |".format(entry_a, characters) for i in range(number_to_show)]))
                    print("".join([" {:>{}} |".format(most_similar[entry_a][ordered_most_similar[entry_a][n]],
                                                      characters) for n in range(number_to_show)]))

                    answer = input("match? ")
                    if answer == "":
                        match[list_for_matching_index_copy.index(entry_a)] = list_to_be_matched_to_index_copy.index(most_similar[entry_a][ordered_most_similar[entry_a][0]])

                    else:
                        try:
                            match[list_for_matching_index_copy.index(entry_a)] = list_to_be_matched_to_index_copy.index(most_similar[entry_a][ordered_most_similar[entry_a][int(answer)]])
                        except ValueError:
                            try:
                                generator = (print("{}: {:1.3f} | {} - {}: fit? ".
                                                   format(n + number_to_show,
                                                          round(ordered_most_similar[entry_a][n + number_to_show],
                                                                3),
                                                          entry_a,
                                                          most_similar[entry_a][
                                                              ordered_most_similar[entry_a][n + number_to_show]]))
                                             for n in range(len(ordered_most_similar[entry_a])))

                                for _ in generator:
                                    result = input("match? ")
                                    if result == "":
                                        match[list_for_matching_index_copy.index(
                                            entry_a)] = list_to_be_matched_to_index_copy.index(
                                            most_similar[entry_a][ordered_most_similar[entry_a][number_to_show]])
                                        break
                                    else:
                                        number_to_show += 1
                            except IndexError:
                                pass

            if list_for_matching_index_copy.index(entry_a) not in match:
                no_match.append(entry_a)
                print('no similarity for "{}" above {}% similarity'.format(entry_a,
                                                                           similarity_limit_for_manual_checking * 100))

    return match, no_match
