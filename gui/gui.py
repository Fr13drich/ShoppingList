"""Generate a shopping list from a set of recipes"""
import logging
import json
import sqlite3
import configparser
import tkinter
import tkinter.filedialog
import customtkinter

DB_FILE = 'recipes.db'

# Create a connection to the SQLite database (or create it if it doesn't exist)
conn = sqlite3.connect(DB_FILE)
cursor = conn.cursor()
config = configparser.ConfigParser()
config.read('./config.cfg', encoding='utf-8')
logger = logging.getLogger(__name__)
logging.basicConfig(filename=config['DEFAULT']['LOG_FILE'], level=logging.DEBUG, encoding='utf-8')
print('Logfile: ' + config['DEFAULT']['LOG_FILE'])

# cursor.execute('SELECT ref, name FROM recipes')
# all_recipes = cursor.fetchall()
# print(all_recipes)
# logger.info('Total number of ingredients: %s', len(Ingredient.knowkn_ingredients_list))

class RecipeFrame(customtkinter.CTkFrame):
    """A grid of reipe combobox + ratio slider."""
    def __init__(self, master):
        super().__init__(master)
        values=[r[1] for r in master.all_recipes]
        values.sort()
        self.recipe_picker = customtkinter.CTkComboBox(self, values=values,\
                        width=200, hover=True, command=self.combobox_callback)
        self.recipe_picker.set('None')
        self.recipe_picker.bind()
        self.recipe_picker.grid(row=0, column=0, padx=10, pady=(10, 0))#, sticky="ew"
        self.ratio = customtkinter.CTkSlider(self, from_=0, to=1,\
                        number_of_steps=4, command=self.update_label)
        self.ratio.set(1)
        self.ratio.grid(row=1, column=0, padx=10, pady=(10, 0))
        self.ratio_label = customtkinter.CTkLabel(self, text='1')
        self.ratio_label.grid(row=1, column=1)

    def update_label(self, choice=None):
        """When the ratio slider is modified the ratio label is updated as well."""
        self.ratio_label.configure(text=str(choice))

    def combobox_callback(self, choice=None):
        self.master.generate_shopping_list()

class RecipesFrame(customtkinter.CTkFrame):
    """A grid of recipes combobox"""
    nb_of_combo = 9
    nb_of_week = 4
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.recipe_frame_list = []
        self.disable_button_list = []
        self.all_recipes = cursor.execute('SELECT ref, name FROM recipes').fetchall()
        # values=[r[1] for r in all_recipes]
        # values.sort()
        for j in range(RecipesFrame.nb_of_week):
            self.recipe_frame_list.append([])
            for i in range(RecipesFrame.nb_of_combo):
                recipe_frame = RecipeFrame(self)
                recipe_frame.grid(row=i, column=j, padx=10, pady=(10, 0))
                self.recipe_frame_list[j].append(recipe_frame)
            disable_button = customtkinter.CTkCheckBox(self, text='Disable')
            disable_button.deselect()
            disable_button.grid(row=RecipesFrame.nb_of_combo+1, column=j)
            self.disable_button_list.append(disable_button)
        self.save_button = customtkinter.CTkButton(self, text='Save', command=self.save_view)
        self.save_button.grid(row=RecipesFrame.nb_of_combo+2, column=0, padx=10, pady=(10, 0))
        self.load_button = customtkinter.CTkButton(self, text='Load', command=self.load_menu)
        self.load_button.grid(row=RecipesFrame.nb_of_combo+2, column=1, padx=10, pady=(10, 0))
        self.reset_button = customtkinter.CTkButton(self, text='Reset', command=self.reset_menu)
        self.reset_button.grid(row=RecipesFrame.nb_of_combo+2, column=2, padx=10, pady=(10, 0))
        self.view_picker = customtkinter.CTkComboBox(self, values=self.get_views(),
                                                     width=200, hover=True,
                                                     command=self.load_view)

        self.view_picker.grid(row=RecipesFrame.nb_of_combo+2, column=3, padx=20, pady=20, columnspan=2)
        # self.button = customtkinter.CTkButton(self, text="make shopping list",\
        #                                       command=self.generate_shopping_list)

    def get_views(self):
        """Return the list of all views in the database."""
        cursor.execute("SELECT name FROM sqlite_master WHERE type='view'")
        return [row[0] for row in cursor.fetchall()]

    def save_view(self, view_name='test_view'):
        """Save the current menu as a view in the database."""
        view_name = self.view_picker.get()
        
        if not view_name:
            return
        menu_list = []
        for j in range(RecipesFrame.nb_of_week):
            for pos, a in enumerate(self.recipe_frame_list[j]):
                menu_list.append({'name': a.recipe_picker.get(),
                                'ratio': a.ratio.get(),
                                'week': j,
                                'pos': pos}
                            )
        create_view_stmt = "CREATE VIEW " + view_name \
                            +  " (name, multiplier, week, pos) AS SELECT * FROM (VALUES"\
                            + ', '.join(['(' +  ', '.join(['"' + r['name'] + '"', str(r['ratio']),
                                                           str(r['week']), str(r['pos'])]) + ')'
                                                        for r in menu_list])\
                            + ')'
        print(create_view_stmt)
        cursor.execute('DROP VIEW IF EXISTS ' + view_name)
        cursor.execute(create_view_stmt)
        conn.commit()
        # update the view list
        self.view_picker.configure(values=self.get_views())

    def load_view(self, view_name=None):
        """Load a view from the database and populate the recipe frames."""
        view_name = self.view_picker.get()
        if not view_name:
            return
        cursor.execute('SELECT * FROM ' + view_name)
        recipe_list = cursor.fetchall()
        print(recipe_list)
        for recipe in recipe_list:
            self.recipe_frame_list[recipe[2]][recipe[3]]\
                .recipe_picker.set(recipe[0])
            self.recipe_frame_list[recipe[2]][recipe[3]]\
                .ratio.set(recipe[1])
        self.generate_shopping_list()

    def save_menu(self, filename=None):
        """Write a list of recipe along with their ratio on disk in json format."""
        if not filename:
            filename = tkinter.filedialog.asksaveasfile(mode='w', defaultextension=".json").name
        if not filename: # asksaveasfile return `None` if dialog closed with "cancel".
            return
        save_list = []
        with open(filename, 'w', encoding='utf-8') as outfile:
            for j in range(RecipesFrame.nb_of_week):
                save_list.append([(a.recipe_picker.get(), a.ratio.get())\
                                  for a in self.recipe_frame_list[j]])
            json.dump(save_list, outfile, indent=2, ensure_ascii=False)

    def load_menu(self, filename=None):
        """load a list of recipe name and ratio from a json file"""
        if not filename:
            filename = tkinter.filedialog.askopenfile(mode='r').name
        if not filename: # asksaveasfile return `None` if dialog closed with "cancel".
            return
        with open(filename, 'r', encoding='utf-8') as recipes_file:
            text = json.load(recipes_file)
            for j in range(RecipesFrame.nb_of_week):
                for i in range(RecipesFrame.nb_of_combo):
                    self.recipe_frame_list[j][i].recipe_picker.set(text[j][i][0])
                    self.recipe_frame_list[j][i].ratio.set(text[j][i][1])
                    self.recipe_frame_list[j][i].update_label(text[j][i][1])
        self.generate_shopping_list()
        

    def reset_menu(self):
        """Set all entries to a dummy empty recipe named 'None'."""
        for j in range(RecipesFrame.nb_of_week):
            for i in range(RecipesFrame.nb_of_combo):
                self.recipe_frame_list[j][i].recipe_picker.set('None')
        self.master.ingredients_frame.merged_ingredients.delete("0.0", "end")
    def insert_menu_item(self, recipe_ref, recipe_name, multiplier=1.0):
        """Insert a menu item into the database."""
        cursor.execute('SELECT id FROM recipes WHERE ref = ?', (recipe_ref,))
        recipe_id = cursor.fetchone()
        if recipe_id:
            cursor.execute('INSERT INTO menu (recipe_id, multiplier) VALUES (?, ?)',
                           (recipe_id[0], multiplier))
            conn.commit()
            logger.info('Inserted menu item: %s with multiplier %s', recipe_name, multiplier)
    def sql_merge(self):
        """Merge the ingredients and return the shopping list."""
        with open('./requests.sql', 'r', encoding='utf-8') as sql_file:
            cursor.execute(sql_file.read())
        logger.info('SQL merge completed')
        return cursor.fetchall()
    def generate_shopping_list(self):
        """Collect ant scale the recipes then display the shopping list"""
        #clean menu table
        cursor.execute('DELETE FROM menu')
        conn.commit()
        for j in range(RecipesFrame.nb_of_week):
            if self.disable_button_list[j].get():
                continue
            for i in range(RecipesFrame.nb_of_combo):
                for recipe in self.all_recipes:
                    if recipe[1] == self.recipe_frame_list[j][i].recipe_picker.get()\
                        and recipe[1] != 'None':
                        self.insert_menu_item(
                            recipe[0], recipe[1], self.recipe_frame_list[j][i].ratio.get())
                        break
        shopping_list = self.sql_merge()
        print(shopping_list)
        # total_ingredients_bill = menu.merge_ingredients()
        self.master.ingredients_frame.merged_ingredients.delete("0.0", "end")
        # Display the shopping list in the text box
        for bill_item in shopping_list:
            self.master.ingredients_frame.merged_ingredients.insert("end",
                str(bill_item[0]) + ' ' +
                str(bill_item[1]) + ' ' +
                str(bill_item[2]) + '\n')
        # previous_ingredient_lemma = ''
        # for bill_item in total_ingredients_bill:
        #     if bill_item.ingredient.lemma != previous_ingredient_lemma:
        #         self.master.ingredients_frame.merged_ingredients.insert\
        #             ("end", '\n' + str(bill_item))
        #     else:
        #         self.master.ingredients_frame.merged_ingredients.insert\
        #             ("end", ' ' + str(bill_item.amount) + ' ' +str(bill_item.unit))
        #     previous_ingredient_lemma = bill_item.ingredient.lemma

class IngredientsFrame(customtkinter.CTkFrame):
    """Frame for the text box that display the shopping list."""
    def __init__(self, master):
        super().__init__(master)
        self.merged_ingredients = customtkinter.CTkTextbox(self, width=400,\
                                        height=800, activate_scrollbars=True)
        self.merged_ingredients.grid(row=0, column=0, rowspan=6, columnspan=2, sticky="e")

class FilterFrame(customtkinter.CTkFrame):
    """Frame for the filter combobox."""
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.ing_filter = customtkinter.CTkComboBox(self, values=self.fetch_ingredients(),\
                                    width=200, hover=True, command=self.combobox_callback,)
        self.ing_filter.set('')
        self.ing_filter.bind('<<ComboboxSelected>>',
                             lambda event: self.combobox_callback(self.ing_filter.get()))
        self.ing_filter.bind('<Return>',
                             lambda event: self.combobox_callback(self.ing_filter.get()))
        self.ing_filter.bind('<FocusOut>',
                             lambda event: self.combobox_callback(self.ing_filter.get()))
        self.ing_filter_label = customtkinter.CTkLabel(self, text="Filter by ingredient:")
        self.ing_filter_label.grid(row=0, column=0, padx=10, pady=(10, 0), sticky="nw")
        self.ing_filter.grid(row=0, column=1, padx=10, pady=(10, 0), sticky="ne")

    def combobox_callback(self, choice=''):
        """Filter the recipes based on the selected ingredient."""
        with open('./ing_filter.sql', 'r', encoding='utf-8') as ing_filter:
            sql_query = ing_filter.read()
        cursor.execute(sql_query, ('%' + choice + '%',))
        filtered_recipe = ['None'] + [r[0] for r in cursor.fetchall()]
        print(filtered_recipe)
        for sub_list_frame in self.master.recipes_frame.recipe_frame_list:
            for recipe_frame in sub_list_frame:
                recipe_frame.recipe_picker.configure(values=filtered_recipe)

    def fetch_ingredients(self):
        """Fetch the ingredients from the database and return them as a list."""
        cursor.execute('SELECT DISTINCT name FROM ingredients ORDER BY name')
        ingredients = cursor.fetchall()
        return [ing[0] for ing in ingredients] + ['']

class App(customtkinter.CTk):
    """Main classe. Contains a grid of recipes, a text zone and some buttons."""
    def __init__(self):
        super().__init__()
        self.title("Shopping list")
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.geometry("1600x1200")
        self.grid_columnconfigure((0, 1), weight=1)
        self.filter_frame = FilterFrame(self)
        self.filter_frame.grid(row=0, column=0)
        self.recipes_frame = RecipesFrame(self)
        self.recipes_frame.grid(row=1, column=0, padx=10, pady=(10, 0), sticky="nsw")
        self.ingredients_frame = IngredientsFrame(self)
        self.ingredients_frame.grid(row=0, column=1, rowspan=2, padx=10, pady=(10, 0), sticky="e")
    
    def on_closing(self):
        conn.close()
        self.destroy()


if __name__ == '__main__':
    app = App()
    app.mainloop()
