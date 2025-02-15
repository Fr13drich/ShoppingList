"""Create a shopping list"""
import requests
import json
from typing import List
from urllib.parse import unquote
import math
import requests
import lxml.etree as ET
# import load

class Ingredient:
    categories = ['Légume et fruit', 'Boucherie', 'Crémerie', 'Boulangerie', 'Epicerie', 'Boisson', 'Vin']
    # knowkn_ingredients_list = load.load_all_ingredients_files()
    knowkn_ingredients_list = []
    def __init__(self, name: str, wiki_ref=None, category=None, synonymes=[]):
        self.name = name
        self.wiki_ref = wiki_ref #if wiki_ref else Ingredient.get_wiki_ref(name)
        self.category = category
        self.synonymes = synonymes if synonymes else [name]
        # prefered_unit
        # possible_units
        Ingredient.knowkn_ingredients_list.append(self)
        print('Created: ' + str(self))
        
    def write_ingredient_file(self):
        name = self.wiki_ref if self.wiki_ref else self.name
        filename = name + '.json'
        with open('./ingredient_files/' + str(filename).encode('utf-16').decode('utf-16'), 'w', encoding='utf-16') as outfile:
            json.dump(self.serialize(), outfile, indent=2)
        print(filename + ' written')
    
    def __str__(self):
        return str('Ingredient: ' + str(self.name) + ' Wiki ref: ' + str(self.wiki_ref))

    @classmethod
    def add(cls, name, wiki_ref=None, category=None):
        for knowkn_ingredient in cls.knowkn_ingredients_list:
            if name in knowkn_ingredient.synonymes:
                return knowkn_ingredient
        #the name is not known let's check in wikipedia:
        if not wiki_ref:
            wiki_ref = Ingredient.get_wiki_ref(name)
        if wiki_ref:
            # is this ref known?
            for knowkn_ingredient in cls.knowkn_ingredients_list:
                if wiki_ref == knowkn_ingredient.wiki_ref:
                    knowkn_ingredient.synonymes.append(name)
                    print('synonyme added')
                    knowkn_ingredient.write_ingredient_file()
                    return knowkn_ingredient
        #new wiki_ref or None
        new_ingredient = Ingredient(name, wiki_ref)
        new_ingredient.write_ingredient_file()
        return new_ingredient

    @classmethod
    def get_wiki_ref(cls, name):
        """return a wikipedia url"""
        url= None
        wiki_ref = None
        #shorten the name
        if len(name.split()) > 3:
            name = name.split()[0:3]
        nb_words = len(name.split())
        for i in range(nb_words):
            r = requests.get(f'https://fr.wikipedia.org/w/index.php?search={str(name).replace(" ", "+")}',\
                             allow_redirects=True, timeout=10)
            print('request done to wikipedia')
            # r.encoding = r.encoding = r.apparent_encoding
            if r.status_code != 200:
                print(r.status_code)
                return None
            for line in r.iter_lines():
                if 'https://fr.wikipedia.org/wiki/' in str(line):
                    if 'Recherche' in str(line):
                        break # no search result
                    url = str(line)[str(line).index('https://fr.wikipedia.org/wiki/'):-3]
                    url = unquote(url)
                    wiki_ref = str(url).rsplit(sep='/', maxsplit=1)[-1]
                    print(wiki_ref)
                    break
            if wiki_ref:
                break
            else:
                name = name.split(maxsplit=nb_words-i+1)
        return wiki_ref

    # def categorize(self):
    #     r = requests.get('https://fr.wikipedia.org/w/index.php?search=beurre', allow_redirects=True, timeout=10)
    #     selector = Selector(text=str(r.content))
    #     selector.xpath('//h1/text()').r

    def serialize(self):
        """produce a dictionary containing relevant attributes for JSON serialization."""
        return dict({'name': self.name, 'wiki_ref': self.wiki_ref if self.wiki_ref else "",\
                     'category': self.category, 'synonymes': self.synonymes})


class Ingredient_bill():
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
    unit_list = ['tour de moulin', 'branches', 'branche', 'feuilles', 'feuille', 'zeste', 'brins', 'brin', 'botte', 'gousses', 'gousse', 'g', 'kg', 'ml', 'cuil. à café', 'cuil. à soupe', 'cuil à soupe', 'pincee', 'pincée', 'tête', 'l']
    juxtaposant_list = ['de', 'd\'', 'à']

    def __init__(self, ref: str, name: str, ingredients_bill):
        self.ref = ref
        self.name = name
        self.ingredients_bill = ingredients_bill
    
    @classmethod
    def parse_ingredients_bill_dict(cls, ingredients_bill_dict: dict):
        """Transform to a list of Ingredient_bill"""
        ingredients = []
        for d , amount in ingredients_bill_dict.items():
            unit = 'p'
            jxt = ''
            rest = d
            for unit_item in cls.unit_list:
                if d.startswith(unit_item + ' '):
                    unit = unit_item
                    rest = d[len(str(unit)):].lstrip()
                    for jxt_item in cls.juxtaposant_list:
                        if rest.startswith(jxt_item):
                            jxt = jxt_item
                            rest = rest[len(str(jxt_item)):].lstrip()
                            break
                    break
            ingredients.append(Ingredient_bill(amount, unit, jxt, Ingredient.add(rest)))
        return ingredients

    def __str__(self):
        return f"{self.name} ({self.ref})"

class Menu():
    """A list of recipes"""
    def __init__(self, season='None') -> None:
        self.season = season
        self.recipes = []

    def add_recipe(self, recipe:Recipe, ratio=1):
        self.recipes.append((recipe, float(ratio)))

    def merge_ingredients(self):
        total_ingredients_bill = []
        for (recipe, ratio) in self.recipes:
            print(recipe.name)
            for ingredient_bill in recipe.ingredients_bill:
                added = False
                for total_ingredient_bill in total_ingredients_bill:
                    if total_ingredient_bill.ingredient is ingredient_bill.ingredient\
                        and total_ingredient_bill.unit == ingredient_bill.unit:
                        total_ingredient_bill.amount += int(math.ceil(ingredient_bill.amount * float(ratio)))
                        added = True
                        break
                if not added: #then append
                    amount = int(math.ceil(ingredient_bill.amount * float(ratio)))
                    total_ingredients_bill.append(Ingredient_bill(amount, ingredient_bill.unit, ingredient_bill.jxt, ingredient_bill.ingredient))
        return total_ingredients_bill

    def __str__(self) -> str:
        pass


    
