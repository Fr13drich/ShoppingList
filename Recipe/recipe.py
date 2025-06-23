import logging
import json
import configparser
import spacy
from Ingredient import Ingredient
# from Reader.parser import get_strategy

config = configparser.ConfigParser()
config.read('./config.cfg')
logger = logging.getLogger(__name__)
nlp = spacy.load("fr_core_news_md")

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
    UNIT_LIST = ['millilitre', 'tour', 'tranche',  'l', 'pincée', 'brin',\
                 'bâton', 'bille', 'branche', 'botte', 'kilogramme', 'gramme', 'tête',\
                 'trait', 'gousse', 'pincee', 'feuille', 'grain', 'morceau']
    # juxtaposant_list = ['de', 'd\'', 'à']

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
    def write_recipe_file(self):
        """write an recipe on disk in json"""
        name = self.ref if self.ref else self.name
        filename = name + '.json'
        with open(config['DEFAULT']['RECIPES_DIR'] +\
                  str(filename).encode('utf-16').decode('utf-16'),\
                  'w', encoding='utf-16') as outfile:
            json.dump(self.serialize(), outfile, indent=2, ensure_ascii=False)
        logger.info('%s written', filename)

def __str__(self):
    return f"{self.name} ({self.ref})"
