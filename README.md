# Neural Network Pokédex

## Description

A small python program that utilizes a trained CNN model to classify jpeg images of any of the [original 151 Generation I Pokémon](https://www.serebii.net/pokemon/gen1pokemon.shtml). For any predicted Pokémon, the program displays its name, height, weight, type and one of the areas from the original Blue and Red games that it can be found in.

## Classification Demonstration

![pokedex_classify](https://user-images.githubusercontent.com/59716448/236895647-fc27340f-d575-4281-b8c2-f46bd6d88774.gif)

## Running and Using the Program

**To run the program use the following command:**<br />
python pokedex.py <br /><br />
Use the Upload Image button in the window to select the jpeg image of the Pokémon you want to classify.<br /><br />
Press the Classify button to have the program predict a class label for the image and display the top 5 matches on the right side of the window.<br /><br />

## About the CNN Model Used

The program utilizes a pretrained VGG19 CNN model. Building off what the model has previously learned, it was subjected to further training for this particular classification task, using 188,000 Pokémon images. <br /><br />
The trained model had an accuracy score of 0.9843 and a validation loss of 0.2404 on its test set.<br /><br />
To see the steps involved in the model's training, please view the pokemonnetwork.ipynb notebook included in this repository.  
