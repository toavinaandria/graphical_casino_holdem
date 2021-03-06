# Note: Rules taken from https://en.wikipedia.org/wiki/Casino_hold_%27em

import Tkinter as tk
import webbrowser
import sys

import gamevars
from gameclasses import Deck, Player, Pot, PhysHand, SynthHand

# To change settings, modify the gamevars.py file
from gamevars import sidebet_paytable, call_multiple, min_sidebet_hand, space_btwn_cards, card_xshrink, card_yshrink, \
    canvas_width, canvas_height, msgbox_wraplength, window_x, window_y, rules_url, handranks_url, cardback_path, \
    bankroll_display_coords, ante_display_coords, sidebet_display_coords, callbet_display_coords

from handevaluator import calc_value

# Create relevant initial game objects
player1 = Player(name="player1")
player1_pot = Pot(owner="player1")

player1_cards = PhysHand(owner='player1')
bank_cards = PhysHand(owner='bank')
community_cards = PhysHand(owner='community')
player1_synth = SynthHand(owner="player1")
bank_synth = SynthHand(owner="bank")
deck = Deck()


# Graphical Interface and main app -------------------------------------------------------------------------------------

class GameApp(tk.Tk):
    def __init__(self, parent):
        tk.Tk.__init__(self, parent)
        self.parent = parent
        self.title("Casino Hold'Em - You versus the bank")
        self.create_menu()
        self.reset_game()
        self.deal_rd1_cards()
        self.create_main_widgets()
        self.display_opening_msg()

    # Validation functions for betting amounts -------------------------------------------------------------------------

    def validate_antebet(self, user_input, new_value):
        """ Used to ensure only positive integers are entered for bets and bets are within bankroll"""
        # Disallows blanks and zero as ante bets are mandatory for progression
        valid_input = new_value in '0123456789' and user_input != '' != 0
        if valid_input:
            minval = 1
            maxval = player1.bankroll + 1
            if int(user_input) not in range(minval, maxval):
                valid_input = False
        if not valid_input:
            self.bell()
        return valid_input

    def validate_sidebet(self, user_input, new_value):
        """ Used to ensure only positive integers are entered for bets and bets are within bankroll"""
        valid_input = new_value in '0123456789' and user_input != ''
        if valid_input:
            minval = 0
            # Maximum value is constrained by the fact that the side bet can only be executed once an ante bet is made
            # Minimum ante bet being 1 chip, if the player were to bet all their bankroll minus 1 chip for the ante bet
            # this would be the extreme scenario.
            maxval = player1.bankroll
            if int(user_input) not in range(minval, maxval):
                valid_input = False
        if not valid_input:
            self.bell()
        return valid_input

    # Game functions --------------------------------------------------------------------------------------------------

    def player_is_bankrupt(self):
        """Boolean that checks whether player is technically bankrupt"""
        # Player needs a minimum of 2 chips to play an ante bet and a sidebet, below that they cannot win a hand, hence
        # why bankrolls below 2 chips are technically bankrupt.

        return player1.bankroll < 2 and player1_pot.ante_bet == 0 and player1_pot.call_bet == 0 and \
                        player1_pot.side_bet == 0

    def restart_window(self):
        """Create a window to ask whether players want to restart with a fresh bankroll if they are bankrupt"""

        # Frame title -------------------------------------------------------------------------------------------------
        self.bankrupt_window = tk.LabelFrame(text="Start a new game with a new bankroll?",
                                             takefocus=True,
                                             relief='raised')

        self.bankrupt_window.pack()

        # Main text ---------------------------------------------------------------------------------------------------
        self.bankrupt_text = tk.Label(self.bankrupt_window,
                                      text="You are bankrupt!",
                                      wraplength=msgbox_wraplength)
        self.bankrupt_text.pack()

        # Restart button ----------------------------------------------------------------------------------------------
        self.restart_button = tk.Button(self.bankrupt_window,
                                        text="Restart with new bankroll",
                                        command=self.reset_bankroll)
        self.restart_button.pack()

        # Quit button -------------------------------------------------------------------------------------------------
        self.quit_button = tk.Button(self.bankrupt_window,
                                     text="Quit",
                                     command=sys.exit)

        self.quit_button.pack()

        # Canvas window------------------------------------------------------------------------------------------------
        self.bankrupt_windowobj = self.background.create_window(window_x,
                                                                window_y,
                                                                window=self.bankrupt_window,
                                                                height=200,
                                                                width=350)

    def eval_hands(self):
        """Evaluate the score of relevant hands to check whether bank qualifies and who wins which round"""

        global player1_synth, bank_synth, player1_cards, community_cards, bank_cards

        # Create synthetic hands from community cards and bank and player cards so they can be evaluated
        player1_synth = SynthHand(owner="player1")
        bank_synth = SynthHand(owner="bank")

        player1_synth.deal(source=player1_cards.cards, num_cards=2)
        player1_synth.deal(source=community_cards.cards, num_cards=3)

        bank_synth.deal(source=bank_cards.cards, num_cards=2)
        bank_synth.deal(source=community_cards.cards, num_cards=3)

        player1_synth.calc_hand_value()
        bank_synth.calc_hand_value()

    # Menu functions -------------------------------------------------------------------------------------------------

    def create_menu(self):
        """Create toplevel menu for help, restarting and exiting the game"""
        menubar = tk.Menu(self.parent)
        self.config(menu=menubar)

        fileMenu = tk.Menu(menubar)
        fileMenu.add_command(label="New Game", command=self.reset_bankroll)
        fileMenu.add_command(label="Exit", command=sys.exit)
        menubar.add_cascade(label="File", menu=fileMenu)

        helpMenu = tk.Menu(menubar)
        helpMenu.add_command(label="Game rules", command=self.show_rules)
        helpMenu.add_command(label="Hand rankings", command=self.show_hand_ranks)
        menubar.add_cascade(label="Help", menu=helpMenu)

    def show_rules(self):
        """Open a browser window with the URL showing game rules"""
        webbrowser.open(rules_url, new=1, autoraise=True)

    def show_hand_ranks(self):
        """Open a browser window with the URL showing hand ranks for help"""
        webbrowser.open(handranks_url, new=1, autoraise=True)

    # -----------------------------------------------------------------------------------------------------------------

    def create_main_widgets(self):
        """Main function to create canvas and Tkinter widgets for GUI and start of game"""

        # Main Background for the game ---------------------------------------------------------------------------------
        self.background = tk.Canvas(width=canvas_width,
                                    height=canvas_height,
                                    bg='green4',
                                    relief='groove')
        self.background.pack()

        # Bottom left corner rectangle with game statistics ------------------------------------------------------------

        self.background.create_rectangle(5,
                                         canvas_height,
                                         canvas_width / 4.5,
                                         window_y,
                                         fill="grey75")

        self.background.create_text(10,
                                    window_y + 10,
                                    text="Bankroll",
                                    anchor='w')

        self.bankroll_display = self.background.create_text(bankroll_display_coords,
                                                            text=str(player1.bankroll) + " chips",
                                                            anchor='e')

        self.background.create_text(10,
                                    window_y + 30,
                                    text="Ante bet:",
                                    anchor="w")

        self.ante_display = self.background.create_text(ante_display_coords,
                                                        text=str(0) + " chips",
                                                        anchor='e')

        self.background.create_text(10,
                                    window_y + 50,
                                    text="AA side bet:",
                                    anchor="w")

        self.sidebet_display = self.background.create_text(sidebet_display_coords,
                                                           text=str(0) + " chips",
                                                           anchor='e')

        self.background.create_text(10,
                                    window_y + 70,
                                    text="Call bet:",
                                    anchor="w")

        self.callbet_display = self.background.create_text(callbet_display_coords,
                                                           text=str(0) + " chips",
                                                           anchor='e')

        # Player Hand Label --------------------------------------------------------------------------------------------

        self.background.create_text(canvas_width - 100,
                                    canvas_height - 180,
                                    text='Your Hand',
                                    anchor='e')

        # Player Hands -------------------------------------------------------------------------------------------------

        self.P1Card1_img = tk.PhotoImage(file=cardback_path).subsample(card_xshrink, card_yshrink)
        self.background.create_image(canvas_width - 200,
                                     canvas_height - 80,
                                     image=self.P1Card1_img)

        self.P1Card2_img = tk.PhotoImage(file=cardback_path).subsample(card_xshrink, card_yshrink)
        self.background.create_image(canvas_width - 200 + space_btwn_cards,
                                     canvas_height - 80,
                                     image=self.P1Card2_img)

        # Initial Community Cards --------------------------------------------------------------------------------------

        self.background.create_text(canvas_width / 3,
                                    canvas_height / 2 - 100,
                                    text="Community Cards",
                                    anchor="w")

        self.CCard1_img = tk.PhotoImage(file=cardback_path).subsample(card_xshrink, card_yshrink)
        self.background.create_image(canvas_width / 3,
                                     canvas_height / 2,
                                     image=self.CCard1_img)

        self.CCard2_img = tk.PhotoImage(file=cardback_path).subsample(card_xshrink, card_yshrink)
        self.background.create_image(canvas_width / 3 + space_btwn_cards,
                                     canvas_height / 2,
                                     image=self.CCard2_img)

        self.CCard3_img = tk.PhotoImage(file=cardback_path).subsample(card_xshrink, card_yshrink)
        self.background.create_image(canvas_width / 3 + space_btwn_cards * 2,
                                     canvas_height / 2,
                                     image=self.CCard3_img)

        # Bank Cards ---------------------------------------------------------------------------------------------------

        self.background.create_text(60,
                                    canvas_height / 5 - 100,
                                    text="Bank Hand",
                                    anchor="w")

        self.BCard1_img = tk.PhotoImage(file=cardback_path).subsample(card_xshrink, card_yshrink)
        self.background.create_image(60,
                                     canvas_height / 5,
                                     image=self.BCard1_img)

        self.BCard2_img = tk.PhotoImage(file=cardback_path).subsample(card_xshrink, card_yshrink)
        self.background.create_image(60 + space_btwn_cards,
                                     canvas_height / 5,
                                     image=self.BCard2_img)

        # Card references for display ---------------------------------------------------------------------------------

        self.P1Card1_rs = str(player1_cards.cards[0])
        self.P1Card2_rs = str(player1_cards.cards[1])

        self.BCard1_rs = str(bank_cards.cards[0])
        self.BCard2_rs = str(bank_cards.cards[1])

        self.CCard1_rs = str(community_cards.cards[0])
        self.CCard2_rs = str(community_cards.cards[1])
        self.CCard3_rs = str(community_cards.cards[2])

    # -----------------------------------------------------------------------------------------------------------------

    # Opening message box ---------------------------------------------------------------------------------------------

    def display_opening_msg(self):
        """Displays the opening message when the game is first started"""

        # Frame title ----------------------------------------------------------------------------------------------
        self.opening_window = tk.LabelFrame(text="Welcome!",
                                            takefocus=True,
                                            relief='raised')

        self.opening_window.pack()

        # Main message ---------------------------------------------------------------------------------------------
        self.opening_window_label = tk.Label(self.opening_window,
                                      text="Welcome to Casino Hold'Em! For game rules or rankings, see " + str(
                                          " Help in the menu bar "),
                                      wraplength=msgbox_wraplength)
        self.opening_window_label.pack()

        # Start game button ----------------------------------------------------------------------------------------
        self.start_game_button = tk.Button(self.opening_window,
                                                text="OK. Start game",
                                                command=self.hide_opening_msg,
                                                state='normal')

        self.start_game_button.pack()

        # Sidebet window object ------------------------------------------------------------------------------------
        self.opening_window_obj = self.background.create_window(window_x,
                                                                window_y,
                                                                window=self.opening_window)

    def hide_opening_msg(self):
        self.background.itemconfig(self.opening_window_obj,
                                   state='hidden')
        self.get_sidebet()

    # -----------------------------------------------------------------------------------------------------------------


    def reset_bankroll(self):
        """Reset bankroll if player was bankrupt and wants to play another round"""
        player1.bankroll = gamevars.starting_chips
        self.play_again()

    def get_antebet(self):
        """Display ante bet window on canvas and store bet value"""

        # Frame title ----------------------------------------------------------------------------------------------
        self.ante_window = tk.LabelFrame(text="Ante Bet",
                                         takefocus=True,
                                         relief='raised')
        self.ante_window.pack()

        # Main message ---------------------------------------------------------------------------------------------
        self.antebet_label = tk.Label(self.ante_window,
                                      text="How much do you want to bet as an ante bet?" + str(
                                      "\n Please note that your call bet will be") + str(
                                      "%sx your ante bet, so ensure you can afford to call." % str(
                                      gamevars.call_multiple)),
                                      wraplength=msgbox_wraplength)
        self.antebet_label.pack()

        # Entry object ---------------------------------------------------------------------------------------------
        self.ante_entry = tk.Spinbox(self.ante_window,
                                     width=5,
                                     from_=1,
                                     to=player1.bankroll,
                                     validate='key',
                                     validatecommand=(self.register(self.validate_antebet), '%P', '%S'))

        self.ante_entry.pack()

        # Confirm button -------------------------------------------------------------------------------------------

        self.confirm_ante_button = tk.Button(self.ante_window,
                                             text="Confirm ante bet",
                                             command=self.confirm_ante,
                                             state='normal')
        self.confirm_ante_button.pack()

        # Window object --------------------------------------------------------------------------------------------
        self.ante_window_obj = self.background.create_window(window_x,
                                                             window_y,
                                                             window=self.ante_window)

    def display_rd1_cards(self):
        """Show the faces of the flop cards on the canvas (which previously were hidden)"""
        self.P1Card1_img = tk.PhotoImage(file="images/" +
                                              self.P1Card1_rs +
                                              ".gif").subsample(card_xshrink,
                                                                card_yshrink)
        self.P1Card2_img = tk.PhotoImage(file="images/" +
                                              self.P1Card2_rs +
                                              ".gif").subsample(card_xshrink,
                                                                card_yshrink)
        self.CCard1_img = tk.PhotoImage(file="images/" +
                                             self.CCard1_rs +
                                             ".gif").subsample(card_xshrink,
                                                               card_yshrink)
        self.CCard2_img = tk.PhotoImage(file="images/" +
                                             self.CCard2_rs +
                                             ".gif").subsample(card_xshrink,
                                                               card_yshrink)
        self.CCard3_img = tk.PhotoImage(file="images/" +
                                             self.CCard3_rs +
                                             ".gif").subsample(card_xshrink, card_yshrink)

        self.background.create_image(canvas_width - 200,
                                     canvas_height - 80,
                                     image=self.P1Card1_img)

        self.background.create_image(canvas_width - 200 + space_btwn_cards,
                                     canvas_height - 80,
                                     image=self.P1Card2_img)

        self.background.create_image(canvas_width / 3,
                                     canvas_height / 2,
                                     image=self.CCard1_img)

        self.background.create_image(canvas_width / 3 + space_btwn_cards,
                                     canvas_height / 2,
                                     image=self.CCard2_img)

        self.background.create_image(canvas_width / 3 + space_btwn_cards * 2,
                                     canvas_height / 2,
                                     image=self.CCard3_img)

    def update_display(self, target, content):
        """
        Allow to change text in game statistics display
        :param target: Object in canvas for which to update text, must be one of the display objects
        :param content: Text to display, must be a string
        """
        self.background.itemconfig(target, text=content)

    def update_rd1_displays(self):
        """Update relevant round 1 displays (i.e. everything except call bet"""
        self.update_display(self.bankroll_display,
                            str(player1.bankroll) + " chips")
        self.update_display(self.ante_display,
                        str(player1_pot.ante_bet) + " chips")
        self.update_display(self.sidebet_display,
                        str(player1_pot.side_bet) + " chips")


    def confirm_ante(self):
        """
        Function to ensure that ante and side bet amounts entered in spinboxes are confirmed only when "Confirm" button
        is pressed. Update bankroll and ante and side bet displays.
        """
        self.update_antebet()
        self.background.itemconfig(self.ante_window_obj,
                                   state='hidden')
        self.update_rd1_displays()
        self.display_rd1_cards()

        # Execute next steps in the program
        # Note - Sidebet amount is requested before ante amount to ensure the player can afford the ante and call bet
        self.eval_hands()
        self.exec_side_bet()

    def get_sidebet(self):
        """Open sidebet window to get sidebet amounts"""

        self.display_opening_msg()

        if self.player_is_bankrupt():
            self.restart_window()
        else:

            # Frame title ----------------------------------------------------------------------------------------------
            self.sidebet_window = tk.LabelFrame(text="AA Side bet",
                                                takefocus=True,
                                                relief='raised')

            self.sidebet_window.pack()

            # Main message ---------------------------------------------------------------------------------------------
            self.sidebet_label = tk.Label(self.sidebet_window,
                                          text="How much do you want to bet as an AA side bet?" + str(
                                          "\n You will need at least a pair of A at the flop to win. ") + str(
                                          "The side bet will be placed after the ante bet and will be based") + str(
                                          " on the flop cards.") + str(
                                          "\nIf you do not want to place an AA side") + str(
                                          "bet, please leave the number as zero"),
                                          wraplength=msgbox_wraplength)

            self.sidebet_label.pack()

            # Sidebet entry box ----------------------------------------------------------------------------------------
            self.sidebet_entry = tk.Spinbox(self.sidebet_window,
                                            width=5,
                                            from_=0,
                                            to=player1.bankroll,
                                            validate='key',
                                            validatecommand=(self.register(self.validate_sidebet), '%P', '%S'))
            self.sidebet_entry.pack()

            # Sidebet confirm button -----------------------------------------------------------------------------------
            self.sidebet_confirm_button = tk.Button(self.sidebet_window,
                                                    text="Confirm AA side bet",
                                                    command=self.confirm_sidebet,
                                                    state='normal')

            self.sidebet_confirm_button.pack()

            # Sidebet window object ------------------------------------------------------------------------------------
            self.sidebet_window_obj = self.background.create_window(window_x,
                                                                    window_y,
                                                                    window=self.sidebet_window)

    def confirm_sidebet(self):
        """Get relevant sidebet value and hide sidebet window"""
        self.update_sidebet()
        self.background.itemconfig(self.sidebet_window_obj,
                                   state='hidden')
        self.update_rd1_displays()

        # Execute next step in the program - requests ante bet amount
        self.get_antebet()

    def update_antebet(self):
        """Update ante bet value and bankroll from spinbox"""
        player1_pot.ante_bet = int(self.ante_entry.get())
        player1.change_bankroll(- player1_pot.ante_bet)

    def update_sidebet(self):
        """Update sidebet value and bankroll from spinbox"""
        player1_pot.side_bet = int(self.sidebet_entry.get())
        player1.change_bankroll(- player1_pot.side_bet)

    def reset_game(self):
        """Shuffle the deck, empty all hands and create initial cards (without resetting bankroll)"""
        global deck, player1_cards, bank_cards, community_cards
        deck = Deck()
        deck.shuffle()
        player1_cards = PhysHand(owner='player1')
        bank_cards = PhysHand(owner='bank')
        community_cards = PhysHand(owner='community')

    def deal_rd1_cards(self):
        """Deal 2 cards to each of player and bank, and 3 community cards for the flop"""
        global player1_cards, bank_cards, community_cards

        player1_cards.deal(source=deck.deck, num_cards=2)
        bank_cards.deal(source=deck.deck, num_cards=2)
        community_cards.deal(source=deck.deck, num_cards=3)

    def exec_side_bet(self):
        """Execute side bet procedures and update displays accordingly"""
        if player1_pot.side_bet > 0:

            # Calculates minimum value required to win side bet - a pair of Aces as a default
            side_bet_threshold = calc_value(min_sidebet_hand[0], min_sidebet_hand[1])

            if player1_synth.score >= side_bet_threshold[0]:
                payout = (
                             1 + sidebet_paytable[
                                 player1_synth.hand_rank]) * player1_pot.side_bet  # Returns original stake

                player1.change_bankroll(payout)

                self.display_AA_result(title="AA side bet - You Win!",
                                       text="You have won the AA side bet with the following hand" + str(
                                        ": %s. You have won %s chips") % (player1_synth.desc,str(
                                        payout - player1_pot.side_bet)))

                self.update_display(self.bankroll_display,
                                    str(player1.bankroll) + " chips")

                # Reset side bet
                player1_pot.side_bet = 0

                self.update_display(self.sidebet_display,
                                    str(player1_pot.side_bet) + " chips")

            else:
                self.display_AA_result(title="AA side bet - You've Lost!",
                                       text="Your hand: %s is too weak to win the AA side bet." % player1_synth.desc +
                                            str("You have lost your side bet of %s chips. ") % str(
                                                player1_pot.side_bet))

                # Reset side bet
                player1_pot.side_bet = 0

                self.update_display(self.sidebet_display,
                                    str(player1_pot.side_bet) + " chips")

                if self.player_is_bankrupt():
                    self.restart_window()
                else:
                    pass
        else:
            self.begin_round2()

    def display_AA_result(self, title, text):
        """Display results of AA sidebet with button allowing player to continue on"""

        # Frame title -------------------------------------------------------------------------------------------------

        self.results_window = tk.LabelFrame(text=title,
                                            takefocus=True,
                                            relief='raised')
        self.results_window.pack()

        # Frame main text --------------------------------------------------------------------------------------------
        self.results_label = tk.Label(self.results_window,
                                      text=text,
                                      wraplength=msgbox_wraplength)
        self.results_label.pack()

        # Continue button --------------------------------------------------------------------------------------------
        self.continue_button = tk.Button(self.results_window,
                                         text="Continue",
                                         command=lambda: self.begin_round2())
        self.continue_button.pack()

        # Window object ---------------------------------------------------------------------------------------------
        self.results_windowobj = self.background.create_window(window_x,
                                                               window_y,
                                                               window=self.results_window)

    def begin_round2(self):
        """Begin procedure after ante and side bets, asking player whether they want to fold or call after flop"""

        # Removes sidebet window only if has been created, otherwise continues to next step
        try:
            self.background.itemconfig(self.results_windowobj, state="hidden")
        except:
            pass

        if player1.bankroll < call_multiple * player1_pot.ante_bet:

            self.show_cannot_call_display("Can't afford call bet")

            player1_pot.ante_bet = 0
            self.update_display(self.ante_display, str(player1_pot.ante_bet) + " chips ")

        else:
            # Frame title -----------------------------------------------------------------------------------------
            self.foldorcall_window = tk.LabelFrame(text="Fold or Call?",
                                                   takefocus=True,
                                                   relief='raised')
            self.foldorcall_window.pack()

            # Frame main text -------------------------------------------------------------------------------------
            self.foldorcalltxt = "You currently have the following hand: \n %s. Do you want " % (
                player1_synth.desc) + str(
                "to fold or call? If you call, your call bet will be %s x the ante bet" % (str(call_multiple)) + str(
                    ", ie. %s chips.") % (str(player1_pot.ante_bet * call_multiple)))

            self.foldorcall_text = tk.Label(self.foldorcall_window,
                                            text=self.foldorcalltxt,
                                            wraplength=msgbox_wraplength)
            self.foldorcall_text.pack()

            # Fold button ----------------------------------------------------------------------------------------
            self.fold_button = tk.Button(self.foldorcall_window,
                                         text="Fold",
                                         command=self.fold)
            self.fold_button.pack(side='left', expand=True, ipadx=50)

            # Call button ----------------------------------------------------------------------------------------
            self.call_button = tk.Button(self.foldorcall_window,
                                         text="Call",
                                         command=self.call)
            self.call_button.pack(side='right', expand=True, ipadx=50)

            # Window object -------------------------------------------------------------------------------------
            self.foldorcall_windowobj = self.background.create_window(window_x,
                                                                      window_y,
                                                                      window=self.foldorcall_window)

    def fold(self):
        """ Procedure once player decides to fold"""

        self.background.itemconfig(self.foldorcall_windowobj, state="hidden")

        # Frame title -----------------------------------------------------------------------------------------
        self.foldresult_window = tk.LabelFrame(text="You have folded",
                                               takefocus=True,
                                               relief='raised')

        self.foldresult_window.pack()

        # Main text -------------------------------------------------------------------------------------------
        self.foldtext = "You have folded. You lose your ante outlay (%s chips)" % (str(player1_pot.ante_bet))

        self.foldresult_text = tk.Label(self.foldresult_window,
                                        text=self.foldtext,
                                        wraplength=msgbox_wraplength)

        self.foldresult_text.pack()

        player1_pot.ante_bet = 0
        self.update_display(self.ante_display, str(player1_pot.ante_bet) + " chips")

        if self.player_is_bankrupt():
            self.restart_window()

        else:
            self.play_again_text = tk.Label(self.foldresult_window,
                                            text="Do you want to play again?")
            self.play_again_text.pack()

            # Play again button -----------------------------------------------------------------------------
            self.play_again_button = tk.Button(self.foldresult_window,
                                               text="Yes",
                                               command=self.play_again)
            self.play_again_button.pack(side='left', expand=True, ipadx=50)

            # Quit button -----------------------------------------------------------------------------------
            self.quit_button = tk.Button(self.foldresult_window,
                                         text="No. Quit",
                                         command=sys.exit)
            self.quit_button.pack(side='right', expand=True, ipadx=50)

            # Window object ---------------------------------------------------------------------------------
            self.foldresult_windowobj = self.background.create_window(window_x,
                                                                      window_y,
                                                                      window=self.foldresult_window)

    def call(self):
        """Procedure assuming player wants to call after the flop"""
        player1_pot.call_bet = call_multiple * player1_pot.ante_bet
        player1.change_bankroll(-player1_pot.call_bet)

        self.update_display(self.bankroll_display,
                            str(player1.bankroll) + " chips")
        self.update_display(self.callbet_display,
                            str(player1_pot.call_bet) + " chips")

        self.final_round()

    def show_bank_cards(self):
        """Display bank cards for the final round once player calls the bet"""
        self.BCard1_img = tk.PhotoImage(file="images/" +
                                             self.BCard1_rs +
                                             ".gif").subsample(card_xshrink,
                                                               card_yshrink)

        self.BCard2_img = tk.PhotoImage(file="images/" +
                                             self.BCard2_rs +
                                             ".gif").subsample(card_xshrink,
                                                               card_yshrink)
        self.background.create_image(60,
                                     canvas_height / 5,
                                     image=self.BCard1_img)

        self.background.create_image(60 + space_btwn_cards,
                                     canvas_height / 5,
                                     image=self.BCard2_img)

    def deal_rd2_cards(self):
        """Deal an extra 2 community cards for the final round and displays them"""
        global community_cards

        community_cards.deal(source=deck.deck, num_cards=2)

        # Get references to display community cards to display
        self.CCard4_rs = str(community_cards.cards[3])
        self.CCard5_rs = str(community_cards.cards[4])

        # Display the cards on the canvas
        self.CCard4_img = tk.PhotoImage(file="images/" +
                                             self.CCard4_rs +
                                             ".gif").subsample(card_xshrink,
                                                               card_yshrink)
        self.CCard5_img = tk.PhotoImage(file="images/" +
                                             self.CCard5_rs +
                                             ".gif").subsample(card_xshrink,
                                                               card_yshrink)

        self.background.create_image(canvas_width / 3 + space_btwn_cards * 3,
                                     canvas_height / 2,
                                     image=self.CCard4_img)
        self.background.create_image(canvas_width / 3 + space_btwn_cards * 4,
                                     canvas_height / 2,
                                     image=self.CCard5_img)

    def prep_rd2_hands(self):
        """Prepare round 2 synthetic hands for evaluation function"""
        global community_cards

        # Reset synthetic hands to recreate them - New round 2 object for player 1 synthetic hand required as ante hand
        # used to calculate ante payout in certain cases

        self.player1_synth_rd2 = SynthHand(owner="player1")
        self.bank_synth = SynthHand(owner="bank")

        self.player1_synth_rd2.deal(source=player1_cards.cards, num_cards=2)
        self.bank_synth.deal(source=bank_cards.cards, num_cards=2)
        self.player1_synth_rd2.deal(source=community_cards.cards, num_cards=5)
        self.bank_synth.deal(source=community_cards.cards, num_cards=5)

    def eval_rd2_hands(self, hand):
        """
        Run hand evaluation function and returns value tuple for use in final round calculations
        hand: Must be a SynthHand object
        """
        return hand.calc_hand_value()

    def define_rd2_outcome(self):
        """Check player hand vs bank hand to determine what outcome is shown to player"""

        # Determine whether bank qualifies with a sufficiently large hand
        self.bank_qualifies_rd2 = 0
        if self.bank_synth.score >= calc_value(gamevars.min_bank_hand[0], gamevars.min_bank_hand[1])[0]:
            self.bank_qualifies_rd2 = 1
        else:
            self.bank_qualifies_rd2 = 0

        # Determine which process to run depending on winner
        if self.bank_qualifies_rd2 == 0:
            self.bank_not_qualified()
        else:
            if self.player1_synth_rd2.score > self.bank_synth.score:
                self.player1_wins()

            elif self.player1_synth_rd2.score < self.bank_synth.score:
                self.bank_wins()

            else:
                self.tie()

    def player1_wins(self):
        """Calculate returns for player for round 2 and ask whether player wants to play again"""
        ante_payout = gamevars.antewin_paytable[player1_synth.hand_rank] * player1_pot.ante_bet

        # Frame title -----------------------------------------------------------------------------------
        self.rd2_result_window = tk.LabelFrame(text="You have won!",
                                               takefocus=True,
                                               relief='raised')

        self.rd2_result_window.pack()
        # Main text -----------------------------------------------------------------------------------
        self.wintext = "Your hand is: %s. \n The bank's hand is: %s." % (str(self.player1_synth_rd2.desc),
                                                                         str(self.bank_synth.desc)) + str(
            "\n You win! Your call bet of %s chips wins 1:1 and your ante bet wins %s chips." % (
                str(player1_pot.call_bet),
                str(ante_payout)))

        player1.change_bankroll(ante_payout + player1_pot.ante_bet + player1_pot.call_bet * 2)
        self.reset_bets()
        self.update_rd2_displays()

        self.rd2_result_text = tk.Label(self.rd2_result_window,
                                        text=self.wintext,
                                        wraplength=msgbox_wraplength)
        self.rd2_result_text.pack()

        self.play_again_text = tk.Label(self.rd2_result_window,
                                        text="Do you want to play again?")
        self.play_again_text.pack()

        # Play again button --------------------------------------------------------------------------
        self.play_again_button = tk.Button(self.rd2_result_window,
                                           text="Yes",
                                           command=self.play_again)

        self.play_again_button.pack(side='left', expand=True, ipadx=50)

        # Quit button ----------------------------------------------------------------------------------
        self.quit_button = tk.Button(self.rd2_result_window,
                                     text="No. Quit",
                                     command=sys.exit)
        self.quit_button.pack(side='right', expand=True, ipadx=50)

        # Window object --------------------------------------------------------------------------------
        self.rd2_result_windowobj = self.background.create_window(window_x,
                                                                  window_y,
                                                                  window=self.rd2_result_window)

    def bank_wins(self):
        """Display relevant messages for player for round 2 and ask whether player wants to play again after bank win"""

        # Frame title --------------------------------------------------------------------------------
        self.rd2_result_window = tk.LabelFrame(text="The bank wins!",
                                               takefocus=True,
                                               relief='raised')

        self.rd2_result_window.pack()

        self.reset_bets()
        self.update_rd2_displays()

        # Main text  -------------------------------------------------------------------------------------
        self.wintext = "Your hand is: %s. \n The bank's hand is: %s." % (str(self.player1_synth_rd2.desc),
                                                                         str(self.bank_synth.desc)) + str(
            "\n You lose! Your have lost your bets.")

        self.rd2_result_text = tk.Label(self.rd2_result_window,
                                        text=self.wintext,
                                        wraplength=msgbox_wraplength)

        self.rd2_result_text.pack()

        self.play_again_text = tk.Label(self.rd2_result_window,
                                        text="Do you want to play again?")

        self.play_again_text.pack()

        # Play again button -------------------------------------------------------------------------------
        self.play_again_button = tk.Button(self.rd2_result_window,
                                           text="Yes",
                                           command=self.play_again)
        self.play_again_button.pack(side='left', expand=True, ipadx=50)

        # Quit button -------------------------------------------------------------------------------------
        self.quit_button = tk.Button(self.rd2_result_window,
                                     text="No. Quit",
                                     command=sys.exit)
        self.quit_button.pack(side='right', expand=True, ipadx=50)

        # Window object -----------------------------------------------------------------------------------
        self.rd2_result_windowobj = self.background.create_window(window_x,
                                                                  window_y,
                                                                  window=self.rd2_result_window)

    def tie(self):
        """Display relevant messages for player for round 2 and ask whether player wants to play again after tie"""

        player1.change_bankroll(player1_pot.ante_bet + player1_pot.call_bet)
        self.reset_bets()
        self.update_rd2_displays()

        # Frame title -------------------------------------------------------------------------------------
        self.rd2_result_window = tk.LabelFrame(text="This round is a tie!",
                                               takefocus=True,
                                               relief='raised')

        self.rd2_result_window.pack()

        # Main message -------------------------------------------------------------------------------------
        self.wintext = "Your hand is: %s. \n The bank's hand is: %s." % (str(self.player1_synth_rd2.desc),
                                                                         str(self.bank_synth.desc)) + str(
            "\n This round is a tie. You get your bets back.")

        self.rd2_result_text = tk.Label(self.rd2_result_window,
                                        text=self.wintext,
                                        wraplength=msgbox_wraplength)

        self.rd2_result_text.pack()

        self.play_again_text = tk.Label(self.rd2_result_window,
                                        text="Do you want to play again?")

        self.play_again_text.pack()

        # Play again button --------------------------------------------------------------------------------
        self.play_again_button = tk.Button(self.rd2_result_window,
                                           text="Yes",
                                           command=self.play_again)
        self.play_again_button.pack(side='left', expand=True, ipadx=50)

        # Quit button -------------------------------------------------------------------------------------
        self.quit_button = tk.Button(self.rd2_result_window,
                                     text="No. Quit",
                                     command=sys.exit)
        self.quit_button.pack(side='right', expand=True, ipadx=50)

        # Window object -----------------------------------------------------------------------------------
        self.rd2_result_windowobj = self.background.create_window(window_x,
                                                                  window_y,
                                                                  window=self.rd2_result_window)

    def update_rd2_displays(self):
        """Update the display of all bet and bankroll statistics post final-round"""

        self.update_display(self.bankroll_display, str(player1.bankroll) + " chips")
        self.update_display(self.ante_display, str(player1_pot.ante_bet) + " chips")
        self.update_display(self.callbet_display, str(player1_pot.call_bet) + " chips")

    def reset_bets(self):
        """Reset bets to zero"""
        player1_pot.ante_bet = 0
        player1_pot.call_bet = 0
        player1_pot.side_bet = 0

    def bank_not_qualified(self):
        """Procedure to run when bank's hand is too weak to qualify for the second round"""

        payout = gamevars.antewin_paytable[player1_synth.hand_rank] * player1_pot.ante_bet

        # Frame title -------------------------------------------------------------------------------------
        self.rd2_result_window = tk.LabelFrame(text="The bank's hand is too weak to qualify! ",
                                               takefocus=True,
                                               relief='raised')

        self.rd2_result_window.pack()

        # Main text -------------------------------------------------------------------------------------
        self.not_qualified_text = "The bank does not qualify." + \
                                  str("Your call bet of %s chips is returned " % str(player1_pot.call_bet)) + str(
            "and your ante bet wins. Your win based on your ante hand is %s chips." % str(payout))

        player1.change_bankroll(player1_pot.call_bet + payout + player1_pot.ante_bet)
        self.reset_bets()
        self.update_rd2_displays()

        self.rd2_result_text = tk.Label(self.rd2_result_window,
                                        text=self.not_qualified_text,
                                        wraplength=msgbox_wraplength)

        self.rd2_result_text.pack()

        self.play_again_text = tk.Label(self.rd2_result_window,
                                        text="Do you want to play again?")

        self.play_again_text.pack()

        # Play again button ------------------------------------------------------------------------------
        self.play_again_button = tk.Button(self.rd2_result_window,
                                           text="Yes",
                                           command=self.play_again)
        self.play_again_button.pack(side='left', expand=True, ipadx=50)

        # Quit button ------------------------------------------------------------------------------------
        self.quit_button = tk.Button(self.rd2_result_window,
                                     text="No. Quit",
                                     command=sys.exit)
        self.quit_button.pack(side='right', expand=True, ipadx=50)

        # Window object ----------------------------------------------------------------------------------
        self.rd2_result_windowobj = self.background.create_window(window_x,
                                                                  window_y,
                                                                  window=self.rd2_result_window)

    def play_again(self):
        """Delete the canvas and reset the game to the first round"""
        self.background.destroy()
        self.reset_game()
        self.deal_rd1_cards()
        self.create_main_widgets()
        self.get_sidebet()

    def final_round(self):
        """Execute final round procedures"""
        self.background.itemconfig(self.foldorcall_windowobj, state='hidden')

        self.show_bank_cards()
        self.deal_rd2_cards()
        self.prep_rd2_hands()
        self.eval_rd2_hands(self.player1_synth_rd2)
        self.eval_rd2_hands(self.bank_synth)
        self.define_rd2_outcome()

    def show_cannot_call_display(self, title):
        """
        Procedure if player cannot call the bet due to insufficient funds (Possible because the player could
        win the sidebet and then have sufficient funds to call)
        """

        # Frame title-------------------------------------------------------------------------------------
        self.cannot_call_window = tk.LabelFrame(text=title,
                                                takefocus=True,
                                                relief='raised')
        self.cannot_call_window.pack()

        # Main text -------------------------------------------------------------------------------------
        self.cannot_call_text = tk.Label(self.cannot_call_window,
                                         text="You cannot afford to call the bet. You lose your ante bet.",
                                         wraplength=msgbox_wraplength)
        self.cannot_call_text.pack()

        if self.player_is_bankrupt():
            self.bankrupt_text = tk.Label(self.cannot_call_window,
                                          text="You are bankrupt!",
                                          wraplength=msgbox_wraplength)
            self.bankrupt_text.pack()

            # Restart button -------------------------------------------------------------------------------------
            self.restart_button = tk.Button(self.cannot_call_window,
                                            text="Restart with new bankroll",
                                            command=self.reset_bankroll)
            self.restart_button.pack()

            # Window object -----------------------------------------------------------------------------------
            self.cannot_call_windowobj = self.background.create_window(window_x,
                                                                       window_y,
                                                                       window=self.cannot_call_window)

        else:
            self.play_again_text = tk.Label(self.cannot_call_window,
                                            text="Do you want to play again?")
            self.play_again_text.pack()

            # Play again button -------------------------------------------------------------------------------
            self.play_again_button = tk.Button(self.cannot_call_window,
                                               text="Yes",
                                               command=self.play_again)
            self.play_again_button.pack()

            # Quit button -------------------------------------------------------------------------------------
            self.quit_button = tk.Button(self.cannot_call_window,
                                         text="No, quit",
                                         command=sys.exit)
            self.quit_button.pack()

            # Window object -----------------------------------------------------------------------------------
            self.cannot_call_windowobj = self.background.create_window(window_x,
                                                                       window_y,
                                                                       window=self.cannot_call_window)


app = GameApp(None)
app.mainloop()
