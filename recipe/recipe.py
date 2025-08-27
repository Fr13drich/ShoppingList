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
config.read('./config.cfg', encoding='utf-8')
logger = logging.getLogger(__name__)

class IngredientEntry:
    """Represents an ingredient with its amount, unit, and additional context.

    Attributes:
        amount (float): Quantity of the ingredient.
        unit (str): Unit of measurement.
        jxt (str): Juxtaposant (e.g., 'de', 'à').
        ingredient (Ingredient): Ingredient object.
    """

    def __init__(self, amount: float, unit: str, jxt: str, ingredient: Ingredient):
        self.amount = amount
        self.unit = IngredientEntry.get_std_unit(unit)
        self.jxt = jxt
        self.ingredient = ingredient

    @classmethod
    def get_std_unit(cls, unit: str) -> str:
        """Convert various unit representations to a standard form.

        Args:
            unit (str): The unit to standardize.

        Returns:
            str: The standardized unit.
        """
        unit_mapping = {
            'cuillère à soupe': 'càs',
            'cuillère à café': 'càc',
            'cuil. à soupe': 'càs',
            'cuil. à café': 'càc',
            'c. à s.': 'càs',
            'c.às': 'càs',
            'cuillères à soupe': 'càs',
            'c. à c.': 'càc',
            'litre': 'l',
            'millilitre': 'ml',
            'gramme': 'g',
            'kilogramme': 'kg',
            'pincées': 'pincée',
            'brins': 'brin',
            'bâtons': 'bâton',
            'billes': 'bille',
            'branches': 'branche',
            'bottes': 'botte',
            'têtes': 'tête',
            'traits': 'trait',
            'gousses': 'gousse',
            'grains': 'grain',
            'morceaux': 'morceau',
        }
        return unit_mapping.get(unit, unit)

    def __repr__(self):
        return f"{self.amount} {self.unit} {self.jxt} {self.ingredient.name}"

    def __str__(self):
        """Return a human-readable string representation of the ingredient entry."""
        return f"{self.ingredient.name}: {self.amount} {self.unit}"

    def __add__(self, ingredient_entry):
        """Add two IngredientEntry objects if they refer to the same ingredient and unit.

        Args:
            ingredient_entry (IngredientEntry): Another ingredient entry to add.

        Returns:
            IngredientEntry: New IngredientEntry with summed amount,
            or NotImplemented if incompatible.
        """
        if self.ingredient == ingredient_entry.ingredient and self.unit == ingredient_entry.unit:
            return IngredientEntry(
                amount=self.amount + ingredient_entry.amount,
                unit=self.unit,
                jxt=self.jxt,
                ingredient=self.ingredient
            )
        return NotImplemented

    def serialize(self):
        """Convert the ingredient entry to a dictionary for JSON serialization.

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
        ingredients_bill (list): List of IngredientEntry objects.
    """

    def __init__(self, ref: str, name: str, ingredients_bill: list[IngredientEntry]):
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

    @staticmethod
    def load_recipe_file(filename):
        """Load a recipe from a JSON file.

        Args:
            filename (str): Path to the recipe file.

        Returns:
            Recipe: Loaded Recipe object, or None if loading fails.
        """
        try:
            with open(filename, 'r', encoding='utf-8') as infile:
                data = json.load(infile)
            ingredients_bill = []
            for ingredient_entry in data['ingredients_bill']:
                ingredient = Ingredient.get(ingredient_entry['ingredient'])
                if not ingredient:
                    ingredient = Ingredient.add(
                        name=ingredient_entry['ingredient'],
                        lemma=' '.join([token.lemma_ for token in
                                        nlp(ingredient_entry['ingredient'])]),
                                        recipe_refs=set([data['ref']])
                    )
                ingredients_bill.append(
                    IngredientEntry(
                        amount=ingredient_entry['amount'],
                        unit=ingredient_entry['unit'],
                        jxt=ingredient_entry['jxt'],
                        ingredient=ingredient
                    )
                )
            return Recipe(
                ref=data['ref'],
                name=data['name'],
                ingredients_bill=ingredients_bill
            )
        except (FileNotFoundError, json.JSONDecodeError, KeyError) as e:
            logger.error('Failed to load recipe from %s: %s', filename, e)
            return None

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
            list: Sorted list of merged IngredientEntry objects.
        """
        total_ingredients_bill = []
        for (recipe, ratio) in self.recipes:
            for ingredient_entry in recipe.ingredients_bill:
                added = False
                name = ingredient_entry['ingredient']
                i = Ingredient.add(
                    name=name,
                    lemma=' '.join([token.lemma_ for token in nlp(name)]),
                    recipe_refs=set([recipe.ref])
                )
                for total_ingredient_entry in total_ingredients_bill:
                    logger.debug('Comparing %s with %s', total_ingredient_entry, ingredient_entry)
                    logger.debug('IS: %s', total_ingredient_entry.ingredient is i)
                    logger.debug('Unit: %s', total_ingredient_entry.unit)
                    logger.debug('Unit: %s', ingredient_entry['unit'])
                    # Check if the ingredient and unit match
                    if total_ingredient_entry.ingredient is i\
                        and total_ingredient_entry.unit\
                            == IngredientEntry.get_std_unit(ingredient_entry['unit']):
                        total_ingredient_entry.amount += int(math.ceil(ingredient_entry['amount']\
                                                                      * float(ratio)))
                        added = True
                        break
                if not added:
                    amount = int(math.ceil(ingredient_entry['amount'] * float(ratio)))
                    total_ingredients_bill.append(
                        IngredientEntry(amount=amount, unit=ingredient_entry['unit'],
                                       jxt=ingredient_entry['jxt'], ingredient=i)
                    )
        total_ingredients_bill.sort(key=lambda x: x.ingredient.name)
        return total_ingredients_bill
