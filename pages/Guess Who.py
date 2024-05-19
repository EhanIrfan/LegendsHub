import streamlit as st
import streamlit.components.v1 as components

source_code = '<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-1269390288736567" crossorigin="anonymous"></script>'
print(source_code)
components.html(source_code, height=600)

import random
from typing import Any


class Fighter:
    """
    A class for a fighter

    Attributes:
        Rarity: The fighters rarity
        Name: The fighters name
        Color: The fighters color
        Tags: The fighters tags
        Z-Tags: The tags the fighter supports with their z-ability
        IMG: The fighters image
    """

    rarity: str
    name: str
    color: str
    tags: list
    ztags: list
    img: Any
    epi: str
    dbl: str

    def __init__(self, rarity: str, name: str, color: str, tags: list,
                 ztags: list, img: Any, epi: str, dbl: str):
        self.rarity = rarity
        self.name = name
        self.color = color
        self.tags = tags.copy()
        self.ztags = ztags.copy()
        self.img = img
        self.epi = epi
        self.dbl = dbl

    def __str__(self):
        hold = self.name.split(".")
        rar = self.rarity
        if rar == "Ul":
            rar = "Ultra"
        elif rar == "LL":
            rar = "Legends Limited"

        return self.color + " " + rar + " " + hold[0] + " " + self.dbl

    def __eq__(self, other):
        return str(self) == str(other)


################################
######### STORE DATA ###########
################################
fighters = []
with open("data.csv") as file:
    # Read header
    file.readline()

    for line in file:
        dat = line.split(",")

        # Reset values
        tags = []
        ztags = []

        # Store all the data in the file
        rar = dat[0]

        # Change the rarity from "Ultra" to "ul"
        if rar == "Ultra":
            rar = "Ul"

        nam = dat[1]
        col = dat[2]
        epi = dat[5]
        dbl = "DBL" + dat[6]

        # Split and hold the tags
        hold1 = dat[3].split(".")
        hold3 = dat[4].split(".")

        for tag in hold1:
            tags.append(tag)

        for ztag in hold3:
            ztags.append(ztag)

        # Rewrite the name of the image file with removing all the useless stuff
        img = col.lower() + rar.lower() + nam.lower().replace(" ", "").replace(":", "").replace("(", "").replace(")", "") + ".png"

        fighters.append(Fighter(rar, nam, col, tags, ztags, img, epi, dbl))


months = ["January", "February", "March", "April", "May", "June", "July",
          "August", "September", "October", "November", "December"]
char_rar = ["Hero", "Extreme", "Sparking", "LL", "Ul"]

# Initialize session state
if "begin" not in st.session_state:
    st.session_state.begin = False
if "guesses" not in st.session_state:
    st.session_state.guesses = 0
if "selected_char" not in st.session_state:
    st.session_state.selected_char = None
if "info_to_give" not in st.session_state:
    st.session_state.info_to_give = []
if "char_rar_check" not in st.session_state:
    st.session_state.char_rar_check = char_rar.copy()

# Create the multiselect for the user's choice of rarities
container4 = st.container()
togall4 = st.checkbox("Toggle All", True, key=4)

if togall4:
    st.session_state.char_rar_check = container4.multiselect("Select the rarities that you want"
                                                             " to have a chance to guess",
                                                             char_rar, char_rar,
                                                             placeholder="Select character "
                                                                         "rarity")
else:
    st.session_state.char_rar_check = container4.multiselect("Select the rarities that you want"
                                                             " to have a chance to guess!",
                                                             char_rar,
                                                             placeholder="Select character "
                                                                         "rarity")

selected_rar = st.session_state.char_rar_check.copy()

start_game = st.button("Click to start the game")
if start_game:
    st.session_state.begin = True
    st.session_state.guesses = 0
    num = random.randint(0, len(fighters) - 1)
    st.session_state.selected_char = fighters[num]
    while st.session_state.selected_char.rarity not in selected_rar:
        num = random.randint(0, len(fighters) - 1)
        st.session_state.selected_char = fighters[num]

    st.session_state.info_to_give = []
    st.session_state.info_to_give.append("The fighter's rarity is " + st.session_state.selected_char.rarity)

    if len(st.session_state.selected_char.tags) == 0:
        st.session_state.info_to_give.append("The fighter has no tags")
    for tag in st.session_state.selected_char.tags:
        st.session_state.info_to_give.append("The fighter has tag " + tag)
    st.session_state.info_to_give.append("The fighter is from " + st.session_state.selected_char.epi)

    if st.session_state.selected_char.dbl[3] == "-":
        st.session_state.info_to_give.append("The fighter is a character claimed from an event")
    else:
        num = st.session_state.selected_char.dbl[3:5]
        year = int(num) // 12 + 2018
        month = int(num) % 12
        st.session_state.info_to_give.append("This character came out in " + months[month] + " " + str(year))

    st.session_state.info_to_give.append("This character is a " + st.session_state.selected_char.color + " character")

    random.shuffle(st.session_state.info_to_give)

    st.session_state.info_to_give.append("There is no more info to give.")


if st.session_state.begin:
    fighter_nams = [str(fighter) for fighter in fighters]

    guessed_char = st.selectbox("Select your character", fighter_nams)

    submit = st.button("Submit Guess")

    if submit:
        if guessed_char == str(st.session_state.selected_char):
            st.session_state.begin = False
            st.image("images/" + st.session_state.selected_char.img)
            st.write("That is correct")
            st.write("That took " + str(st.session_state.guesses + 1) + " guesses")
        else:
            st.session_state.guesses += 1
            st.write("That is incorrect")

    # Display all the information given so far as a list
    for i in range(st.session_state.guesses + 1):
        if i < len(st.session_state.info_to_give):
            st.write(st.session_state.info_to_give[i])

# Add the "Give Up" button
give_up = False
if st.session_state.begin:
    give_up = st.button("Give Up")

if give_up:
    st.session_state.begin = False
    st.session_state.guesses = 0
    hold = st.session_state.selected_char.name + " - " + st.session_state.selected_char.dbl
    st.image(st.session_state.selected_char.img)
    st.session_state.selected_char = None
    st.session_state.info_to_give = []
    st.session_state.char_rar_check = char_rar.copy()
    st.write("You gave up. The fighter was " + hold )

