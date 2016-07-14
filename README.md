# graphical_casino_holdem ---------------------------------------------
A casino hold'em game in Python 2.x with one player versus the bank created from scratch to improve my general programming skills,
object-oriented programming and using GUIs to improve interaction versus text-based games.

# Requirements ----------------------------------------------------------
The game uses standard Python 2.x libraries (collections, math, itertools, random, Tkinter, webbrowser) so you should be able to run
it from most Python 2.x environments.

# Running the game -----------------------------------------------------
To run the game, you need run the maingame.py file using a Python 2.7+ interpreter. If you do not know the rules or need to check hand
rankings, please look at the "Help" menu.

You can change some of the configuration of the game in the gamevars.py file, but beware that if you do not know what you are doing, 
you may break the game.

You can restart the game at any time by going to the "File" menu and selecting "New Game".

# Overview of various files --------------------------------------------
<Images/>
The Images folder contains all card and card back images in GIF format. See credit for source

<gameclasses.py>
This contains classes used to create card, hand and player objects for use by the main game

<gamevars.py>
This contains the main variables to modify the look or behaviour of the game

<handevaluator.py>
This is the crux of the engine and contains the code required to evaluate the strength of poker hands. It was relatively complex to
code due to many intricacies, but could be used for other poker games

<maingame.py>
This is the main file which contains the main game functions, logic and GUI

# Development Process ------------------------------------------------------
If you are curious as to how I developed the program, this was my process, which you may find helpful if you are learning
programming:
1) Thourough review of game steps, requirements and logic, step-by-step in a notebook, with very rough pseudo-code
2) Creation of the main classes to generate necessary objects (cards, player and pots)
3) Creation of a text-version of the game logic up to the point where hands needed to be compared
4) Scoping and writing down of logic required to compare hand values - not a benign step given the intricacies of poker hands
and the requirements to compare hand combinations (i.e. best 5 cards from 7 card stacks) - this took a while
5) Creation of hand evaluation function from scratch
6) Creation of text-version of the game, followed by extensive de-bugging
7) Learning how TkInter works and creating a separate file to test creating GUIs
8) Rewriting of text-version of the game to a GUI version, and incorporation of all relevant methods and functions into the main game class
9) Extensive cleaning up of the code to remove redundancies, refactor obscure names and make documentation more explicit
11) Modularization thanks to PyCharm to make code easier to review and separate configuration, hand evaluation, game objects from
the main game logic and GUI
12) Debugging and manually testing the game

# Credits --------------------------------------------------------------
All code was created from scratch, with the help of Stack Overflow to overcome some problems.
The card images are open source, and were converted from PNG to GIF using OS X Preview.
The cards were downloaded from opengameart.org (http://opengameart.org/sites/default/files/Playing%20Cards.zip)

Rules were taken from Wikipedia and poker hand rankings from various online sources.

Thanks to JM Portilla for creating a fantastic Python course which taught me most of what I needed to know in a very clear way 
(https://www.udemy.com/complete-python-bootcamp/)
Thanks to the creators of Jupyter notebook, which I used initially, and JetBrains, which I grew to love for their fantastic PyCharm
IDE, which has saved me countless hours of typing and manual refactoring.

Thanks to the creator of Casino Hold'Em, Stephen Au-Yeung.

# Contact ---------------------------------------------------------------
I would love to hear your feedback on the game if you use it or have suggestions, you can find me on the usual social media platforms.

I hope you enjoy learning and playing this game as much as I did creating it.




