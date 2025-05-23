import logging
import json
import configparser
import spacy
from Ingredient import Ingredient

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
                 'bâton', 'branche', 'botte', 'kilogramme', 'gramme', 'tête',\
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
    @staticmethod
    def strategy01(d: str, text_list, lemma_list, pos_list, book_ref: str):
        other_recipe_ref = None
        #check for a ref to another recipe
        if pos_list[-5:] == ["PUNCT", "VERB", "NOUN", "NUM", "PUNCT"]:
            other_recipe_ref = book_ref + 'p' + str(text_list[-2])
            lemma_list = lemma_list[:-5]
            d = d[0:d.index(' (')] if d.find('(') else d
        if lemma_list[1] in Recipe.UNIT_LIST:
            lemma = ' '.join(lemma_list[3:])
            unit = str(lemma_list[1])
            jxt = str(text_list[2])
            name = d[d.index(text_list[3]):]  #' '.join(text_list[3:])
        else:
            lemma = lemma_list[1]
            unit = 'p'
            jxt = ''
            name = d[d.index(text_list[1]):]
        # lemma = ' '.join(lemma_list[1:])
        return (unit, jxt, name, lemma, other_recipe_ref)
    @staticmethod
    def strategy013(d: str, text_list, lemma_list, pos_list, book_ref: str):
        other_recipe_ref = None
        #check for a ref
        if pos_list[-5:] == ["PUNCT", "VERB", "NOUN", "NUM", "PUNCT"]:
            other_recipe_ref = book_ref + 'p' + str(text_list[-2])
            lemma_list = lemma_list[:-5]
            d = d[0:d.index(' (')] if d.find('(') else d
        #check for a unit
        if lemma_list[1] in Recipe.UNIT_LIST:
            lemma = ' '.join(lemma_list[3:])
            unit = str(lemma_list[1])
            jxt = str(text_list[2])
            name = d[d.index(text_list[3]):]  #' '.join(text_list[3:])
        else:
            lemma = lemma_list[1]
            unit = 'p'
            jxt = ''
            name = d[d.index(text_list[1]):]
        return (unit, jxt, name, lemma, other_recipe_ref)
    @staticmethod
    def strategy0135(d: str, text_list, lemma_list, pos_list, book_ref: str):
        other_recipe_ref = None
        #check for a ref
        if pos_list[-5:] == ["PUNCT", "VERB", "NOUN", "NUM", "PUNCT"]:
            other_recipe_ref = book_ref + 'p' + str(text_list[-2])
            lemma_list = lemma_list[:-5]
            d = d[0:d.index(' (')] if d.find('(') else d
        lemma = ' '.join(lemma_list[3:5])
        unit = str(lemma_list[1])
        jxt = str(text_list[2])
        name = d[d.index(text_list[3]):d.index(text_list[4])+len(text_list[4])]
        return (unit, jxt, name, lemma, other_recipe_ref)
    @staticmethod
    def strategy0156(d: str, text_list, lemma_list, pos_list, book_ref: str):
        other_recipe_ref = None
        #check for a ref
        if pos_list[-5:] == ["PUNCT", "VERB", "NOUN", "NUM", "PUNCT"]:
            # buils a recipe ref based on the page number found(NUM)
            other_recipe_ref = book_ref + 'p' + str(text_list[-2])
            lemma_list = lemma_list[:-5]
            d = d[0:d.index(' (')] if d.find('(') else d
        lemma = ' '.join(lemma_list[6:])
        # unit = ' '.join(lemma_list[1:5])
        unit = d[d.index(text_list[1]):d.index(text_list[5])-1]
        jxt = str(text_list[5])
        name = d[d.index(text_list[6]):]
        return (unit, jxt, name, lemma, other_recipe_ref)
    @staticmethod
    def strategy04(d: str, text_list, lemma_list, pos_list, book_ref: str):
        """Ingredient name in position 4. No unit nor jxt."""
        other_recipe_ref = None
        #check for a ref
        if pos_list[-5:] == ["PUNCT", "VERB", "NOUN", "NUM", "PUNCT"]:
            other_recipe_ref = book_ref + 'p' + str(text_list[-2])
            lemma_list = lemma_list[:-5]
            d = d[0:d.index(' (')] if d.find('(') else d
        lemma = ' '.join(lemma_list[4:])
        unit = 'p'
        name = d[d.index(text_list[4]):]
        return (unit, '', name, lemma, other_recipe_ref)
    @staticmethod
    def choose_strategy(s: str):
        if s == "strategy01":
            return Recipe.strategy01
        if s == "strategy013":
            return Recipe.strategy013
        if s == "strategy0135":
            return Recipe.strategy0135
        if s == "strategy0156":
            return Recipe.strategy0156
        if s == "strategy04":
            return Recipe.strategy04

    @staticmethod
    def load_morphology(file=config['DEFAULT']['INGREDIENT_BILL_MORPHOLOGY_FILE']):
        with open(file, 'r', encoding='utf-8', ) as morphology_file:
            return json.load(morphology_file)

    @classmethod
    def parse_ingredients_bill_dict(cls, ingredients_bill_dict: dict, recipe_ref: str):
        """Transform the json created by the ocr module
            to a list of ingredients"""
        ingredients = []
        for d , amount in ingredients_bill_dict.items():
            morphology = Recipe.load_morphology()
            doc = nlp(' '.join([str(amount), d]))
            ingredient_bill_morphology = ' '.join([token.pos_ for token in doc])
            try:
                strategy = Recipe.choose_strategy(morphology[ingredient_bill_morphology])
            except KeyError:
                logger.warning('Key error on %s %s', d, ingredient_bill_morphology)
            unit, jxt, name, lemma, other_recipe_ref =\
                strategy(d, text_list=[token.text for token in doc],\
                         lemma_list=[token.lemma_ for token in doc],\
                         pos_list=[token.pos_ for token in doc],\
                         book_ref = recipe_ref[0:recipe_ref.rindex('p')] if 'p' in recipe_ref else None)
            ingredients.append(IngredientBill(amount, unit, jxt,\
                        Ingredient.add(name=name,lemma=lemma, recipe_refs=set([str(recipe_ref)]),\
                                       other_recipe_ref=other_recipe_ref)))
        return ingredients
    def __str__(self):
        return f"{self.name} ({self.ref})"
