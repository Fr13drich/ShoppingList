import configparser
import json
import os
import logging
from classes import Recipe, Ingredient
from spellchecker import SpellChecker

config = configparser.ConfigParser()
config.read('./config.cfg')

logger = logging.getLogger(__name__)



spell = SpellChecker(language='fr')
spell.distance = 1

def load_all_recipe_files(location=config['DEFAULT']['READER_OUTPUT_DIR']):
    all_recipes_list = []
    for _root, _dirs, files in os.walk(location):
        for name in files:
            with open(location + name, 'r', encoding='utf-16') as recipe_file:
                recipe_dict = json.load(recipe_file)
                # check_spell(recipe_dict['ingredients'])
                logger.info(recipe_dict['ref'])
                all_recipes_list.append(\
                        Recipe(ref=recipe_dict['ref'],\
                               name=recipe_dict['name'],\
                               ingredients_bill=Recipe.parse_ingredients_bill_dict(\
                                    ingredients_bill_dict=recipe_dict['ingredients'],\
                                    recipe_ref=recipe_dict['ref'])))
    return all_recipes_list

def load_all_ingredient_files(location=config['DEFAULT']['INGREDIENTS_DIR']):
    for _root, _dirs, files in os.walk(location):
        for name in files:
            with open(location + name, 'r', encoding='utf-16') as ingredient_file:
                ingredient = json.load(ingredient_file)
                Ingredient.add(name=ingredient['name'], lemma=ingredient['lemma'],\
                    wiki_ref=ingredient['wiki_ref'], category=ingredient['category'],\
                    other_recipe_ref=ingredient['other_recipe_ref'])

# def write_ingredient_file(ingredient: Ingredient):
#     name = ingredient.wiki_ref if ingredient.wiki_ref else ingredient.name
#     filename = name + '.json'
#     with open('./ingredient_files/' + filename, 'w', encoding='utf-16') as outfile:
#         json.dump(ingredient.serialize(), outfile, indent=2, ensure_ascii=False)

def check_spell(ingredient: dict):
    for text, _num in ingredient.items():
        print(spell.unknown(text.split(sep=' ')))
        for u in spell.unknown(text.split(sep=' ')):
            print(spell.candidates(u))
