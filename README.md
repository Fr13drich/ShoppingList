
# ShoppingList

ShoppingList is a tool to extract recipes and their ingredients from scanned images of cooking books, parse them using NLP, and output structured data. It also provides a GUI and a web interface to create and manage grocery lists from recipes.

## Features
- Extract recipes and ingredients from scanned images (OCR + NLP)
- Parse and structure ingredient lists
- Automatically create and update ingredient files
- Generate grocery/shopping lists from selected recipes
- GUI and web interface for editing and managing recipes

## Requirements
- Python 3.8+
- Install dependencies:
  ```sh
  pip install -r requirements.txt
  python -m spacy download fr_core_news_md
  # For web interface:
  pip install fastapi uvicorn
  ```

## Usage

### 1. Extract Recipes from Images (CLI)

Run the main script to extract recipes from images:

```sh
python read_the_book.py --input_dir ./data/pics/BCrecipesPics/ --output_dir ./data/recipe_files/
```

This will scan images, parse recipes, and write structured output to the `recipe_files` directory. New ingredient files are created as needed in `ingredient_files`.

### 2. GUI for Grocery List

Run the GUI to create a grocery list from a list of recipes:

```sh
python gui/run_gui.py
```

### 3. Web App for Recipe Editing

Run the FastAPI web app for recipe editing:

```sh
python webapp/recipe_editor.py
```
Then open your browser at [http://localhost:8000](http://localhost:8000)

## File Structure

- `read_the_book.py` — Main script for extracting recipes from images
- `recipe/` — Recipe and menu classes
- `ingredient/` — Ingredient classes and utilities
- `gui/` — GUI code for shopping list creation
- `webapp/` — FastAPI web app for recipe editing
- `data/` — Contains images, ingredient files, and recipe files
- `config.cfg` — Configuration file

## Output
- Recipes and their ingredient bills are written to `./data/recipe_files/`.
- Ingredient files are created/updated in `./data/ingredient_files/`.
- Each ingredient file references the recipes it appears in.

## Testing
Test scripts are available in the `test/` directory to validate OCR and parsing results.

## License
MIT License
       