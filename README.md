# ShoppingList

./readTheBook.py
    Scan (OCR) pictures from cooking books. Then user NLP into structured ingredients bill in json format.
       The pictures are read from the ./data/pics folder.
       The name of the recipe and its ingredients bill are written in ./data./recipe_files).
    Create new ingredient files on the fly if needed.
    Add a reference to the recipe in the ingredients files (./data/ingredients_files).

./gui.py
    Create a grocery list from a list of recipes.
       