"""Create a shopping list"""
from collections import Counter
from typing import List

class Recipe():
    """A cooking recipe"""
    unit_list = [ 'g', 'kg', 'ml', 'cuil. à café', 'cuil. à soupe', 'pincee', 'pincée', 'gousse', 'gousses', 'tête']
    juxtaposant_list = ['de', 'd\'']
    def __init__(self, ref: str, name: str, ingredients_bill: dict, instructions=None):
        self.ref = ref
        self.name = name
        self.ingredients = []
        #self.ingredients = ingredients_bill
        # self.ingredients = [ingredient(i for i in ingredients_bill)]
        # print(ingredients_bill)
        for line in ingredients_bill:
            # print(line)
            unit = 'scalar'
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
    def __init__(self, season, recipes) -> None:
        self.season = season
        self.recipes = recipes
    def merge_ingredients(self):
        total = {}
        for recipe in self.recipes:
            for ingredient in recipe.ingredients:
                if ingredient[0].name not in total:
                    total[ingredient[0].name] = 0
                total[ingredient[0].name] += ingredient[1]
                print(total)
        # print(total)
        return dict(total)
    def __str__(self) -> str:
        pass

class Ingredient:
    type_list = ['epice', 'cremerie', 'legume', 'sucre', 'oeuf', 'farine', 'levure']
    
    def __init__(self, i: str):
        
        # for w in Ingredient.juxtaposant_list:
        #     if i.startswith(w):
        #         # i = i[i.find(sub=w) + str(w).__len__():]
        #         i = i[str(w).__len__():]
        #         break
        self.name = i
        # print( 'Created: name: ' + str(self.name))
