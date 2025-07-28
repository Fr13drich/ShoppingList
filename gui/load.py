"""Functions used by the gui"""
import configparser
import json
import os
import logging
from recipe import Recipe, IngredientEntry
from ingredient import Ingredient
from reader import parse_ingredients_bill_dict
# from ingredient import Ingredient

config = configparser.ConfigParser()
config.read('./config.cfg')
logger = logging.getLogger(__name__)

def load_all_recipe_files(location=config['DEFAULT']['RECIPES_DIR']):
    """Create Recipe objects from json files."""
    all_recipes_list = []
    for _root, _dirs, files in os.walk(location):
        for name in files:
            with open(os.path.join(location, name), 'r', encoding='utf-8') as recipe_file:
                recipe_dict = json.load(recipe_file)
                logger.info(recipe_dict['ref'])
                all_recipes_list.append(
                        Recipe(ref=recipe_dict['ref'],
                               name=recipe_dict['name'],
                               ingredients_bill=[IngredientEntry(amount=entry['amount'],
                                                                 unit=entry['unit'],
                                                                 jxt=entry['jxt'],
                                                                 ingredient=Ingredient(name=entry['ingredient'],
                                                                                       lemma=entry.get('lemma', ''),
                                                                                       category=entry.get('category', ''),
                                                                                       synonymes=entry.get('synonymes', []),
                                                                                       recipe_refs=recipe_dict['ref']))
                                                for entry in recipe_dict['ingredients_bill']]
                        ))
                            #    parse_ingredients_bill_dict(
                            #        ingredients_bill_dict=recipe_dict['ingredients_bill'],
                            #        recipe_ref=recipe_dict['ref'])))
    return all_recipes_list

# def load_all_ingredient_files(location=config['DEFAULT']['INGREDIENTS_DIR']):
#     """not used anymore"""
#     for _root, _dirs, files in os.walk(location):
#         for name in files:
#             with open(location + name, 'r', encoding='utf-16') as ingredient_file:
#                 ingredient = json.load(ingredient_file)
#                 Ingredient.add(name=ingredient['name'], lemma=ingredient['lemma'],\
#                     recipe_refs=ingredient['recipe_refs'],\
#                     wiki_ref=ingredient['wiki_ref'], category=ingredient['category'],\
#                     other_recipe_ref=ingredient['other_recipe_ref'])
