import customtkinter
from operator import itemgetter
import load
from classes import Recipe, Menu

all_recipes = load.load_all_recipe_files()

def combobox_callback(choice):
    app.ingredients_frame.ingredients_list.delete("0.0", "end")
    recipe_list = []
    for picked_recipe in app.recipes_frame.recipe_picker_list:
        print(picked_recipe)
        for recipe in all_recipes:
            if recipe.name == picked_recipe.get():
                recipe_list.append(recipe)
                break
    menu = Menu('Hiver', recipe_list)
    shopping_list = menu.merge_ingredients()
    a = ''
    for name, amount in dict(sorted(shopping_list.items(), key=itemgetter(0))).items():
        a += name + ':\t' + str(amount[0]) + ' ' + str(amount[1]) + '\n'
    app.ingredients_frame.ingredients_list.insert("0.0", a)

    # for recipe in all_recipes:
    #     if recipe.name == choice:
    #         for ingredient, ingredient_bill, unit in recipe.ingredients:
    #             app.ingredients_frame.ingredients_list.insert("0.0",  ingredient.name + str(ingredient_bill) + unit + '\n')
    #         break

class RecipesFrame(customtkinter.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.recipe_picker_list = []
        for i in range(5):
            recipe_picker = customtkinter.CTkComboBox(self, values=[r.name for r in all_recipes], command=combobox_callback)
            recipe_picker.set('None')
            recipe_picker.grid(row=i, padx=10, pady=(10, 0), sticky="ew")
            self.recipe_picker_list.append(recipe_picker)
        # self.recipe_picker_1 = customtkinter.CTkComboBox(self, values=[r.name for r in all_recipes], command=combobox_callback)
        # self.recipe_picker_1.grid(row=0, padx=10, pady=(10, 0), sticky="ew")

        # self.recipe_picker_2 = customtkinter.CTkComboBox(self, values=[r.name for r in all_recipes], command=combobox_callback)
        # self.recipe_picker_2.grid(row=1, padx=10, pady=(10, 0), sticky="ew")

class IngredientsFrame(customtkinter.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.ingredients_list = customtkinter.CTkTextbox(self, width=400, height=600)
        self.ingredients_list.grid(sticky="nsew")

class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        self.title("Shopping list")
        self.geometry("800x600")
        # self.grid_columnconfigure((0, 1), weight=1)
        self.recipes_frame = RecipesFrame(self)
        self.recipes_frame.grid(row=0, column=0, padx=10, pady=(10, 0), sticky="nswe")
        self.ingredients_frame = IngredientsFrame(self)
        self.ingredients_frame.grid(row=0, column=1, padx=10, pady=(10, 0), sticky="nswe")


        # self.button = customtkinter.CTkButton(self, text="my button", command=self.button_callback)
        # self.button.grid(row=0, column=0, padx=20, pady=20, sticky="ew", columnspan=2)
        # self.checkbox_1 = customtkinter.CTkCheckBox(self, text="checkbox 1")
        # self.checkbox_1.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="w")
        # self.checkbox_2 = customtkinter.CTkCheckBox(self, text="checkbox 2")
        # self.checkbox_2.grid(row=1, column=1, padx=20, pady=(0, 20), sticky="w")
        
    def button_callback(self):
        print("button pressed")

app = App()
app.mainloop()
