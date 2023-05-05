import numpy as np
import cv2
import requests
import tensorflow as tf
from tensorflow import keras
import tkinter as tk
from tkinter import *
from PIL import ImageTk, Image
from tkinter import filedialog
from tkinter.filedialog import askopenfile
import customtkinter as ctk

POKEMON_NAMES = [
    "Abra", "Aerodactyl", "Alakazam", "Arbok", "Arcanine", "Articuno",
    "Beedrill", "Bellsprout", "Blastoise", "Bulbasaur", "Butterfree",
    "Caterpie", "Chansey", "Charizard", "Charmander", "Charmeleon", "Clefable",
    "Clefairy", "Cloyster", "Cubone",
    "Dewgong", "Diglett", "Ditto", "Dodrio", "Doduo", "Dragonair", "Dragonite",
    "Dratini", "Drowzee", "Dugtrio",
    "Eevee", "Ekans", "Electabuzz", "Electrode", "Exeggcute", "Exeggutor",
    "Farfetchd", "Fearow", "Flareon", 
    "Gastly", "Gengar", "Geodude", "Gloom", "Golbat", "Goldeen", "Golduck",
    "Golem", "Graveler", "Grimer", "Growlithe", "Gyarados",
    "Haunter", "Hitmonchan", "Hitmonlee", "Horsea", "Hypno", 
    "Ivysaur",
    "Jigglypuff", "Jolteon", "Jynx",
    "Kabuto", "Kabutops", "Kadabra", "Kakuna", "Kangaskhan", "Kingler", "Koffing","Krabby",
    "Lapras", "Lickitung", 
    "Machamp", "Machoke", "Machop", "Magikarp", "Magmar", "Magnemite", "Magneton", "Mankey",
    "Marowak","Meowth", "Metapod", "Mew", "Mewtwo", "Moltres", "MrMime", "Muk",
    "Nidoking", "Nidoqueen", "Nidoran(Female)", "Nidoran(Male)", "Nidorina", "Nidorino", "Ninetales",
    "Oddish", "Omanyte", "Omastar", "Onix", 
    "Paras", "Parasect", "Persian", "Pidgeot", "Pidgeotto", "Pidgey", "Pikachu", "Pinsir", "Poliwag",
    "Poliwhirl","Poliwrath", "Ponyta", "Porygon", "Primeape", "Psyduck",
    "Raichu", "Rapidash", "Raticate", "Rattata", "Rhydon", "Rhyhorn",
    "Sandshrew", "Sandslash", "Scyther", "Seadra", "Seaking", "Seel", "Shellder", "Slowbro", "Slowpoke",
    "Snorlax", "Spearow", "Squirtle", "Starmie", "Staryu",
    "Tangela", "Tauros", "Tentacool", "Tentacruel",
    "Vaporeon", "Venomoth", "Venonat", "Venusaur", "Victreebel", "Vileplume", "Voltorb", "Vulpix",
    "Wartortle", "Weedle", "Weepinbell", "Weezing", "Wigglytuff",
    "Zapdos", "Zubat"    
]

# Load the model
trained_model = tf.keras.models.load_model('./pretrained_model_151_pokemon')

# Keep global filepath variable for uploading images
saved_img_filepath = "abra.jpg"

# Create global root window, left and right frames
root = ctk.CTk()
upload_img = None
left_frame = ctk.CTkFrame(root, width=200, height=400, fg_color='transparent')
right_frame = ctk.CTkFrame(root, width=650, height=400,  fg_color='transparent')
right_table_frame = ctk.CTkFrame(right_frame, fg_color="transparent")

# Function handles classification of the uploaded image and displaying the classified pokemon in the gui
#
# name_label is the label that will be updated with the predicted name
# height_label is the label that will be updated with the height of the pokemon
# weight_label is the label that will be updated with the weight of the pokemon
# type_label is the label that will be updated with the type of the pokemon
# area_label is the label that will be updated with the area of where to find the pokemon
def classify_img(name_label, height_label, weight_label, type_label, area_label):
    img_width = 256
    img_height = 256
    num_pixels = 255.0

    # Get the path of the uploaded image. Scale, re-size and reshape the image so it can be fed to the model
    img_filepath = saved_img_filepath
    new_img = cv2.imread(img_filepath)/ num_pixels
    new_img = cv2.resize(new_img, (img_width, img_height))
    new_img = np.reshape(new_img, [1, img_width, img_height, 3])

    # Have the model predict the pokemon label for the class
    predictions = trained_model.predict(new_img)

    # Get list of all predictions with their associated pokemon name. Order them by prediction value from the model.
    # Keep the top 5. Display the predicted pokemon label in the left frame and the top 5 predictions in the right frame.
    list_of_prediction_names_values = assign_pokemon_to_prediction(predictions)
    sorted_predictions = get_sorted_predictions(list_of_prediction_names_values)
    top_five_closest = sorted_predictions[:5]

    # Get the top prediction, lookup the stats for that pokemon in the api and display them in the left frame
    prediction = POKEMON_NAMES[np.argmax(predictions)]
    poke_api_name = get_poke_api_name(prediction)
    pokemon_stats = get_pokemon_stats(poke_api_name)

    # Update the pokemon info in the gui
    name_label.configure(text=prediction)
    height_label.configure(text=str(pokemon_stats["height"])+" m")
    weight_label.configure(text=str(pokemon_stats["weight"])+" kg")
    type_label.configure(text=pokemon_stats["poke_type"])
    area_label.configure(text=pokemon_stats["area"] if pokemon_stats["area"] != None else "Unknown")

    # Update the top five potential matches for the pokemon
    update_right_frame(top_five_closest)

# Function changes the name of the predicted pokemon if it is male or female nidoran or mr. mime 
# to the api version of the name so it can be correctly looked up in the api
#
# predicted_name is the string name label that was predicted for the pokemon image
def get_poke_api_name(predicted_name):
    poke_name = predicted_name

    if poke_name == "Nidoran(Female)":
        poke_name = "nidoran-f"
    elif poke_name == "Nidoran(Male)":
        poke_name = "nidoran-m"
    elif poke_name == "MrMime":
        poke_name = "mr-mime"
    return poke_name

# Function takes in a pokemon name and looksup the stats for that pokemon in the Pokemon API.
# Function returns a dict containing the height, weight, type and one area the Pokemon can be located
#
# pokemon_name is a string representing the name of the predicted pokemon
def get_pokemon_stats(pokemon_name):
    pokemon_stats = {}
    response = requests.get("https://pokeapi.co/api/v2/pokemon/"+pokemon_name.lower()+"/").json()
    areas = requests.get(response["location_area_encounters"]).json()
    poke_areas = filter_poke_areas(areas)

    pokemon_stats["height"] = response["height"]/10
    pokemon_stats["weight"] = response["weight"]/10
    pokemon_stats["poke_type"] = response["types"][0]["type"]["name"].capitalize()
    pokemon_stats["area"] = poke_areas[0] if len(poke_areas) > 0 else None

    return pokemon_stats

# Function loops through all the areas a pokemon can be found and filters out 
# any areas that are not found in the original red or blue versions of the game Pokemon. 
# It returns a list containing the names of the red and blue version areas that the pokemon can be found in.
#
# areas is a json string that stores all of the areas where a pokemon can be found
def filter_poke_areas(areas):
    generation_one_areas = []
    for area in areas:
        versions = area["version_details"] 
        for version in versions:
            version_name = version["version"]["name"]
            if version_name == "red" or version_name == "blue":
                generation_one_areas.append(area["location_area"]["name"])    
    return generation_one_areas

# Function updates the right frame of the window with the top predicted matches for the image
#
# top_five_closest is a list of 5 dicts, with each dict storing a name and prediction value
def update_right_frame(top_five_closest):

    # Remove old matches from the right frame
    for widget in right_table_frame.winfo_children():
        widget.destroy()
    
    # Display new list of top 5 matches in the right frame
    ctk.CTkLabel(right_table_frame, text="Rank", font=("Verdana", 18, "bold")).grid(row=1, column=0, padx=5, pady=5)
    ctk.CTkLabel(right_table_frame, text="Name", font=("Verdana", 18, "bold")).grid(row=1, column=1, padx=5, pady=5)
    ctk.CTkLabel(right_table_frame, text="Value", font=("Verdana", 18, "bold")).grid(row=1, column=2, padx=5, pady=5)
    ctk.CTkLabel(right_table_frame, text="1.", font=("Verdana", 18)).grid(row=2, column=0, padx=5, pady=5)
    ctk.CTkLabel(right_table_frame, text=top_five_closest[0]["name"], font=("Verdana", 18)).grid(row=2, column=1, padx=5, pady=5)
    ctk.CTkLabel(right_table_frame, text=str(top_five_closest[0]["value"]), font=("Verdana", 18)).grid(row=2, column=2, padx=5, pady=5)
    ctk.CTkLabel(right_table_frame, text="2.", font=("Verdana", 18)).grid(row=3, column=0, padx=5, pady=5)
    ctk.CTkLabel(right_table_frame, text=top_five_closest[1]["name"], font=("Verdana", 18)).grid(row=3, column=1, padx=5, pady=5)
    ctk.CTkLabel(right_table_frame, text=str(top_five_closest[1]["value"]), font=("Verdana", 18)).grid(row=3, column=2, padx=5, pady=5)
    ctk.CTkLabel(right_table_frame, text="3.", font=("Verdana", 18)).grid(row=4, column=0, padx=5, pady=5)
    ctk.CTkLabel(right_table_frame, text=top_five_closest[2]["name"], font=("Verdana", 18)).grid(row=4, column=1, padx=5, pady=5)
    ctk.CTkLabel(right_table_frame, text=str(top_five_closest[2]["value"]), font=("Verdana", 18)).grid(row=4, column=2, padx=5, pady=5)
    ctk.CTkLabel(right_table_frame, text="4.", font=("Verdana", 18)).grid(row=5, column=0, padx=5, pady=5)
    ctk.CTkLabel(right_table_frame, text=top_five_closest[3]["name"], font=("Verdana", 18)).grid(row=5, column=1, padx=5, pady=5)
    ctk.CTkLabel(right_table_frame, text=str(top_five_closest[3]["value"]), font=("Verdana", 18)).grid(row=5, column=2, padx=5, pady=5)
    ctk.CTkLabel(right_table_frame, text="5.", font=("Verdana", 18)).grid(row=6, column=0, padx=5, pady=5)
    ctk.CTkLabel(right_table_frame, text=top_five_closest[4]["name"], font=("Verdana", 18)).grid(row=6, column=1, padx=5, pady=5)
    ctk.CTkLabel(right_table_frame, text=str(top_five_closest[4]["value"]), font=("Verdana", 18)).grid(row=6, column=2, padx=5, pady=5)



# Function creates a list of dictionaries storing the pokemon name and their prediction score
#
# predictions is a list storing the predicted value for each Pokemon class
def assign_pokemon_to_prediction(predictions):
    names_predictions = []
    for i in range(0, len(predictions[0])):
        name_dict = {}
        name_dict["name"] = POKEMON_NAMES[i]
        name_dict["value"] = predictions[0][i]
        names_predictions.append(name_dict)
    return names_predictions

# Function sorts the list of dicts by their predicted values in descending order
#
# names_values is a list of dicts, with each dict containing a Pokemon name and a prediction value
def get_sorted_predictions(names_values):
    sorted_values = sorted(names_values, key=lambda d: d['value'], reverse=True)
    return sorted_values

# Function handles uploading and displaying image to pokedex window
#
# left_frame is the frame that the image will be displayed in
def upload_file(left_frame):
    global img
    global saved_img_filepath

    # Get the image and save the filepath. Only allow upload of jpg files
    f_types = [('Jpg Files', '*.jpg')]
    filename = filedialog.askopenfilename(filetypes=f_types)

    # Store the new image filepath if it has a valid path
    saved_img_filepath = filename if len(filename) > 0 else saved_img_filepath

    # Delete old image
    for label in left_frame.grid_slaves():
        if int(label.grid_info()["row"]) == 1:
            label.grid_forget()

    # Open the image, resize it and display it in the left frame
    img = Image.open(saved_img_filepath)
    img_resized = img.resize((150,150))
    img = ImageTk.PhotoImage(img_resized)
    b2 =tk.Button(left_frame,image=img)
    b2.grid(row=1, column=0, padx=5, pady=5)

# Function creates the buttons and widgets for the window and then runs the window
def create_window():

    # Add title, max window size and background colour to the GUI
    root.title("Neural Network Pokédex")  
    root.maxsize(900, 600)  
    root.config(bg="red")  

    # Place left and right frame in window
    left_frame.grid(row=0, column=0, padx=10, pady=5)
    right_frame.grid(row=0, column=1, padx=10, pady=5)

    # Create titles for left and right frames
    ctk.CTkLabel(left_frame, text="Pokémon Image", font=("Verdana", 20, "bold")).grid(row=0, column=0, padx=5, pady=5)
    ctk.CTkLabel(right_frame, text="Top 5 Matches", font=("Verdana", 20, "bold"), justify=CENTER).grid(row=0, padx=5, pady=5)

    # Display image to be classified in left frame
    image = Image.open(saved_img_filepath)
    image = image.resize((150,150))
    image = ImageTk.PhotoImage(image)
    original_image =  image
    Label(left_frame, image=original_image).grid(row=1, column=0, padx=5, pady=5)

    # Create info bar frame
    info_bar = ctk.CTkFrame(left_frame, width=180, height=185)
    info_bar.grid(row=2, column=0, padx=5, pady=5)

    # Create labels that will display the pokemon name, height, weight, type, and area
    name_title_label = ctk.CTkLabel(info_bar, text="Name: ", font=("Verdana", 18, "bold"), anchor='w', justify=LEFT)
    height_title_label = ctk.CTkLabel(info_bar, text="Height: ", font=("Verdana", 18, "bold"), anchor='w',  justify=LEFT)
    weight_title_label = ctk.CTkLabel(info_bar, text="Weight: ", font=("Verdana", 18, "bold"), anchor='w',  justify=LEFT)
    type_title_label = ctk.CTkLabel(info_bar, text="Type: ", font=("Verdana", 18, "bold"), anchor='w',  justify=LEFT)
    area_title_label = ctk.CTkLabel(info_bar, text="Area: ", font=("Verdana", 18, "bold"), anchor='w',  justify=LEFT)
    
    name_label = ctk.CTkLabel(info_bar, text="Unknown", font=("Verdana", 18), anchor='w', justify=LEFT)
    height_label = ctk.CTkLabel(info_bar, text="Unknown", font=("Verdana", 18), anchor='w',  justify=LEFT)
    weight_label = ctk.CTkLabel(info_bar, text="Unknown", font=("Verdana", 18), anchor='w',  justify=LEFT)
    type_label = ctk.CTkLabel(info_bar, text="Unknown", font=("Verdana", 18), anchor='w',  justify=LEFT)
    area_label = ctk.CTkLabel(info_bar, text="Unknown", font=("Verdana", 18), anchor='w',  justify=LEFT)

    # Add labels for name, height, weight, type and area to the window
    name_title_label.grid(row=1, column=0, padx=5, pady=5)
    name_label.grid(row=1, column=1, padx=5, pady=5)

    height_title_label.grid(row=2, column=0, padx=5, pady=5)
    height_label.grid(row=2, column=1, padx=5, pady=5)

    weight_title_label.grid(row=3, column=0, padx=5, pady=5)
    weight_label.grid(row=3, column=1, padx=5, pady=5)
    
    type_title_label.grid(row=4, column=0, padx=5, pady=5)
    type_label.grid(row=4, column=1, padx=5, pady=5)
    
    area_title_label.grid(row=5, column=0, padx=5, pady=5)
    area_label.grid(row=5, column=1, padx=5, pady=5)

    # Create next closest 5 matches labels
    right_table_frame.grid(row=1, column= 0)
    ctk.CTkLabel(right_table_frame, text="Rank", font=("Verdana", 18, "bold")).grid(row=1, column=0, padx=5, pady=5)
    ctk.CTkLabel(right_table_frame, text="Name", font=("Verdana", 18, "bold")).grid(row=1, column=1, padx=5, pady=5)
    ctk.CTkLabel(right_table_frame, text="Value", font=("Verdana", 18, "bold")).grid(row=1, column=2, padx=5, pady=5)
    ctk.CTkLabel(right_table_frame, text="1.", font=("Verdana", 18)).grid(row=2, column=0, padx=5, pady=5)
    ctk.CTkLabel(right_table_frame, text="Unknown", font=("Verdana", 18)).grid(row=2, column=1, padx=5, pady=5)
    ctk.CTkLabel(right_table_frame, text="0", font=("Verdana", 18)).grid(row=2, column=2, padx=5, pady=5)
    ctk.CTkLabel(right_table_frame, text="2.", font=("Verdana", 18)).grid(row=3, column=0, padx=5, pady=5)
    ctk.CTkLabel(right_table_frame, text="Unknown", font=("Verdana", 18)).grid(row=3, column=1, padx=5, pady=5)
    ctk.CTkLabel(right_table_frame, text="0", font=("Verdana", 18)).grid(row=3, column=2, padx=5, pady=5)
    ctk.CTkLabel(right_table_frame, text="3.", font=("Verdana", 18)).grid(row=4, column=0, padx=5, pady=5)
    ctk.CTkLabel(right_table_frame, text="Unknown", font=("Verdana", 18)).grid(row=4, column=1, padx=5, pady=5)
    ctk.CTkLabel(right_table_frame, text="0", font=("Verdana", 18)).grid(row=4, column=2, padx=5, pady=5)
    ctk.CTkLabel(right_table_frame, text="4.", font=("Verdana", 18)).grid(row=5, column=0, padx=5, pady=5)
    ctk.CTkLabel(right_table_frame, text="Unknown", font=("Verdana", 18)).grid(row=5, column=1, padx=5, pady=5)
    ctk.CTkLabel(right_table_frame, text="0", font=("Verdana", 18)).grid(row=5, column=2, padx=5, pady=5)
    ctk.CTkLabel(right_table_frame, text="5.", font=("Verdana", 18)).grid(row=6, column=0, padx=5, pady=5)
    ctk.CTkLabel(right_table_frame, text="Unknown", font=("Verdana", 18)).grid(row=6, column=1, padx=5, pady=5)
    ctk.CTkLabel(right_table_frame, text="0", font=("Verdana", 18)).grid(row=6, column=2, padx=5, pady=5)
    
    # Add buttons for uploading and classifying images
    ctk.CTkButton(info_bar, text='Upload Image',command = lambda:upload_file(left_frame)).grid(row=0,column=0, padx=5, pady=3, ipadx=10) 
    ctk.CTkButton(info_bar, text="Classify", command = lambda:classify_img(name_label, height_label, weight_label, type_label, area_label)).grid(row=0, column=1, padx=5, pady=3, ipadx=10)
    
    # Run the window
    root.mainloop()

create_window()