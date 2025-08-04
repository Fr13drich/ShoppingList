import os
import logging
import sqlite3
import json
import configparser
from ingredient import Ingredient
from gui import load_all_recipe_files
# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
# Read configuration from config file
config = configparser.ConfigParser()
config.read('./config.cfg')

# Define the SQLite3 database file
db_file = 'recipes.db'

# Create a connection to the SQLite database (or create it if it doesn't exist)
conn = sqlite3.connect(db_file)
cursor = conn.cursor()
def create_tables():
    """Create the necessary tables in the SQLite database."""
    print("Creating tables in the database...")
    # Create a table for storing recipe information
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS recipes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ref TEXT NOT NULL UNIQUE,
                name TEXT NOT NULL,
                notes TEXT DEFAULT NULL
    )''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS ingredients (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    lemma TEXT DEFAULT NULL,
                    category TEXT DEFAULT NULL,
                    synonymes TEXT DEFAULT NULL)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS ingredient_entry (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                recipe_id INTEGER NOT NULL,
                ingredient_id INTEGER NOT NULL,
                amount REAL DEFAULT NULL,
                unit TEXT DEFAULT NULL,
                FOREIGN KEY (recipe_id) REFERENCES recipes (id),
                FOREIGN KEY (ingredient_id) REFERENCES ingredients (id)
    )''')
    # Create a table for storing menus
    cursor.execute('''CREATE TABLE IF NOT EXISTS menu(
                   id INTEGER PRIMARY KEY AUTOINCREMENT,
                   recipe_id INTEGER NOT NULL,
                   multiplier REAL DEFAULT 1.0,
                   FOREIGN KEY (recipe_id) REFERENCES recipes (id)
               )''')
    
    # Commit the table creation
    conn.commit()
    print("Tables created successfully.")

def insert_recipe(ref, name):
    """Insert a new recipe into the database."""
    print(f"Inserting recipe: {ref} - {name}")
    # Check if the recipe already exists
    cursor.execute('SELECT id FROM recipes WHERE ref = ?', (ref,))
    existing = cursor.fetchone()
    if existing:
        print(f"Recipe already exists: {ref} - {name}")
        return existing[0]
    cursor.execute('''
    INSERT INTO recipes (ref, name) VALUES (?, ?)
    ''', (ref, name))
    conn.commit()
    return cursor.lastrowid

def insert_ingredient(name, lemma=None, category=None, synonymes=None):
    """Insert a new ingredient into the database."""
    # print(f"Inserting ingredient: {name}")
    # Check if the ingredient already exists
    cursor.execute('SELECT id FROM ingredients WHERE name = ?', (name,))
    existing = cursor.fetchone()
    if existing:
        # print(f"Ingredient already exists: {name}")
        return existing[0]
    cursor.execute('''
    INSERT INTO ingredients (name, lemma, category, synonymes) VALUES (?, ?, ?, ?)
    ''', (name, lemma, category, synonymes))
    conn.commit()
    return cursor.execute('SELECT id FROM ingredients WHERE name = ?', (name,)).fetchone()[0]

def insert_ingredient_entry(recipe_id, ingredient_id, amount=None, unit=None):
    """Insert a new ingredient entry into the database."""
    # check if the recipe_id and ingredient_id exist
    cursor.execute('SELECT id FROM ingredient_entry WHERE recipe_id = ? AND ingredient_id = ?', (recipe_id, ingredient_id))
    existing = cursor.fetchone()
    if existing:
        print(f"Ingredient entry already exists: {recipe_id} - {ingredient_id}")
        return existing[0]
    cursor.execute('''
    INSERT INTO ingredient_entry (recipe_id, ingredient_id, amount, unit) VALUES (?, ?, ?, ?)
    ''', (recipe_id, ingredient_id, amount, unit))
    conn.commit()

def json2sqlite(location=config['DEFAULT']['RECIPES_DIR']):
    """Load all recipe files from the specified directory and insert them into the database."""
    for _root, _dirs, files in os.walk(location):
        for name in files:
            with open(os.path.join(location, name), 'r', encoding='utf-8') as recipe_file:
                recipe_dict = json.load(recipe_file)
                recipe_key = insert_recipe(ref=recipe_dict['ref'],
                              name=recipe_dict['name'])
                ingredients_bill = recipe_dict.get('ingredients_bill', [])
                for ingredient_entry in ingredients_bill:
                    ingredient_key = insert_ingredient(name=ingredient_entry['ingredient'])
                    insert_ingredient_entry(
                        recipe_id=recipe_key,
                        ingredient_id=ingredient_key,
                        amount=ingredient_entry.get('amount'),
                        unit=ingredient_entry.get('unit')
                    )
def reset_db():
    """Reset the database by dropping all tables."""
    cursor.execute('DELETE FROM recipes')
    cursor.execute('DELETE FROM ingredients')
    cursor.execute('DELETE FROM ingredient_entry')
    conn.commit()

    print("Database reset complete.")

def drop_tables():
    """Drop all tables in the database."""
    cursor.execute('ALTER TABLE ingredient_entry DROP CONSTRAINT recipe_id')
    cursor.execute('ALTER TABLE ingredient_entry DROP CONSTRAINT IF EXISTS ingredient_entry_ingredient_id_fkey')
    cursor.execute('DROP TABLE IF EXISTS recipes')
    cursor.execute('DROP TABLE IF EXISTS ingredients')
    cursor.execute('DROP TABLE IF EXISTS ingredient_entry')
    cursor.execute('DROP TABLE IF EXISTS menu')

def load_ingredients_from_file(filename):
    """Load ingredients from a JSON file and insert them into the database."""
    with open(filename, 'r', encoding='utf-16') as file:
        ingredient = json.load(file)
        insert_ingredient(
            name=ingredient['name'],
            lemma=ingredient.get('lemma'),
            category=ingredient.get('category'),
            synonymes=' '.join(ingredient.get('synonymes', []))
        )

def show_data():
    """Display the data in the database."""
    print("Recipes:")
    cursor.execute('SELECT * FROM recipes')
    for row in cursor.fetchall():
        print(row)

    # print("\nIngredients:")
    # cursor.execute('SELECT * FROM ingredients')
    # for row in cursor.fetchall():
    #     print(row)

    # print("\nIngredient Entries:")
    # cursor.execute('SELECT * FROM ingredient_entry')
    # for row in cursor.fetchall():
    #     print(row)

if __name__ == '__main__':
    create_tables()
    reset_db()
    all_recipes = load_all_recipe_files()
    logger.info('Total number of ingredients: %s', len(Ingredient.knowkn_ingredients_list))
    for recipe in all_recipes:
        recipe_key = insert_recipe(ref=recipe.ref, name=recipe.name)
        for entry in recipe.ingredients_bill:
            print(entry)
            ingredient_key = insert_ingredient(name=entry.ingredient.name,
                                               lemma=entry.ingredient.lemma,
                                               category=entry.ingredient.category,
                                               synonymes=' '.join(entry.ingredient.synonymes))
            insert_ingredient_entry(
                recipe_id=recipe_key,
                ingredient_id=ingredient_key,
                amount=entry.amount,
                unit=entry.unit
            )

    # for _root, _dirs, files in os.walk('./data/ingredient_files/'):
    #     for name in files:
    #         load_ingredients_from_file(os.path.join(_root, name))
    # json2sqlite(location='./test/test_results/')
    # Commit the changes and close the connection
    show_data()
    conn.commit()
    conn.close()
    print("Database setup complete.")
