"""Create a shopping list"""
import json
import logging
from urllib.parse import unquote
import math
# import re
import requests
import spacy
nlp = spacy.load("fr_core_news_md")
# import lxml.etree as ET

logger = logging.getLogger(__name__)

class Ingredient:
    """An ingredient for cooking"""
    # categories = ['Légume et fruit', 'Boucherie', 'Crémerie',\
    #               'Boulangerie', 'Epicerie', 'Boisson', 'Vin']
    # knowkn_ingredients_list = load.load_all_ingredients_files()
    knowkn_ingredients_list = []
    def __init__(self, name: str, lemma: str, wiki_ref=None, category=None,\
                 synonymes=None, recipe_ref=None, other_recipe_ref=None):
        self.name = name
        self.lemma = lemma
        self.wiki_ref = wiki_ref #if wiki_ref else Ingredient.get_wiki_ref(name)
        self.category = category
        self.synonymes = synonymes if synonymes else set([name, lemma])
        self.recipe_refs = recipe_ref if recipe_ref else set()
        self.other_recipe_ref = other_recipe_ref
        # prefered_unit
        # possible_units
        Ingredient.knowkn_ingredients_list.append(self)
        logger.info('Created: %s', str(self))

    def write_ingredient_file(self):
        """write an ingredient on disk in json"""
        name = self.wiki_ref if self.wiki_ref else self.name
        filename = name + '.json'
        with open('./ingredient_files/' + str(filename).encode('utf-16').decode('utf-16'),\
                  'w', encoding='utf-16') as outfile:
            json.dump(self.serialize(), outfile, indent=2, ensure_ascii=False)
        logger.info('%s written', filename)

    def __str__(self):
        return str('Ingredient: ' + str(self.name) + ' Wiki ref: ' + str(self.wiki_ref) +\
                   ' Synonymes: '  + str(self.synonymes) + ' recipe_ref: '  + str(self.recipe_refs)\
                   + ' lemma: '  + str(self.lemma)\
                  )

    @classmethod
    def add(cls, name: str, lemma: str, wiki_ref=None, category=None, recipe_ref=None, other_recipe_ref=None):
        """ add a new ingredient in the ingredients list if necessary
        otherwise update and return an existing ingredient"""
        # look for the name in all synonymes list
        for knowkn_ingredient in cls.knowkn_ingredients_list:
            if name in knowkn_ingredient.synonymes or\
                (' '.join([token.lemma_ for token in nlp(name)]) == knowkn_ingredient.lemma):
                knowkn_ingredient.synonymes.add(name)
                if recipe_ref and (recipe_ref not in knowkn_ingredient.recipe_refs):
                    knowkn_ingredient.recipe_refs = knowkn_ingredient.recipe_refs.union(recipe_ref)
                    logger.info('ref added %s', recipe_ref)
                    Ingredient.write_ingredient_file(knowkn_ingredient)
                return knowkn_ingredient
        print(name)
        new_ingredient = Ingredient(name=name, lemma=lemma, wiki_ref=wiki_ref, category=category,\
                                    synonymes=set([name]), recipe_ref=recipe_ref,\
                                    other_recipe_ref=other_recipe_ref)
        new_ingredient.write_ingredient_file()
        return new_ingredient

    @classmethod
    def get_wiki_ref(cls, name):
        """search for the name in wikipedia. Return the last part of the url aka wiki_ref"""
        wiki_ref = None
        #shorten the name
        # words = str(name).rsplit(sep=, maxsplit=5)
        # words = re.split(r"['()\s]+", name)
        words_lemma = [token.lemma_ if (token.pos_ == "NOUN") else token.text for token in nlp(name)]
        words_pos = [token.pos_ for token in nlp(name)]
        logger.info('lemmas: %s', words_lemma)
        nb_words = len(words_lemma)
        for i in range(nb_words):
            # search_str = '+'.join([s  for s in words[:nb_words-i]])
            # search_str = '+'.join(words[:nb_words-i])
            search_str = '+'.join(words_lemma[:nb_words-i])
            if 'NOUN' in words_pos[:nb_words-i]:
                logger.info('search string: %s', search_str)
                r = Ingredient.send_search_request(search_str)
                if r:
                    wiki_ref = Ingredient.parse_response(r)
                if wiki_ref:
                    return wiki_ref
        #try in reverse mode
        for i in range(nb_words):
            search_str = '+'.join(words_lemma[i:])
            if 'NOUN' in words_pos[:nb_words-i]:#paprika est vu comme un adjectif par spacy...
                logger.info('search string (reverse): %s', search_str)
                r = Ingredient.send_search_request(search_str)
                if r:
                    wiki_ref = Ingredient.parse_response(r)
                if wiki_ref:
                    return wiki_ref
        return wiki_ref

    @staticmethod
    def send_search_request(search_str: str):
        """Handle the get requests to Wikipedia. Return the response"""
        try:
            r = requests.get(f'https://fr.wikipedia.org/w/index.php?search={search_str}',\
                                allow_redirects=True, timeout=10)
        except ConnectionError:
            logger.info('No internet!')
            return None
        logger.info('Response received from Wikipedia.')
        # r.encoding = r.encoding = r.apparent_encoding
        if r.status_code != 200:
            logger.info('Bad response %s', r.status_code)
            return None
        return r

    @staticmethod
    def parse_response(response):
        """Parse the response of a get request to Wikipedia.
        May be usefull to categorize an ingredient"""
        wiki_ref = None
        for line in response.iter_lines():
            if 'https://fr.wikipedia.org/wiki/' in str(line):
                if 'Recherche' in str(line):
                    return None # no search result
                url = str(line)[str(line).index('https://fr.wikipedia.org/wiki/'):-3]
                #get rid of trailing hashtags if any
                url = url[:url.find('#')] if '#' in url else url
                # url = unquote(url)
                wiki_ref = unquote(str(url).rsplit(sep='/', maxsplit=1)[-1])
                logger.info('Found ref in wikipedia: %s', wiki_ref)
                break
        return wiki_ref

    # def categorize(self):
    #     r = requests.get('https://fr.wikipedia.org/w/index.php?search=beurre',\
    #                       allow_redirects=True, timeout=10)
    #     selector = Selector(text=str(r.content))
    #     selector.xpath('//h1/text()').r

    def serialize(self):
        """produce a dictionary containing relevant attributes for JSON serialization."""
        return dict({'name': self.name,\
                     'lemma': self.lemma,\
                     'wiki_ref': self.wiki_ref if self.wiki_ref else "",\
                     'category': self.category,\
                     'synonymes': list(self.synonymes),\
                     'recipe_refs': list(self.recipe_refs),\
                     'other_recipe_ref': self.other_recipe_ref if self.other_recipe_ref else ""\
                    })


class IngredientBill():
    """An ingredient with amount and unit"""
    def __init__(self, amount: float, unit: str, jxt: str, ingredient: Ingredient):
        self.amount = amount
        self.unit = unit
        self.jxt = jxt
        self.ingredient = ingredient
    def __str__(self):
        return str(self.ingredient.name) + ': ' + str(self.amount) + ' ' + str(self.unit)
    # def can_add(self, i: Ingredient_bill):
    #     return self.ingredient.name == i.ingredient.name

class Recipe():
    """A cooking recipe"""
    UNIT_LIST = ['millilitre', 'tour', 'tranche',  'l', 'pincée', 'brin', 'bâton', 'branche',\
 'botte', 'kilogramme', 'gramme', 'tête', 'trait', 'gousse', 'pincee', 'feuille', 'grain']
    # unit_list = ['tour de moulin', 'grains', 'grain', 'lamelles', 'tranches', 'tranche',\
    #              'branches', 'branche', 'feuilles', 'feuille', 'zeste', 'brins', 'brin',\
    #              'tranches', 'tranche', 'botte', 'gousses', 'gousse', 'g', 'kg', 'ml', 'l',\
    #              'cuil. à café', 'cuil. à soupe', 'cuil à soupe', 'c. à s.', 'pincee', 'pincée', 'tête',\
    #              'trait', 'zestes', 'zeste']
    juxtaposant_list = ['de', 'd\'', 'à']

    def __init__(self, ref: str, name: str, ingredients_bill):
        self.ref = ref
        self.name = name
        self.ingredients_bill = ingredients_bill
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
        unit = ' '.join(lemma_list[1:5])
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
    def load_morphology(file='./ingredientBillMorphology.json'):
        with open(file, 'r') as morphology_file:
            return json.load(morphology_file)

    @classmethod
    def parse_ingredients_bill_dict(cls, ingredients_bill_dict: dict, recipe_ref: str):
        """Transform the json created by the ocr module
            to a list of Ingredient_bill"""
        ingredients = []
        for d , amount in ingredients_bill_dict.items():
            morphology = Recipe.load_morphology()
            doc = nlp(' '.join([str(amount), d]))
            ingredient_bill_morphology = ' '.join([token.pos_ for token in doc])
            strategy = Recipe.choose_strategy(morphology[ingredient_bill_morphology])
            unit, jxt, name, lemma, other_recipe_ref =\
                strategy(d, text_list=[token.text for token in doc],\
                         lemma_list=[token.lemma_ for token in doc],\
                         pos_list=[token.pos_ for token in doc],\
                         book_ref = recipe_ref[0:recipe_ref.rindex('p')] if 'p' in recipe_ref else None)
            ingredients.append(IngredientBill(amount, unit, jxt,\
                        Ingredient.add(name=name,lemma=lemma, recipe_ref=set([str(recipe_ref)]),\
                                       other_recipe_ref=other_recipe_ref)))

            # unit = 'p'
            # jxt = ''
            # rest = d
            # for unit_item in cls.unit_list:
            #     if d.startswith(unit_item + ' '):
            #         unit = unit_item
            #         rest = d[len(str(unit)):].lstrip()
            #         for jxt_item in cls.juxtaposant_list:
            #             if rest.startswith(jxt_item):
            #                 jxt = jxt_item
            #                 rest = rest[len(str(jxt_item)):].lstrip()
            #                 break
            #         break
            # ingredients.append(IngredientBill(amount, unit, jxt,\
            #             Ingredient.add(name=rest,recipe_ref=set([str(recipe_ref)]))))
        return ingredients
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
        """Merge a list of ingredients bills to one ingredients bill."""
        total_ingredients_bill = []
        for (recipe, ratio) in self.recipes:
            print(recipe.name)
            for ingredient_bill in recipe.ingredients_bill:
                added = False
                for total_ingredient_bill in total_ingredients_bill:
                    if total_ingredient_bill.ingredient is ingredient_bill.ingredient\
                        and total_ingredient_bill.unit == ingredient_bill.unit:
                        total_ingredient_bill.amount +=\
                                int(math.ceil(ingredient_bill.amount * float(ratio)))
                        added = True
                        break
                if not added: #then append
                    amount = int(math.ceil(ingredient_bill.amount * float(ratio)))
                    total_ingredients_bill.append(IngredientBill(amount, ingredient_bill.unit,\
                                                ingredient_bill.jxt, ingredient_bill.ingredient))
        total_ingredients_bill.sort(key=lambda x: x.ingredient.name)

        return total_ingredients_bill

    def __str__(self) -> str:
        pass
