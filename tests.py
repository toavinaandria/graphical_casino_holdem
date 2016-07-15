"""
Note that this file is geared for using PyCharm's testing procedures
"""

from unittest import TestCase

from gameclasses import Player, Card, Deck, Pot, PhysHand
from handevaluator import match_val_bool, maxconsmatches, isflush, isstraight, isroyalflush, isstraightflush, \
    isfourkind, isfullhouse, isthreekind, ispair, istwopair, ishighcard, countval, getcard, nranked, calc_value
from collections import namedtuple, Counter

# Used for testing certain classes
card_value = {'A': 14, 'K':13}
Counter = namedtuple('Counter', 'four_kind three_kind pairs single')


# Test gameclasses -----------------------------------------------------------------------------------------------------

class TestCard(TestCase):
    """Test the Card class used in gameclasses"""

    def setUp(self):
        # Try out an Ace of spades
        self.example_card = Card('A', 'S')

    def testvalue(self):
        self.assertEqual(self.example_card.value, 14)

    def teststr(self):
        """ Test what should be returned if a card is shown as a string"""
        self.assertEqual(str(self.example_card), 'AS')


class TestDeck(TestCase):
    """ Test that the deck returns appropriate cards"""

    def setUp(self):
        self.deck = Deck()

    def teststr(self):
        """Test what should be returned if deck is shown as a string"""
        self.assertEqual(str(self.deck),
                         ' 2H 3H 4H 5H 6H 7H 8H 9H 10H JH QH KH AH 2S 3S 4S 5S 6S 7S 8S 9S 10S JS QS KS AS 2D 3D 4D 5D' +
                         ' 6D 7D 8D 9D 10D JD QD KD AD 2C 3C 4C 5C 6C 7C 8C 9C 10C JC QC KC AC ')

    def testshuffle(self):
        """Ensure that shuffle returns changed deck"""
        self.assertNotEqual(str(self.deck.shuffle()),
                            ' 2H 3H 4H 5H 6H 7H 8H 9H 10H JH QH KH AH 2S 3S 4S 5S 6S 7S 8S 9S 10S JS QS KS AS 2D 3D 4D' +
                            ' 5D 6D 7D 8D 9D 10D JD QD KD AD 2C 3C 4C 5C 6C 7C 8C 9C 10C JC QC KC AC ')


class TestPlayer(TestCase):
    """Test the Player class used in gameclasses"""

    def setUp(self):
        self.player1 = Player(name="Player 1")
        self.player1.bankroll = 2000

    def test_get_bankroll(self):
        self.assertEqual(self.player1.get_bankroll(), '2000')

    def test_change_bankroll(self):
        self.player1.change_bankroll(-500)
        self.assertEqual(self.player1.bankroll, 1500)


class TestPot(TestCase):
    """Test the Pot class used in gameclasses"""

    def setUp(self):
        self.player1 = Player(name="Player 1")
        self.player1_pot = Pot(owner="Player 1", ante_bet=10, side_bet=20, call_bet=20)

    def testchange_ante(self):
        self.player1_pot.change_ante(20)
        self.assertEqual(self.player1_pot.ante_bet, 30)

    def testchange_side(self):
        self.player1_pot.change_side(20)
        self.assertEqual(self.player1_pot.side_bet, 40)

    def testchange_call(self):
        self.player1_pot.change_call(-10)
        self.assertEqual(self.player1_pot.call_bet, 10)


class TestPhysHand(TestCase):
    """Test the PhysHand class used in gameclasses"""

    def setUp(self):
        self.sample_hand = PhysHand(owner='Sample Player')
        self.deck = Deck()
        # Take the last two cards from an unshuffled deck as an example (i.e. AC and KC)
        self.sample_hand.deal(self.deck.deck, 2)

    def test_deal(self):
        self.assertEqual(str(self.sample_hand.cards[0]) + ' ' + str(self.sample_hand.cards[1]), 'AC KC')

    def teststr(self):
        self.assertEqual(str(self.sample_hand), ' AC KC ')


# TODO - Create test for SynthHand in gameclasses

# --------------------------------------------------------------------------------------------------------------------

# Test handevaluator -------------------------------------------------------------------------------------------------


class Testmatchvalbool(TestCase):
    """Test the match_val_bool class in handevaluator"""

    def testasequence(self):
        self.assertEqual(match_val_bool((2, 2, 4, 5, 6, 6)), [True, False, False, False, True])


class Testmaxconsmatches(TestCase):
    def testasequence(self):
        # Should show only one consecutive match below as it's true twice that there are two consecutive matching
        # numbers (i.e. True, True for 2,2,2, and therefore 1x consecutive)
        self.assertEqual(maxconsmatches((2, 2, 2, 5, 6, 6)), 1)


class Testhands(TestCase):
    """Check that functions correctly identify hands """

    def testflush(self):
        self.assertEqual(isflush((2, 3, 4, 5, 9), ('S', 'S', 'S', 'S', 'S')), True)

    def teststraightto5(self):
        """Test special case of A,2,3,4,5 straight"""
        self.assertEqual(isstraight((14, 5, 4, 3, 2), ('H', 'S', 'S', 'S', 'S')), True)

    def teststraightstd(self):
        self.assertEqual(isstraight((9, 8, 7, 6, 5), ('H', 'S', 'S', 'S', 'S')), True)

    def testroyalflush(self):
        self.assertEqual(isroyalflush((14, 13, 12, 11, 10), ('S', 'S', 'S', 'S', 'S')), True)

    def teststraightflush(self):
        self.assertEqual(isstraightflush((13, 12, 11, 10, 9), ('S', 'S', 'S', 'S', 'S')), True)

    def testisfourkind(self):
        self.assertEqual(isfourkind((14, 5, 5, 5, 5), ('H', 'S', 'S', 'S', 'S')), True)

    def testisfullhouse(self):
        self.assertEqual(isfullhouse((14, 14, 14, 5, 5), ('H', 'S', 'S', 'S', 'S')), True)

    def testisthreekind(self):
        self.assertEqual(isthreekind((13, 13, 13, 5, 2), ('H', 'S', 'S', 'S', 'S')), True)

    def testistwopair(self):
        self.assertEqual(istwopair((12, 12, 11, 11, 2), ('H', 'S', 'S', 'S', 'S')), True)

    def testispair(self):
        self.assertEqual(ispair((14, 10, 10, 5, 3), ('H', 'S', 'S', 'S', 'S')), True)

    def testishighcard(self):
        self.assertEqual(ishighcard((14, 10, 8, 7, 4), ('H', 'S', 'S', 'S', 'S')), True)

    def testcountval(self):
        self.assertEqual(countval((14,14,14,3,3)), Counter(four_kind=0, three_kind=14, pairs=[3], single=[]))

    def testgetcard(self):
        self.assertEqual(getcard(13),'K')

    def testnranked(self):
        self.assertEqual(nranked((4,3,2), n=2),3)

    def testcalc_value(self):
        self.assertEqual(calc_value((14, 10, 8, 7, 4), ('H', 'S', 'S', 'S', 'S')),(275, 'High card: A with 10,8,7,4',
                                                                                   'high_card'))
# --------------------------------------------------------------------------------------------------------------------









