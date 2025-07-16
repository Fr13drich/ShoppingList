"""Recipe management module.

Defines classes for representing ingredients, recipes, and menus.
Handles serialization and file writing for recipes and ingredients.
"""

import os
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
    """Represents an ingredient with its amount, unit, and additional context.

    Attributes:
        amount (float): Quantity of the ingredient.
        unit (str): Unit of measurement.
        jxt (str): Juxtaposant (e.g., 'de', 'à').
        ingredient (Ingredient): Ingredient object.
    """

    def __init__(self, amount: float, unit: str, jxt: str, ingredient: Ingredient):
        self.amount = amount
        self.unit = unit
        self.jxt = jxt
        self.ingredient = ingredient

    def __str__(self):
        """Return a human-readable string representation of the ingredient bill."""
        return f"{self.ingredient.name}: {self.amount} {self.unit}"

    def __add__(self, ingredient_bill):
        """Add two IngredientBill objects if they refer to the same ingredient and unit.

        Args:
            ingredient_bill (IngredientBill): Another ingredient bill to add.

        Returns:
            IngredientBill: New IngredientBill with summed amount,
            or NotImplemented if incompatible.
        """
        if self.ingredient == ingredient_bill.ingredient and self.unit == ingredient_bill.unit:
            return IngredientBill(
                amount=self.amount + ingredient_bill.amount,
                unit=self.unit,
                jxt=self.jxt,
                ingredient=self.ingredient
            )
        return NotImplemented

    def serialize(self):
        """Convert the ingredient bill to a dictionary for JSON serialization.

        Returns:
            dict: Dictionary of relevant attributes.
        """
        return {
            'amount': self.amount,
            'unit': self.unit,
            'jxt': self.jxt,
            'ingredient': self.ingredient.name
        }

class Recipe():
    """Represents a cooking recipe.

    Attributes:
        ref (str): Reference code for the recipe.
        name (str): Name of the recipe.
        ingredients_bill (list): List of IngredientBill objects.
    """

    def __init__(self, ref: str, name: str, ingredients_bill):
        self.ref = ref
        self.name = name
        self.ingredients_bill = ingredients_bill

    def serialize(self):
        """Convert the recipe to a dictionary for JSON serialization.

        Returns:
            dict: Dictionary of relevant attributes.
        """
        return {
            'ref': self.ref,
            'name': self.name,
            'ingredients_bill': [i.serialize() for i in self.ingredients_bill]
        }

    def write_recipe_file(self, location=config['DEFAULT']['RECIPES_DIR']):
        """Write the recipe to disk as a JSON file.

        Args:
            location (str): Directory to save the recipe file.
        """
        name = self.ref if self.ref else self.name
        filename = name + '.json'
        with open(os.path.join(location, filename), 'w', encoding='utf-8') as outfile:
            json.dump(self.serialize(), outfile, indent=2, ensure_ascii=False)
        logger.info('%s written', filename)

    def __str__(self):
        """Return a human-readable string representation of the recipe."""
        return f"{self.name} ({self.ref})"

class Menu():
    """Represents a menu consisting of multiple recipes.

    Attributes:
        season (str): Season for the menu.
        recipes (list): List of tuples (Recipe, ratio).
    """

    def __init__(self, season='None') -> None:
        self.season = season
        self.recipes = []

    def add_recipe(self, recipe:Recipe, ratio=1):
        """Add a recipe to the menu.

        Args:
            recipe (Recipe): Recipe to add.
            ratio (float): Scaling factor for the recipe.
        """
        self.recipes.append((recipe, float(ratio)))

    def merge_ingredients(self):
        """Merge ingredients from all recipes,
        summing amounts for identical ingredients.

        Returns:
            list: Sorted list of merged IngredientBill objects.
        """
        total_ingredients_bill = []
        for (recipe, ratio) in self.recipes:
            for ingredient_bill in recipe.ingredients_bill:
                added = False
                name = ingredient_bill['ingredient']
                i = Ingredient.add(
                    name=name,
                    lemma=' '.join([token.lemma_ for token in nlp(name)]),
                    recipe_refs=set([recipe.ref])
                )
                for total_ingredient_bill in total_ingredients_bill:
                    if total_ingredient_bill.ingredient is i\
                        and total_ingredient_bill.unit == ingredient_bill['unit']:
                        # If the ingredient already exists, update its amount
                        # and set added to True to avoid adding it again.
                        total_ingredient_bill.amount += int(math.ceil(ingredient_bill['amount']\
                                                                      * float(ratio)))
                        added = True
                        break
                if not added:
                    amount = int(math.ceil(ingredient_bill['amount'] * float(ratio)))
                    total_ingredients_bill.append(
                        IngredientBill(amount=amount, unit=ingredient_bill['unit'],
                                       jxt=ingredient_bill['jxt'], ingredient=i)
                    )
        total_ingredients_bill.sort(key=lambda x: x.ingredient.name)
        return total_ingredients_bill
