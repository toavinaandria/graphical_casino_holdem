from collections import namedtuple, Counter
from math import factorial

import gamevars
from gamevars import card_value, hand_ranks


# This module calculates the value of a hand using the calcvalue(values,suits) function.
# The values and suits parameters must be lists or tuples of the relevant card values (sorted) and suits.


def match_val_bool(seq):
    """Creates a boolean list for consecutive matching card values."""
    true_list = []
    for i in range(len(seq) - 1):
        if seq[i] == seq[i + 1]:
            true_list.append(True)
        else:
            true_list.append(False)
    return true_list


def maxconsmatches(seq):
    """
    Counts the maximum number of consecutive matching card values in a sequence
    Used to distinguish between 4 of kind and full house or 3 of a kind and two pairs.
    """
    max_cons = 0
    max_list = []

    # Creates a boolean list for consecutive matching card values

    true_list = match_val_bool(seq)

    if True not in true_list:
        return 0
    else:

        # Counter for consecutive matching values

        for j in range(len(true_list) - 1):
            if true_list[j] == true_list[j + 1] == True:
                max_cons += 1
                max_list.append(max_cons)
            else:
                max_cons = 0
                max_list.append(max_cons)
    return max(max_list)


def isflush(values, suits):
    """
    Checks whether all suits are the same.
    Needs to be applied to list of card suits.
    """
    return len(set(suits)) == 1


def isstraight(values, suits):
    """
    Checks whether hand contains cards with consecutive rankings.
    Needs to be applied to list of card values sorted in descending order.
    """
    value_list = []

    # Checks for special case where there is a straight through ace
    if values == (card_value["A"],
                  card_value['5'],
                  card_value['4'],
                  card_value['3'],
                  card_value['2']) or values == [card_value["A"],
                                                 card_value['5'],
                                                 card_value['4'],
                                                 card_value['3'],
                                                 card_value['2']]:
        return True

    else:
        for i in range(len(values) - 1):
            if values[i] == values[i + 1] + 1:
                value_list.append(True)
            else:
                value_list.append(False)
        return all(value_list)


def isroyalflush(values, suits):
    """Must be straight to Ace and all same suit."""
    return (values == (card_value["A"],
                       card_value['K'],
                       card_value['Q'],
                       card_value['J'],
                       card_value['10']) or
            values == [card_value["A"],
                       card_value['K'],
                       card_value['Q'],
                       card_value['J'],
                       card_value['10']]) and isflush(values, suits)


def isstraightflush(values, suits):
    """Straight flush must be a straight (5 cards of consecutive value) and all of the same suit"""
    return isstraight(values, suits) and isflush(values, suits)


def isfourkind(values, suits):
    """Four cards that are the same and a kicker"""
    return maxconsmatches(values) == 2


def isfullhouse(values, suits):
    """Three of a kind and a pair"""
    return maxconsmatches(values) == 1 and len(set(values)) == 2


def isthreekind(values, suits):
    """Three cards with the same value and two kickers"""
    return maxconsmatches(values) == 1 and len(set(values)) == 3


def ispair(values, suits):
    return maxconsmatches(values) == 0 and len(set(values)) == 4


def istwopair(values, suits):
    return maxconsmatches(values) == 0 and len(set(values)) == 3


def ishighcard(values, suits):
    """No hand, just a high card"""
    return maxconsmatches(values) == 0 and isstraight(values, suits) == False and True not in match_val_bool(values)


def countval(seq):
    """
    Creates a dictionary that counts the number of occurences of each card value.
    Used to return hand composition and calculate hand value.
    """
    four_kind = 0
    three_kind = 0
    pairs = []
    single = []
    counter_list = namedtuple('Counter', 'four_kind three_kind pairs single')
    for value, count in Counter(seq).iteritems():
        if count == 4:
            four_kind = value
        elif count == 3:
            three_kind = value
        elif count == 2:
            pairs.append(value)
        else:
            single.append(value)
    return counter_list(four_kind, three_kind, pairs, single)


def getcard(value):
    """
    Returns the relevant card (rank, i.e. A, 4, 5...) from its value by returning the relevant index from card value.
    """
    return gamevars.card_value.keys()[gamevars.card_value.values().index(value)]


def nranked(sequence, n=1):
    """Gets the nth ranked value in a sequence. Used to compare kicker values."""
    return sorted(sequence, reverse=True)[n - 1]


def calcvalue(values, suits):
    """
    Master hand valuation function which returns the value of a hand.
    Looks up value of hand and cards and computes a score.
    Cards outside ranked hands are weighted by n-highest position to ensure highest card outside ranked hand wins.
    The higher the score, the stronger the hand.
    Also returns the hand rank for pot win computation.
    """

    if isroyalflush(values, suits):
        return (hand_ranks['royal_flush'] * (card_value["A"] *
                                             card_value["K"] *
                                             card_value["Q"] *
                                             card_value["J"] *
                                             card_value["10"]),
                'Royal flush',
                'royal_flush')

    elif isstraightflush(values, suits):

        # This account for value of straight to 5, where the value will be lowest straight flush
        if values == (card_value["A"],
                      card_value["5"],
                      card_value["4"],
                      card_value["3"],
                      card_value["2"]) or values == [card_value["A"],
                                                     card_value["5"],
                                                     card_value["4"],
                                                     card_value["3"],
                                                     card_value["2"]]:

            return (hand_ranks['straight_flush'] *
                    factorial(card_value["5"]),
                    'Straight flush to 5',
                    'straight_flush')

        # All other cases
        else:
            return (hand_ranks['straight_flush'] *
                    reduce(lambda x, y: x * y, values),
                    'Straight flush to ' +
                    str(max(values)),
                    'straight_flush')

    elif isfourkind(values, suits):
        counts = countval(values)
        return (hand_ranks['four_kind'] *
                (counts.four_kind ** 4) +
                counts.single[0],
                "four of a kind of " +
                getcard(counts.four_kind) +
                " and a " + getcard(counts.single[0]),
                'four_kind')

    # Note that the three of a kind determines the winner, weights reflect this
    elif isfullhouse(values, suits):
        counts = countval(values)
        return (hand_ranks['full_house'] *
                (((counts.three_kind * 10) ** 3) +
                 counts.pairs[0] ** 2),
                "full house with three " +
                getcard(counts.three_kind) +
                " and a pair of " +
                getcard(counts.pairs[0]),
                'full_house')


    # Weights on nranked cards ensure highest kicker wins
    elif isflush(values, suits):
        counts = countval(values)
        return (hand_ranks['flush'] * (nranked(values, 1) * 60 +
                                       nranked(values, 2) * 40 +
                                       nranked(values, 3) * 30 +
                                       nranked(values, 4) * 15 +
                                       nranked(values, 5)),
                "Flush of " + suits[0] + " with " +
                str(counts.single),
                'flush')


    elif isstraight(values, suits):
        counts = countval(values)
        return (hand_ranks['straight'] *
                (reduce(lambda x, y: x * y, counts.single)),
                "Straight to " + str(max(counts.single)),
                'straight')


    # Weights reflect importance of highest kicker
    elif isthreekind(values, suits):
        counts = countval(values)
        return (hand_ranks['three_kind'] *
                (counts.three_kind * 20) ** 3 +
                nranked(counts.single, 1) * 20 +
                nranked(counts.single, 2),
                "Three of a kind of " +
                getcard(counts.three_kind) +
                " and " + getcard(counts.single[0]) +
                ", " + getcard(counts.single[1]),
                'three_kind')


    # Weights reflect importance of highest kicker
    elif istwopair(values, suits):
        counts = countval(values)
        return (hand_ranks['two_pair'] *
                (nranked(counts.pairs, 1) * 20) ** 2 *
                (nranked(counts.pairs, 2) * 5) ** 2 +
                counts.single[0],
                "Two pairs of " +
                getcard(counts.pairs[0]) + "&" +
                getcard(counts.pairs[1]) + " and a " +
                getcard(counts.single[0]),
                'two_pair')


    elif ispair(values, suits):
        counts = countval(values)
        return (hand_ranks['one_pair'] *
                counts.pairs[0] ** 2 +
                nranked(counts.single, 1) * 20 +
                nranked(counts.single, 2) * 10 +
                nranked(counts.single, 3),
                "A pair of " +
                getcard(counts.pairs[0]) + " plus " +
                getcard(counts.single[0]) + "," +
                getcard(counts.single[1]) + "," +
                getcard(counts.single[2]),
                'one_pair')


    elif ishighcard(values, suits):
        counts = countval(values)
        return (hand_ranks['high_card'] *
                nranked(counts.single, 1) +
                nranked(counts.single, 2) * 7 +
                nranked(counts.single, 3) * 5 +
                nranked(counts.single, 4) * 3 +
                nranked(counts.single, 5),
                "High card: " +
                getcard(nranked(counts.single, 1)) + " with " +
                getcard(nranked(counts.single, 2)) + "," +
                getcard(nranked(counts.single, 3)) + "," +
                getcard(nranked(counts.single, 4)) + "," +
                getcard(nranked(counts.single, 5)),
                'high_card')
