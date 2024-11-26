import time
from typing import Any, List
import streamlit as st
from PIL import Image

from streamlit_server_state import server_state, server_state_lock
import random
from streamlit.runtime.scriptrunner.script_run_context import add_script_run_ctx
from streamlit_autorefresh import st_autorefresh

image_dimensions = (200, 200)

months = ["January", "February", "March", "April", "May", "June", "July",
          "August", "September", "October", "November", "December"]


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


fighters = []
def read_data() -> List:

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

            #Change the rarity from "Ultra" to "ul"
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
            img = col.lower() + rar.lower() + nam.lower().replace(" ", "").replace(":", "").replace("(", "").replace(")", "")  + ".png"

            fighters.append(Fighter(rar, nam, col, tags, ztags, img, epi, dbl))

read_data()

def get_fighter_by_name(name: str) -> Fighter:
    """
    Given the string representation of a fighter, return the fighter.

    Precondition: <name> is a valid string representation of a fighter
    """

    for fighter in fighters:
        if str(fighter) == name:
            return fighter

def create_fighter_image(fighter: Fighter):
    # Rewrite the name of the image file with removing all the useless stuff
    img =("images/" + fighter.color.lower() + fighter.rarity.lower() +
          fighter.name.lower().replace(" ", "")
          .replace(":", "").replace("(", "")
          .replace(")", "") + ".png")

    # Open and resize the image to the proper dimensions
    image = Image.open(img)
    new_image = image.resize(image_dimensions)

    colim = Image.open("images/" + fighter.color.lower() + ".png")
    newcol = colim.resize(image_dimensions)

    # Get the rarity picture
    temp = Image.open("images/" + fighter.rarity.lower() + ".png").resize(image_dimensions)

    final_im = Image.alpha_composite(new_image, temp)

    # Add the sparking image for LL's
    if fighter.rarity == "LL":
        # Open the sparking image
        temp = Image.open("images/sparking.png")
        # Apply the sparking image on the LL
        final_im = Image.alpha_composite(final_im,temp)

    final_im = Image.alpha_composite(final_im, newcol)
    return final_im


st.title("Guess Who Multiplayer Game")

# Add auto-refresh every second
add_script_run_ctx(st.session_state)
st_autorefresh(interval=1000, limit=None, key="auto_refresh")

# Initialize server state for rooms
with server_state_lock["rooms"]:
    if 'rooms' not in server_state:
        server_state.rooms = {}

# Function to initialize a room
def init_room(room_id):
    server_state.rooms[room_id] = {
        'players': {},  # Dictionary to hold player names and their scores
        'game_started': False,  # Flag to check if the game has started
        'character_images': [str(fighter) for fighter in fighters],  # List of character names
        'selected_characters': {},  # Dictionary to hold each player's selected character
        'turn': None,  # Whose turn it is to guess
        'guesses': {},  # Dictionary to hold guesses
        'chat': [],  # List to hold chat messages
        'last_guess_time': time.time(),
        'timer_start' : time.time()
    }

# Function to check and remove inactive rooms
def remove_inactive_rooms():
    current_time = time.time()
    with server_state_lock["rooms"]:
        inactive_rooms = []
        for room_id, room in server_state.rooms.items():
            # Check if no guess has been made for 120 seconds
            if current_time - room['last_guess_time'] > 120:
                inactive_rooms.append(room_id)

        for room_id in inactive_rooms:
            del server_state.rooms[room_id]
            if 'room_id' in st.session_state and st.session_state.room_id == room_id:
                del st.session_state.room_id
            st.warning(f"Room '{room_id}' has been closed due to inactivity or no players.")

# Periodically check for inactive rooms
remove_inactive_rooms()

# Room selection/creation
action = st.radio("Do you want to create a new room or join an existing one?", ("Create", "Join"))

if action == "Create":
    new_room = st.text_input("Enter a room name:")
    if st.button("Create Room"):
        with server_state_lock["rooms"]:
            if new_room not in server_state.rooms:
                init_room(new_room)
                st.session_state.room_id = new_room
                st.success(f"Room '{new_room}' created!")
            else:
                st.error("Room already exists. Choose a different name.")
else:
    existing_room = st.selectbox("Select a room to join:", list(server_state.rooms.keys()))
    if st.button("Join Room"):
        st.session_state.room_id = existing_room
        st.success(f"Joined room '{existing_room}'")

# Player name
player_name = st.text_input("Enter your name:")
if st.button("Join Game"):
    if 'room_id' in st.session_state:
        room_id = st.session_state.room_id
        with server_state_lock["rooms"]:
            if player_name and player_name not in server_state.rooms[room_id]['players']:
                if len(server_state.rooms[room_id]['players']) < 2:  # Check if the room has less than 2 players
                    server_state.rooms[room_id]['players'][player_name] = {'score': 0}
                    st.session_state.player_name = player_name
                    st.success(f"Player '{player_name}' joined the game!")
                else:
                    st.error("Room is full. Please join another room.")
            else:
                st.error("Name already taken or invalid.")

# Game Lobby
if 'room_id' in st.session_state and 'player_name' in st.session_state:
    room_id = st.session_state.room_id
    player_name = st.session_state.player_name
    room = server_state.rooms[room_id]

    st.subheader(f"Room: {room_id}")
    st.write("Players in the room:")
    for player in room['players']:
        st.write(player + ": " + str(room['players'][player]['score']) + " wins")

    # Game start condition
    if not room['game_started']:
        if st.button("Start Game") and player_name == list(room['players'].keys())[0] and len(room['players']) == 2:
            # Only the room creator can start the game if there are 2 players
            with server_state_lock["rooms"]:
                room['game_started'] = True
                room['turn'] = random.choice(list(room['players'].keys()))  # Randomly select who goes first
                st.success("Game started!")
        else:
            if len(room['players']) < 2:
                st.write("Waiting for another player to join.")
            else:
                st.write("Waiting for HOST to start the game.")

    # Character selection
    if room['game_started']:
        room['last_guess_time'] = time.time()
        if player_name not in room['selected_characters']:
            selected_character = st.selectbox("Select your character:", room['character_images'])
            if st.button("Submit Character"):
                room['last_guess_time'] = time.time()
                with server_state_lock["rooms"]:
                    room['selected_characters'][player_name] = get_fighter_by_name(selected_character)
                    st.success(f"{selected_character}' selected!")

        # Display selected character
        if player_name in room['selected_characters']:
            st.write(f"Your selected character: {str(room['selected_characters'][player_name])}")
            st.image(create_fighter_image(room['selected_characters'][player_name]))


            # Write down their characters info

            fighter = room['selected_characters'][player_name]
            character_info = st.expander("Character Information")
            character_info.write("Your fighters rarity is " + fighter.rarity)
            character_info.write("Your fighters color is " + fighter.color)

            if len(fighter.tags) == 0:
                character_info.write("Your fighter has no tags")
            else:
                for tag in fighter.tags:
                    character_info.write("Your fighter has tag " + tag)

            character_info.write("Your fighter is from " + fighter.epi)

            if fighter.dbl[3] == "-":
                character_info.write("Your fighter is a character claimed from an event")
            else:
                num = fighter.dbl[3:5]
                year = (int(num) + 5 )// 12 + 2018
                month = (int(num) + 5) % 12
                character_info.write("Your fighter came out in " + months[month] + " " + str(year))



            # Guessing process
            if player_name == room['turn']:
                guess = st.selectbox("Guess the opponent's character:", room['character_images'])

                if st.button("Submit Guess"):
                    with server_state_lock["rooms"]:
                        opponent = [p for p in room['players'] if p != player_name][0]
                        room['guesses'][player_name] = guess
                        room['last_guess_time'] = time.time()
                        room['timer_start'] = time.time()
                        if guess == str(room['selected_characters'][opponent]):
                            st.success("Correct! You win!")
                            room['players'][player_name]['score'] += 1
                            room['game_started'] = False  # End the game
                            room['selected_characters'] = {}
                        else:
                            st.error("Incorrect. Opponent's turn.")
                            room['turn'] = opponent
            else:
                st.write("The opponent is making their guess...")

        # Timer display
        current_time = time.time()
        time_remaining = 300 - (current_time - room['timer_start'])
        if time_remaining <= 0:
            st.warning("Time's up! The game has ended due to inactivity.")
            with server_state_lock["rooms"]:
                room['game_started'] = False
        else:
            minutes, seconds = divmod(time_remaining, 60)
            st.write(f"Time remaining: {int(minutes)}:{int(seconds):02d}")

    # Chat room
    st.subheader("Chat Room")
    chat_message = st.text_input("Enter your message:")
    if st.button("Send"):
        with server_state_lock["rooms"]:
            room['chat'].append(f"{player_name}: {chat_message}")

    st.write("Chat Messages:")
    for msg in room['chat']:
        st.write(msg)
