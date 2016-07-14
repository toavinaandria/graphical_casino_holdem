# Hearts, Spades, Diamonds, Clubs
suits = ('H', 'S', 'D', 'C')

ranks = ('2', '3', '4', '5', '6',
         '7', '8', '9', '10',
         'J', 'Q', 'K', 'A')

card_value = {'2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7,
              '8': 8, '9': 9, '10': 10, 'J': 11, 'Q': 12,
              'K': 13, 'A': 14}

# Multiples represent value multiplier used in hand evaluator
hand_ranks = {'high_card': 10, 'one_pair': 25,
              'pair_ace': 100, 'two_pair': 1000,
              'three_kind': 10 ** 4, 'straight': 10 ** 5,
              'flush': 10 ** 6, 'full_house': 10 ** 7,
              'four_kind': 10 ** 8, 'straight_flush': 10 ** 9,
              'royal_flush': 10 ** 10}

# Multiple of ante pot won if ante bet wins
antewin_paytable = {'royal_flush': 100, 'straight_flush': 20,
                    'four_kind': 10, 'full_house': 3,
                    'flush': 2, 'straight': 1,
                    'three_kind': 1, 'two_pair': 1,
                    'pair_ace': 1, 'one_pair': 1,
                    'high_card': 1}

# Multiple of sidebet pot won if side bet wins
sidebet_paytable = {'royal_flush': 100, 'straight_flush': 50,
                    'four_kind': 40, 'full_house': 30,
                    'flush': 20, 'straight': 7,
                    'three_kind': 7, 'two_pair': 7,
                    'pair_ace': 7, 'one_pair': 1,
                    'high_card': 1}

# Default number of starting chips for a player
starting_chips = 500

# Default multiple of ante bet the call bet represents
call_multiple = 2

# Represents the minimum hand required to win
min_sidebet_hand = ((card_value['A'],
                     card_value['A'],
                     card_value['4'],
                     card_value['3'],
                     card_value['2']),
                    ('H', 'S', 'S', 'C', 'D'))

# Represents the minimum hand required for the bank to qualify for the call bet
min_bank_hand = ((card_value['5'],
                  card_value['4'],
                  card_value['4'],
                  card_value['3'],
                  card_value['2']),
                 ('H', 'S', 'S', 'C', 'D'))

# Default betting amounts displayed
default_ante = 10
default_sidebet = 0

# Spacing between card displays
space_btwn_cards = 110

# Factor by which card GIF images are shrunk for both x and y coordinates
card_xshrink = 5
card_yshrink = 5

# Size of the main game window
canvas_width = 800
canvas_height = 600

# Length of pixels after which text will wrap to the next line in message boxes
msgbox_wraplength = 300

# Default messagebox placement on canvas
window_x = canvas_width / 2.2
window_y = canvas_height / 1.2

# Help webpage links
rules_url = "https://en.wikipedia.org/wiki/Casino_hold_%27em#Rules"
handranks_url = "http://www.cardplayer.com/rules-of-poker/hand-rankings"

# Path to card back image
cardback_path = "images/Back.gif"

# Variables for coordinates of various data displays
bankroll_display_coords = (45 + 120, window_y + 10)
ante_display_coords = (45 + 120, window_y + 30)
sidebet_display_coords = (45 + 120, window_y + 50)
callbet_display_coords = (45 + 120, window_y + 70)
