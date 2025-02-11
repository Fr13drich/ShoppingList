"""Create a shopping list"""
from collections import Counter
from typing import List
import math
import requests
import lxml.etree as ET
from parsel import Selector

class Recipe():
    """A cooking recipe"""
    unit_list = ['tour de moulin', 'branches', 'branche', 'feuilles', 'feuille', 'zeste', 'brins', 'brin', 'botte', 'gousses', 'gousse', 'g', 'kg', 'ml', 'cuil. à café', 'cuil. à soupe', 'cuil à soupe', 'pincee', 'pincée', 'tête', 'l']
    juxtaposant_list = ['de', 'd\'', 'à']
    def __init__(self, ref: str, name: str, ingredients_bill: dict):
        self.ref = ref
        self.name = name
        self.ingredients = Recipe.parse_ingredients_bill(ingredients_bill)

    @classmethod
    def parse_ingredients_bill(cls, ingredients_bill: dict):
        ingredients = []
        for line in ingredients_bill:
            # print(line)
            unit = 'p'
            rest = line
            for unit_item in cls.unit_list:
                if line.startswith(unit_item + ' '):
                    unit = unit_item
                    rest = line[len(str(unit)):].lstrip()
                    for jxt_item in cls.juxtaposant_list:
                        if rest.startswith(jxt_item):
                            rest = rest[len(str(jxt_item)):].lstrip()
                            break
                    break
            ingredients.append((Ingredient(rest), ingredients_bill[line], unit))
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
        total = {}
        for (recipe, ratio) in self.recipes:
            for ingredient in recipe.ingredients:
                if ingredient[0].name not in total:
                    total[ingredient[0].name] = {ingredient[2]: 0}
                if ingredient[2] not in total[ingredient[0].name]:
                    total[ingredient[0].name][ingredient[2]] = 0
                total[ingredient[0].name][ingredient[2]] += int(math.ceil(ingredient[1] * float(ratio)))
        # print(total)
        return dict(total)
    def __str__(self) -> str:
        pass

class Ingredient:
    categories = ['Légume et fruit', 'Boucherie', 'Crémerie', 'Boulangerie', 'Epicerie', 'Boisson', 'Vin']
    def __init__(self, i: str):
        self.name = str(i).lower()
        # prefered_unit
        # possible_units
        # print( 'Created: name: ' + str(self.name))
    def categorize(self):
        r = requests.get('https://fr.wikipedia.org/w/index.php?search=beurre', allow_redirects=True)
        selector = Selector(text=str(r.content))
        selector.xpath('//h1/text()').r
        

