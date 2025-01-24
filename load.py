import json
import os
from spellchecker import SpellChecker
from classes import Recipe, Menu

spell = SpellChecker(language='fr')
spell.distance = 1

def load_all_recipe_files(location='./json/'):
    all_recipes_list = []
    for _root, _dirs, files in os.walk(location):
        for name in files:
            with open(location + name, 'r', encoding='utf-16') as recipe_file:
                recipe_dict = json.load(recipe_file)
                # check_spell(recipe_dict['ingredients'])
                all_recipes_list.append(Recipe(recipe_dict['ref'], recipe_dict['name'], recipe_dict['ingredients']))
    return all_recipes_list

def check_spell(ingredient: dict):
    for text, num in ingredient.items():
        print(spell.unknown(text.split(sep=' ')))
        for u in spell.unknown(text.split(sep=' ')):
            print(spell.candidates(u))
