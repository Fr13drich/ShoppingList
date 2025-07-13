"""Generate a shopping list from a set of recipes"""
import logging
import json
import configparser
import tkinter
import tkinter.messagebox
import tkinter.filedialog
import customtkinter
import load
from recipe import Menu
from ingredient import Ingredient

config = configparser.ConfigParser()
config.read('./config.cfg')
logger = logging.getLogger(__name__)
logging.basicConfig(filename=config['DEFAULT']['LOG_FILE'], level=logging.INFO, encoding='utf-8')
print('Logfile: ' + config['DEFAULT']['LOG_FILE'])

# load.load_all_ingredient_files()
all_recipes = load.load_all_recipe_files()
logger.info('Total number of ingredients: %s', len(Ingredient.knowkn_ingredients_list))

class RecipeFrame(customtkinter.CTkFrame):
    """A grid of reipe combobox + ratio slider."""
    def __init__(self, master):
        super().__init__(master)
        values=[r.name for r in all_recipes]
        values.sort()
        self.recipe_picker = customtkinter.CTkComboBox(self, values=values,\
                        width=200, hover=True, command=self.combobox_callback)
        self.recipe_picker.set('None')
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
        """Can be used one day to replace the 'make shopping list button."""
        # pass

class RecipesFrame(customtkinter.CTkFrame):
    """A grid of recipes combobox"""
    nb_of_combo = 9
    nb_of_week = 4
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.recipe_frame_list = []
        self.disable_button_list = []
        values=[r.name for r in all_recipes]
        values.sort()
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
        self.save_button = customtkinter.CTkButton(self, text='Save', command=self.save_menu)
        self.save_button.grid(row=RecipesFrame.nb_of_combo+2, column=0, padx=10, pady=(10, 0))
        self.load_button = customtkinter.CTkButton(self, text='Load', command=self.load_menu)
        self.load_button.grid(row=RecipesFrame.nb_of_combo+2, column=1, padx=10, pady=(10, 0))
        self.reset_button = customtkinter.CTkButton(self, text='Reset', command=self.reset_menu)
        self.reset_button.grid(row=RecipesFrame.nb_of_combo+2, column=2, padx=10, pady=(10, 0))
        self.button = customtkinter.CTkButton(self, text="make shopping list",\
                                              command=self.generate_shopping_list)
        self.button.grid(row=RecipesFrame.nb_of_combo+2, column=3, padx=20, pady=20, columnspan=2)

    def save_menu(self):
        """Write a list of recipe along with their ratio on disk in json format."""
        f = tkinter.filedialog.asksaveasfile(mode='w', defaultextension=".json", )
        if f is None: # asksaveasfile return `None` if dialog closed with "cancel".
            return
        save_list = []
        with open(f.name, 'w', encoding='utf-16') as outfile:
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
        with open(filename, 'r', encoding='utf-16') as recipes_file:
            text = json.load(recipes_file)
            for j in range(RecipesFrame.nb_of_week):
                for i in range(RecipesFrame.nb_of_combo):
                    self.recipe_frame_list[j][i].recipe_picker.set(text[j][i][0])
                    self.recipe_frame_list[j][i].ratio.set(text[j][i][1])
                    self.recipe_frame_list[j][i].update_label(text[j][i][1])

    def reset_menu(self):
        """Set all entries to a dummy empty recipe named 'None'."""
        for j in range(RecipesFrame.nb_of_week):
            for i in range(RecipesFrame.nb_of_combo):
                self.recipe_frame_list[j][i].recipe_picker.set('None')
        self.master.ingredients_frame.merged_ingredients.delete("0.0", "end")

    def generate_shopping_list(self):
        """Collect ant scale the recipes then display the shopping list"""
        menu = Menu('Hiver')
        for j in range(RecipesFrame.nb_of_week):
            if self.disable_button_list[j].get():
                continue
            for i in range(RecipesFrame.nb_of_combo):
                for recipe in all_recipes:
                    if recipe.name == self.recipe_frame_list[j][i].recipe_picker.get()\
                        and recipe.name != 'None':
                        menu.add_recipe(recipe, self.recipe_frame_list[j][i].ratio.get())
                        # print(recipe)
                        break
        total_ingredients_bill = menu.merge_ingredients()
        self.master.ingredients_frame.merged_ingredients.delete("0.0", "end")
        previous_ingredient_lemma = ''
        for bill_item in total_ingredients_bill:
            if bill_item.ingredient.lemma != previous_ingredient_lemma:
                self.master.ingredients_frame.merged_ingredients.insert\
                    ("end", '\n' + str(bill_item))
            else:
                self.master.ingredients_frame.merged_ingredients.insert\
                    ("end", ' ' + str(bill_item.amount) + ' ' +str(bill_item.unit))
            previous_ingredient_lemma = bill_item.ingredient.lemma

class IngredientsFrame(customtkinter.CTkFrame):
    """Frame for the text box that display the shopping list."""
    def __init__(self, master):
        super().__init__(master)
        self.merged_ingredients = customtkinter.CTkTextbox(self, width=400,\
                                        height=800, activate_scrollbars=True)
        self.merged_ingredients.grid(row=0, column=0, rowspan=6, columnspan=2, sticky="e")

class App(customtkinter.CTk):
    """Main classe. Contains a grid of recipes, a text zone and some buttons."""
    def __init__(self):
        super().__init__()
        self.title("Shopping list")
        self.geometry("1600x1200")
        self.grid_columnconfigure((0, 1), weight=1)
        self.recipes_frame = RecipesFrame(self)
        self.recipes_frame.grid(row=0, column=0, padx=10, pady=(10, 0), sticky="nsw")
        self.ingredients_frame = IngredientsFrame(self)
        self.ingredients_frame.grid(row=0, column=1, padx=10, pady=(10, 0), sticky="e")

app = App()
if __name__ == '__main__':
    app.mainloop()
