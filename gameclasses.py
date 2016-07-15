import itertools
import random

import gamevars
from gamevars import card_value, suits, ranks
from handevaluator import calc_value


class Card(object):
    """
    Define card objects
    """

    def __init__(self, rank, suit):
        self.rank = rank
        self.suit = suit
        self.value = card_value[self.rank]

    def __str__(self):
        return self.rank + self.suit


class Deck(object):
    """
    Define deck object with relevant methods
    """

    def __init__(self):
        """
        Create a full 52 cards deck
        """
        self.deck = []
        for suit in suits:
            for rank in ranks:
                self.deck.append(Card(rank, suit))

    def __str__(self):
        deck_comp = " "
        for card in self.deck:
            deck_comp += str(card) + " "
        return deck_comp

    def shuffle(self):
        random.shuffle(self.deck)


class Player(object):
    """
    Define player object
    """

    def __init__(self, name="Player 1"):
        self.name = name
        self.bankroll = gamevars.starting_chips

    def get_bankroll(self):
        return str(self.bankroll)

    def change_bankroll(self, amount):
        self.bankroll += amount


class Pot(object):
    """
    Define pot to keep count of ante, side and call bets
    """
    def __init__(self, owner="Player 1", ante_bet=0, side_bet=0, call_bet=0):
        self.owner = owner
        self.ante_bet = ante_bet
        self.side_bet = side_bet
        self.call_bet = call_bet

    def change_ante(self, amount):
        self.ante_bet += amount

    def change_side(self, amount):
        self.side_bet += amount

    def change_call(self, amount):
        self.call_bet += amount


class PhysHand(object):
    """
    Actual cards in Player and bank hands + community cards.
    """

    def __init__(self, owner):
        self.owner = owner
        self.cards = []

    # Deal function removes cards from the deck
    def deal(self, source, num_cards):
        for i in range(num_cards):
            self.cards.append(source.pop())

    def __str__(self):
        deck_comp = " "
        for card in self.cards:
            deck_comp += str(card) + " "
        return deck_comp


class SynthHand(object):
    """
    Synthetic hand objects that aggregate community cards and bank / player cards. Store hand value and rank
    after relevant methods are executed.
    """

    def __init__(self, owner):
        self.owner = owner
        self.cards = []
        self.ranks = []
        self.suits = []
        # comb_5 represents the list of combinations of 5 cards from the synthetic hand
        self.comb_5 = []
        self.values = []
        self.max_hand_index = []
        self.score = 0
        self.desc = ""
        self.hand_rank = ""

    def __str__(self):
        deck_comp = " "
        for card in self.cards:
            deck_comp += str(card) + " "
        return deck_comp

    # Deal function synthetically adds community cards to the synthetic hand
    def deal(self, source, num_cards):
        for i in range(num_cards):
            self.cards.append(source[i])

        # Reset ranks, suits and values to empty lists so as to not repeat cards
        self.ranks = []
        self.suits = []
        self.values = []

        for card in self.cards:
            self.ranks.append(card.rank)
            self.suits.append(card.suit)
            self.values.append(card.value)

        # Creates combination of 5 hands for calculating best 5-hand out of synthetic hand
        hand_comb = []
        for i in range(len(self.cards)):
            hand_comb.append((self.cards[i].rank, self.cards[i].suit, self.cards[i].value))

        hand_comb_5 = []
        for each in itertools.combinations(hand_comb, 5):
            hand_comb_5.append(each)

        zipped_hand_comb_5 = []
        for each in range(len(hand_comb_5)):
            zipped_hand_comb_5.append(zip(*hand_comb_5[each]))

        for i in range(len(zipped_hand_comb_5)):
            zipped_hand_comb_5[i][2] = sorted(zipped_hand_comb_5[i][2], reverse=True)

        self.comb_5 = zipped_hand_comb_5

    # Gets maximum hand value from the various combinations of 5 cards possible

    def calc_hand_value(self):
        max_hand_val = 0
        max_index = 0
        for number, item in enumerate(range(len(self.comb_5))):
            hand_val = calc_value(self.comb_5[item][2], self.comb_5[item][1])
            if hand_val > max_hand_val:
                max_hand_val = hand_val
                max_index = number
            else:
                max_hand_val = max_hand_val
                max_index = max_index

        self.score = max_hand_val[0]
        self.desc = max_hand_val[1]
        self.hand_rank = max_hand_val[2]
        self.max_hand_index = max_index


