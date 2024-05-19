import streamlit as st
import streamlit.components.v1 as components

HtmlFile = open("test.html", 'r', encoding='utf-8')
source_code = HtmlFile.read()
print(source_code)
components.html(source_code, height=600)

from typing import Optional


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

        return self.color + " " + rar + " " + hold[0] + " (" + self.dbl + ")"


    def __eq__(self, other):
        return str(self) == str(other)

import streamlit as st
import random
from PIL import Image


# Title of page and size
st.set_page_config(page_title="Legends Randomizer", layout="wide")


info = st.expander("INFO")
info.write("Just like the game, if no tags are selected, they are all selected."
           " The characters you receive will contain atleast one of the chosen"
           " character tags and be in one of the chosen episodes. Similarly, "
           "they will be one of the rarities and one of the colors.")
info.write(" With "
           "guaranteed character, you can choose a character that you want to"
           " guarantee to be on your team. With advanced mode, the "
           "randomization will try to build a somewhat capable team of a "
           "random tag.")
info.write("If advanced mode is active, only the first character "
           "of guaranteed select will be used and the team will be built "
           "around a random tag of theirs, if possible.")
info.write("Use the unwanted fighter code to save your settings for which "
           "fighters you don't want on your team by copying and pasting the "
           "code when you need to.")


cred_url = "https://legends.dbz.space/characters/"
st.write("Image Source: [link](%s)" % cred_url)

# Dimensions of fighter images
image_dimensions = (200, 200)

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



def compare_data(l1: list, l2: list) -> bool:
    """
    Return true iff l1 and l2 share atleast one element
    """

    small_list = l1.copy()
    big_list = l2.copy()
    if l1 > l2:
        small_list = l2.copy()
        big_list = l1.copy()

    for elem in small_list:
        if elem in big_list:
            return True

    return False



def get_fighter_by_name(name: str) -> Fighter:
    """
    Given the string representation of a fighter, return the fighter.

    Precondition: <name> is a valid string representation of a fighter
    """

    for fighter in fighters:
        if str(fighter) == name:
            return fighter


def get_fighter_index(fighter: Fighter) -> int:
    """
    Given a fighter, return their position in the dataset (as an index)

    Precondition: <fighter> is in the dataset
    """

    count = 0

    for f in fighters:
        if fighter == f:
            return count
        count += 1

def sort_tags(fighters: list, tags: list, rarites: list, colors: list, epi: list) -> list:
    """
    Return a list of fighters that contain atleast one of the <tags>
    and are one of the chosen <rarites>, and are in one of the chosen
    <epi>'s
    """

    big_list = []
    for fighter in fighters:

        if (compare_data(fighter.tags, tags) and
                fighter.rarity in rarites and fighter.color in colors and
                fighter.epi in epi):
            big_list.append(fighter)

    return big_list


def get_strong_fighters(tag: str, f: Optional[Fighter]) -> list:
    """Given a <tag> that is either a character tag or episode, return a list
    of 3 ll characters or above. If there are fewer than 3 ll characters or
    above, include sparkings. If there are still too few sparkings,
    include all rarites

    Precondition: <tag> is either a relevant episode or character tag defined
    in <char_epi> or <char_tags>
    """

    big_list = []
    tags = char_tags
    epi = char_epi

    if tag in char_epi:
        epi = [tag]
    else:
        tags = [tag]

    relevant_fighters = sort_tags(wanted_fighters,tags, char_rar, char_col, epi)

    # Shuffle the list
    random.shuffle(relevant_fighters)

    if f in relevant_fighters:
        relevant_fighters.remove(f)

    # First look for Ul or LL units
    for fighter in relevant_fighters:
        if fighter.rarity.lower() == "ul" or fighter.rarity.lower() == "ll":
            big_list.append(fighter)
            relevant_fighters.remove(fighter)

        # Return if all needed characters were found
        if len(big_list) == 3:
            return big_list

    # Next, look for sparkings
    for fighter in relevant_fighters:
        if fighter.rarity.lower() == "sparking":
            big_list.append(fighter)
            relevant_fighters.remove(fighter)

        # Return if all needed characters were found
        if len(big_list) == 3:
            return big_list

    # Finally, just fill up the list if nothing else
    for fighter in relevant_fighters:
        big_list.append(fighter)

        if len(big_list) == 3:
            return big_list


    # Just add random characters if they got this far which they really shouldnt

    hold = fighters.copy()

    random.shuffle(hold)

    for fighter in hold:
        big_list.append(fighter)

        # Break out when length is 3
        if len(big_list) == 3:
            return big_list


def get_support_fighters(tag: str, selected: list) -> list:
    """Return a list of 3 fighters that have <tag> in the fighters
    <ztags> attribute. The fighters in <selected> will not be selected

    <tag> is either an episode or character tag
    """

    big_list = []

    # Shuffle the fighters
    rand_fighters = wanted_fighters.copy()
    random.shuffle(rand_fighters)
    for fighter in rand_fighters:
        if tag in fighter.ztags and fighter not in selected:
            big_list.append(fighter)
            rand_fighters.remove(fighter)

        # Exit when three fighters have been found
        if len(big_list) == 3:
            return big_list

    # There are not three fighters, so get the color of the second fighter
    # (since the first fighter will be the leader)

    col = selected[1].color

    for fighter in rand_fighters:
        if col in fighter.ztags:
            big_list.append(fighter)

        # Exit when three fighters have been found
        if len(big_list) == 3:
            return big_list


st.header("Randomization Time!")

# Show the most recent character (show how updated site is)
st.write("MOST RECENT CHARACTER: " + str(fighters[-1]))






char_tags = ["Saiyan", "Hybrid Saiyan", "Super Saiyan", "Super Saiyan 2",
             "Super Saiyan 3", "Super Saiyan 4", "Super Saiyan God",
             "Super Saiyan God SS", "Super Saiyan Rose", "Namekian",
             "Android", "Shadow Dragon", "God of Destruction", "Angel",
             "Kids", "Girls", "Regeneration", "Powerful Opponent",
             "Transforming Warrior", "Lineage of Evil", "Minion", "Twins",
             "Otherworld Warrior", "Fusion Warrior", "God Ki", "Son Family",
             "Vegeta Clan", "Super Warrior", "Frieza Force", "Ginyu Force",
             "Team Bardock", "Hera Clan", "Future", "GT", "Merging",
             "Absorption", "Fusion", "Potara", "Rival Universe",
             "Universe 2", "Universe 4", "Universe 6", "Universe 9",
             "Universe 11", "Universe Rep", "DB", "Event Exclusive",
             "Legends Road", "Game Originals"]

char_epi = ["Dragon Ball Saga", "Saiyan Saga (Z)", "Frieza Saga (Z)",
            "Android Saga (Z)", "Cell Saga (Z)", "Majin Buu Saga (Z)",
            "Black Star Dragon Ball Saga (GT)", "Super Baby Saga (GT)",
            "Super #17 Saga (GT)", "Shadow Dragon Saga (GT)",
            "God of Destruction Beerus Saga (S)",
            "Frieza Resurrected Saga (S)",
            "God of Destruction Champa Saga (S)", "Future Trunks Saga (S)",
            "Universe Survival Saga (S)", "Movies",
            "Anime Originals Saga", "DRAGON BALL FighterZ",
            "Dragon Ball Z: Kakarot"]

char_col = ["Red", "Yellow", "Purple", "Green", "Blue"]

char_rar = ["Hero", "Extreme", "Sparking", "LL", "Ul"]
# Create lists to store what the selected tags are
selected_tags = []
selected_rar = []
selected_col = []

container = st.container()
togall = st.checkbox("Toggle All", True, key=1)

if togall:
    char_tags_check = container.multiselect("Select Tags for Randomization!",
                                            char_tags, char_tags,
                                            placeholder="Select Character Tags")
else:
    char_tags_check = container.multiselect("Select Tags for Randomization!",
                                            char_tags,
                                            placeholder="Select Character Tags")

selected_tags.extend(char_tags_check)

st.write("")

container2 = st.container()
togall2 = st.checkbox("Toggle All", True, key=2)

if togall2:
    char_epi_check = container2.multiselect("Select Episode for Randomization!",
                                            char_epi, char_epi,
                                            placeholder="Select Character Episode")
else:
    char_epi_check = container2.multiselect("Select Episode for Randomization!",
                                            char_epi,
                                            placeholder="Select Character Episode")
selected_epi = char_epi_check.copy()

st.write("")

container3 = st.container()
togall3 = st.checkbox("Toggle All", True, key=3)

if togall3:
    char_col_check = container3.multiselect("Select Color for Randomization!",
                                            char_col, char_col,
                                            placeholder="Select Character Color")
else:
    char_col_check = container3.multiselect("Select Color for Randomization!",
                                            char_col,
                                            placeholder="Select Character Color")

selected_col = char_col_check.copy()


# Create the multiselect for the users choice of rarites
container4 = st.container()
togall4 = st.checkbox("Toggle All", True, key=4)

if togall4:
    char_rar_check = container4.multiselect("Select the rarities that you want"
                                            " to have a chance to get!",
                                            char_rar, char_rar,
                                            placeholder="Select character "
                                                        "rarity")
else:
    char_rar_check = container4.multiselect("Select the rarities that you want"
                                            " to have a chance to get!",
                                            char_rar,
                                            placeholder="Select character "
                                                        "rarity")

selected_rar = char_rar_check.copy()


### Guaranteed Character Select ###

selected_chars = []
selected_fighters = []

fighter_nams = []
# Display the choices of guaranteed fighters

for fighter in fighters:
    fighter_nams.append(str(fighter))

container5 = st.container()
selected_chars_check = container5.multiselect("Select the characters that you "
                                              "want to guarantee are on your "
                                              "team!", fighter_nams, placeholder="Select Character(s)")

# Store the names of all the selected fighters
selected_chars.extend(selected_chars_check)

for name in selected_chars:
    selected_fighters.append(get_fighter_by_name(name))

# Truncate the guaranteed fighters to ensure it is not larger than length 6
selected_fighters = selected_fighters[0:6]



### OMIT CHARACTER SELECT ###
container6 = st.container()
omitted_chars_check = container6.multiselect("Select the characters that you "
                                             "DON'T want on your team!",
                                             fighter_nams,
                                             placeholder="Select Character(s)")

omitted_chars = []
omitted_chars.extend(omitted_chars_check)
wanted_fighters = fighters.copy()


omit = ""
for fighter in fighters:
    if fighter in omitted_chars:
        omit += "0"
    else:
        omit += "1"


enter_code = st.toggle("Show Unwanted Fighter Code (For Copying and Pasting)")

if enter_code:
    omit = st.text_input("Enter Code Here", omit)

# Remove the omitted characters from the randomization
if len(omit) == len(fighters) and (omit.count("0") + omit.count("1") == len(fighters)):
    for i, char in enumerate(omit):
        if char == "0":
            wanted_fighters.pop(i - (len(fighters) - len(wanted_fighters)))






##### ADVANCED MODE #####

adv_mode = st.toggle("Advanced Mode")
if adv_mode:
    epis_only = st.toggle("Episodes Only (NOTE: This is "
                          "irrelevant when guaranteed character is used)")
    tags_only = st.toggle("Tags Only (NOTE: This is "
                          "irrelevant when guaranteed character is used)")

# Make the Button for a random fighter
randfighter = st.button("Click for a random team")



############################
#    RANDOMIZE FIGHTERS    #
############################


if randfighter:

    # Check if user selected no tags. If they did, select all tags
    if not selected_tags:
        selected_tags.extend(char_tags)

    # Check if the user selected no rarities. If they did, select all rarites
    if not selected_rar:
        selected_rar.extend(char_rar)

    # Check if the user selected no episodes. If they did, select all episodes
    if not selected_epi:
        selected_epi.extend(char_epi)

    # Check if user selected no colors. If they did, select all colors
    if not selected_col:
        selected_col.extend(char_col)

    if adv_mode:

        # If guaranteed fighter is not used
        if len(selected_fighters) == 0:
            # Put episodes and tags into one list
            relevant_info = []

            if not tags_only:
                relevant_info.extend(selected_epi)
            if not epis_only:
                relevant_info.extend(selected_tags)

            if epis_only and tags_only:
                relevant_info.extend(selected_epi)
                relevant_info.extend(selected_tags)

            rand_num = random.randint(0, len(relevant_info) - 1)
            tag = relevant_info[rand_num]

        # If guaranteed fighter is used
        else:
            # Only take the first fighter (if the user selected multiple guaranteed
            # fighters)
            selected_fighters = selected_fighters[:1]

            # Choose a random tag that the character has (or their episode)
            possible_tags = selected_fighters[0].tags.copy()
            possible_tags.extend([selected_fighters[0].epi])

            rand_num = random.randint(0, len(possible_tags) - 1)

            tag = possible_tags[rand_num]

        st.markdown("The selected tag is: " + tag)

        if selected_fighters == []:
            temp = get_strong_fighters(tag, None)
        else:
            temp = get_strong_fighters(tag, selected_fighters[0])
        # If the user did not select a fighter beforehand, take all three
        # fighters

        if len(selected_fighters) == 0:
            selected_fighters = temp
        # Otherwise, just take the first two fighters
        else:
            selected_fighters.extend(temp[0:2])

        selected_fighters.extend(get_support_fighters(tag, selected_fighters))



    else:
        # Create a list of fighters that follow the rules
        temp_fighters = sort_tags(wanted_fighters, selected_tags, selected_rar,
                                  selected_col, selected_epi)

        # Check for duplicates between temp_fighters and guaranteed_fighters
        for fighter in selected_fighters:
            if fighter in temp_fighters:
                temp_fighters.remove(fighter)

        # The number of fighters needed to get via randomization
        req_rand = 6 - len(selected_fighters)

        if len(temp_fighters) < req_rand:
            st.write("A Valid team can not be constructed with these tags.")
        else:

            # Randomly shuffle the list and take the first <req_rand> fighters
            random.shuffle(temp_fighters)

            # List for the fighters image
            hold2 = []

            for i in range(req_rand):
                # Store the fighters in a list
                selected_fighters.append(temp_fighters[i])


    # Creating the images of the fighters
    hold2 = []
    for fighter in selected_fighters:
        # Rewrite the name of the image file with removing all the useless stuff
        img = "images/" + (fighter.color.lower() + fighter.rarity.lower() +
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
            temp = Image.open("sparking.png")
            # Apply the sparking image on the LL
            final_im = Image.alpha_composite(final_im,temp)

        final_im = Image.alpha_composite(final_im, newcol)
        # Store the final image in a list
        hold2.append(final_im)


    # Print the images and names of the chosen fighters
    st.image(hold2[0:3])

    st.image(hold2[3:])

    for fighter in selected_fighters:
        st.write(str(fighter))
