"""Recipe"""
import logging
import json
import configparser
import math
import spacy
from ingredient import Ingredient

nlp = spacy.load("fr_core_news_md")
config = configparser.ConfigParser()
config.read('./config.cfg')
logger = logging.getLogger(__name__)

class IngredientBill():
    """An ingredient with amount and unit"""
    def __init__(self, amount: float, unit: str, jxt: str, ingredient: Ingredient):
        self.amount = amount
        self.unit = unit
        self.jxt = jxt
        self.ingredient = ingredient
    def __str__(self):
        return str(self.ingredient.name) + ': ' + str(self.amount) + ' ' + str(self.unit)
    def serialize(self):
        """produce a dictionary containing relevant attributes for JSON serialization."""
        return dict({'amount': self.amount,\
                     'unit': self.unit,\
                     'jxt': self.jxt,\
                     'ingredient': self.ingredient.name
                    })
class Recipe():
    """A cooking recipe"""

    def __init__(self, ref: str, name: str, ingredients_bill):
        self.ref = ref
        self.name = name
        self.ingredients_bill = ingredients_bill

    def serialize(self):
        """produce a dictionary containing relevant attributes for JSON serialization."""
        return dict({'ref': self.ref,\
                     'name': self.name,\
                     'ingredients_bill': [i.serialize() for i in self.ingredients_bill]
                    })
    def write_recipe_file(self, location=config['DEFAULT']['RECIPES_DIR']):
        """write an recipe on disk in json"""
        name = self.ref if self.ref else self.name
        filename = name + '.json'
        with open(str(location) + '/' + str(filename).encode('utf-16').decode('utf-16'),
                  'w', encoding='utf-16') as outfile:
            json.dump(self.serialize(), outfile, indent=2, ensure_ascii=False)
        with open(str(location) + '/' + str(filename) + '-utf8',
                  'w', encoding='utf-8') as outfile:
            json.dump(self.serialize(), outfile, indent=2, ensure_ascii=False)
        logger.info('%s written', filename)

    def __str__(self):
        return f"{self.name} ({self.ref})"

class Menu():
    """A list of recipes"""
    def __init__(self, season='None') -> None:
        self.season = season
        self.recipes = []

    def add_recipe(self, recipe:Recipe, ratio=1):
        """Append a recipe to the list"""
        self.recipes.append((recipe, float(ratio)))
    def merge_ingredients(self):
        """merge ingredients that have the same lemma
        sum the amounts if possible
        """
        total_ingredients_bill = []
        for (recipe, ratio) in self.recipes:
            for ingredient_bill in recipe.ingredients_bill:
                added = False
                name = ingredient_bill['ingredient']
                i = Ingredient.add(name=name,\
                                    lemma=' '.join([token.lemma_ for token in nlp(name)]),\
                                    recipe_refs=set([recipe.ref]))
                for total_ingredient_bill in total_ingredients_bill:
                    if total_ingredient_bill.ingredient is i\
                        and total_ingredient_bill.unit == ingredient_bill['unit']:
                        total_ingredient_bill.amount +=\
                                int(math.ceil(ingredient_bill['amount'] * float(ratio)))
                        added = True
                        break
                if not added: #then append
                    amount = int(math.ceil(ingredient_bill['amount'] * float(ratio)))
                    # name = ingredient_bill['ingredient']
                    total_ingredients_bill.append(\
                        IngredientBill(amount=amount, unit=ingredient_bill['unit'],\
                                       jxt=ingredient_bill['jxt'], ingredient=i))
        total_ingredients_bill.sort(key=lambda x: x.ingredient.name)
        return total_ingredients_bill
