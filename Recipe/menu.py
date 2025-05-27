"""Create a shopping list"""
import math
import spacy
from Recipe import Recipe, IngredientBill
from Ingredient import Ingredient

nlp = spacy.load("fr_core_news_md")

class Menu():
    """A list of recipes"""
    def __init__(self, season='None') -> None:
        self.season = season
        self.recipes = []

    def add_recipe(self, recipe:Recipe, ratio=1):
        """Append a recipe to the list"""
        self.recipes.append((recipe, float(ratio)))
    def merge_ingredients(self):
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

    # def merge_ingredients(self):
    #     """Merge a list of ingredients bills to one ingredients bill."""
    #     # il faudrait définir un opérateur pour additionner 2 elts
    #     total_ingredients_bill = []
    #     for (recipe, ratio) in self.recipes:
    #         for ingredient_bill in recipe.ingredients_bill:
    #             added = False
    #             for total_ingredient_bill in total_ingredients_bill:
    #                 if total_ingredient_bill.ingredient is ingredient_bill.ingredient\
    #                     and total_ingredient_bill.unit == ingredient_bill.unit:
    #                     total_ingredient_bill.amount +=\
    #                             int(math.ceil(ingredient_bill.amount * float(ratio)))
    #                     added = True
    #                     break
    #             if not added: #then append
    #                 amount = int(math.ceil(ingredient_bill.amount * float(ratio)))
    #                 total_ingredients_bill.append(IngredientBill(amount, ingredient_bill.unit,\
    #                                             ingredient_bill.jxt, ingredient_bill.ingredient))
    #     total_ingredients_bill.sort(key=lambda x: x.ingredient.name)
    #     return total_ingredients_bill

    def __str__(self) -> str:
        pass
