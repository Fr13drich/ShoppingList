"""Create a shopping list"""
from collections import Counter
from typing import List

class Recipe():
    """A cooking recipe"""
    unit_list = ['brin', 'botte', 'gousses', 'gousse', 'g', 'kg', 'ml', 'cuil. à café', 'cuil. à soupe', 'pincee', 'pincée', 'tête', 'l']
    juxtaposant_list = ['de', 'd\'']
    def __init__(self, ref: str, name: str, ingredients_bill: dict, instructions=None):
        self.ref = ref
        self.name = name
        self.ingredients = []
        for line in ingredients_bill:
            # print(line)
            unit = 'unité(s)'
            rest = line
            for unit_item in Recipe.unit_list:
                if line.startswith(unit_item + ' '):
                    unit = unit_item
                    rest = line[str(unit).__len__():].lstrip()
                    for jxt_item in Recipe.juxtaposant_list:
                        if rest.startswith(jxt_item):
                            rest = rest[str(jxt_item).__len__():].lstrip()
                            break
                    break
            self.ingredients.append((Ingredient(rest), ingredients_bill[line], unit))

        self.instructions = instructions
    """A few class methods to convert quantities"""
    #TODO
    def __str__(self) -> str:
        return self.name

class Menu():
    """A list of recipes"""
    def __init__(self, season='None', recipes=[]) -> None:
        self.season = season
        self.recipes = recipes

    def add_recipe(self, recipe:Recipe):
        self.recipes.append(recipe)

    def merge_ingredients(self):
        total = {}
        for recipe in self.recipes:
            for ingredient in recipe.ingredients:
                if ingredient[0].name not in total:
                    total[ingredient[0].name] = (0, ingredient[2])
                total[ingredient[0].name] = (total[ingredient[0].name][0] + ingredient[1], ingredient[2])
                print(total)
        # print(total)
        return dict(total)
    def __str__(self) -> str:
        pass

class Ingredient:
    type_list = ['épice', 'crèmerie', 'légume', 'sucre', 'oeuf', 'farine', 'levure']
    
    def __init__(self, i: str):
        self.name = i
        # print( 'Created: name: ' + str(self.name))
