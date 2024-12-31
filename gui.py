import tkinter
import tkinter.messagebox
import tkinter.filedialog
import customtkinter
from operator import itemgetter
import load
from classes import Recipe, Menu

all_recipes = load.load_all_recipe_files()


    # for recipe in all_recipes:
    #     if recipe.name == choice:
    #         for ingredient, ingredient_bill, unit in recipe.ingredients:
    #             app.ingredients_frame.ingredients_list.insert("0.0",  ingredient.name + str(ingredient_bill) + unit + '\n')
    #         break

class RecipesFrame(customtkinter.CTkFrame):
    nb_of_combo = 7
    def __init__(self, master):
        super().__init__(master)
        # super().__init__(parent)
        self.recipe_picker_list = []
        for i in range(RecipesFrame.nb_of_combo):
            recipe_picker = customtkinter.CTkComboBox(self, values=[r.name for r in all_recipes], width=300, command=self.combobox_callback)
            recipe_picker.set('None')
            recipe_picker.grid(row=i, column=0, padx=10, pady=(10, 0), sticky="ew")
            self.recipe_picker_list.append(recipe_picker)
        self.save_button = customtkinter.CTkButton(self, text='Save', command=self.save_menu)
        self.save_button.grid(column=0, padx=10, pady=(10, 0), sticky="s")
        self.load_button = customtkinter.CTkButton(self, text='Load', command=self.load_menu)
        self.load_button.grid(column=0, padx=10, pady=(10, 0), sticky="s")
        self.ingredients_list = customtkinter.CTkTextbox(self, width=600, height=800, activate_scrollbars=True)
        self.ingredients_list.grid(row=0, column=2, sticky="e", rowspan=10)
        
        # self.recipe_picker_1 = customtkinter.CTkComboBox(self, values=[r.name for r in all_recipes], command=combobox_callback)
        # self.recipe_picker_1.grid(row=0, padx=10, pady=(10, 0), sticky="ew")
        # self.recipe_picker_2 = customtkinter.CTkComboBox(self, values=[r.name for r in all_recipes], command=combobox_callback)
        # self.recipe_picker_2.grid(row=1, padx=10, pady=(10, 0), sticky="ew")
    def combobox_callback(self, choice=None):
        self.ingredients_list.delete("0.0", "end")
        recipe_list = []
        for picked_recipe in self.recipe_picker_list:
            # print(picked_recipe)
            for recipe in all_recipes:
                if recipe.name == picked_recipe.get():
                    recipe_list.append(recipe)
                    print(recipe.ref + ': ' + recipe.name)
                    break
        menu = Menu('Hiver', recipe_list)
        shopping_list = menu.merge_ingredients()
        a = ''
        for name, amounts in dict(sorted(shopping_list.items(), key=itemgetter(0))).items():
            a += name + ':\t'
            for amount in amounts.items():
                a += str(amount[1]) + ' ' + amount[0] + '\t'
            a += '\n'
        self.ingredients_list.insert("0.0", a)

    def save_menu(self):
        f = tkinter.filedialog.asksaveasfile(mode='w', defaultextension=".txt")
        if f is None: # asksaveasfile return `None` if dialog closed with "cancel".
            return
        text2save = [a.get() for a in self.recipe_picker_list]
        f.write(str(text2save))
        f.close()

    def load_menu(self):
        f = tkinter.filedialog.askopenfile(mode='r')
        if f is None: # asksaveasfile return `None` if dialog closed with "cancel".
            return
        recipes = []
        recipes = f.read()[1:-1]
        print(type(recipes))
        print(recipes)
        # text2save = [a.get() for a in self.recipe_picker_list]
        # self.recipe_picker_list = map(customtkinter.CTkComboBox.set, list(f))
        # self.recipe_picker_list = [customtkinter.CTkComboBox.set(a) for a in list(f.read())]
        for i in range(RecipesFrame.nb_of_combo):
            self.recipe_picker_list[i].set(recipes.split(sep=', ')[i][1:-1])

        self.combobox_callback()

class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        self.title("Shopping list")
        self.geometry("800x800")
        # self.grid_columnconfigure((0, 1), weight=1)
        recipes_frame = RecipesFrame(self)
        recipes_frame.grid(row=0, column=0, padx=10, pady=(10, 0), sticky="nswe")
        # self.ingredients_frame = IngredientsFrame(self)
        # self.ingredients_frame.grid(row=0, column=1, padx=10, pady=(10, 0), sticky="nswe")
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
