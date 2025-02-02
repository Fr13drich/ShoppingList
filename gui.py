import tkinter
import tkinter.messagebox
import tkinter.filedialog
import customtkinter
import json
from operator import itemgetter
import load
from classes import Recipe, Menu

all_recipes = load.load_all_recipe_files()
    # for recipe in all_recipes:
    #     if recipe.name == choice:
    #         for ingredient, ingredient_bill, unit in recipe.ingredients:
    #             app.ingredients_frame.ingredients_list.insert("0.0",  ingredient.name + str(ingredient_bill) + unit + '\n')
    #         break

class RecipeFrame(customtkinter.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        values=[r.name for r in all_recipes]
        values.sort()
        self.recipe_picker = customtkinter.CTkComboBox(self, values=values, width=200, command=self.combobox_callback)
        self.recipe_picker.set('None')
        self.recipe_picker.grid(row=0, column=0, padx=10, pady=(10, 0))#, sticky="ew"
        self.ratio = customtkinter.CTkSlider(self, from_=0, to=1, number_of_steps=4, command=self.update_label)
        self.ratio.set(1)
        self.ratio.grid(row=1, column=0, padx=10, pady=(10, 0))
        self.ratio_label = customtkinter.CTkLabel(self, text='1')
        self.ratio_label.grid(row=1, column=1)

    def update_label(self, choice=None):
        self.ratio_label.configure(text=str(choice))

    def combobox_callback(self, choice=None):
        pass
                

class RecipesFrame(customtkinter.CTkFrame):
    nb_of_combo = 9
    nb_of_week = 4
    def __init__(self, master):
        super().__init__(master)
        # super().__init__(parent)
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
        # self.ingredients_list = customtkinter.CTkTextbox(self, width=400, height=800, activate_scrollbars=True)
        # self.ingredients_list.grid(row=0, column=5, sticky="e", rowspan=10)
        self.save_button = customtkinter.CTkButton(self, text='Save', command=self.save_menu)
        self.save_button.grid(row=RecipesFrame.nb_of_combo+2, column=0, padx=10, pady=(10, 0))
        self.load_button = customtkinter.CTkButton(self, text='Load', command=self.load_menu)
        self.load_button.grid(row=RecipesFrame.nb_of_combo+2, column=1, padx=10, pady=(10, 0))
        self.reset_button = customtkinter.CTkButton(self, text='Reset', command=self.reset_menu)
        self.reset_button.grid(row=RecipesFrame.nb_of_combo+2, column=2, padx=10, pady=(10, 0))
        # self.merge_button = customtkinter.CTkButton(self, text='Merge', command=self.merge_ingredients)
        # self.merge_button.grid(row=7, column=3, padx=10, pady=(10, 0))


    def save_menu(self):
        f = tkinter.filedialog.asksaveasfile(mode='w', defaultextension=".json", )
        if f is None: # asksaveasfile return `None` if dialog closed with "cancel".
            return
        save_list = []
        with open(f.name, 'w', encoding='utf-16') as outfile:
            for j in range(RecipesFrame.nb_of_week):
                save_list.append([(a.recipe_picker.get(), a.ratio.get()) for a in self.recipe_frame_list[j]])
            json.dump(save_list, outfile, indent=2, ensure_ascii=False)


    def load_menu(self):
        f = tkinter.filedialog.askopenfile(mode='r')
        if f is None: # asksaveasfile return `None` if dialog closed with "cancel".
            return
        with open(f.name, 'r', encoding='utf-16') as recipes_file:
            text = json.load(recipes_file)
            for j in range(RecipesFrame.nb_of_week):
                for i in range(RecipesFrame.nb_of_combo):
                    # print(i,j)
                    self.recipe_frame_list[j][i].recipe_picker.set(text[j][i][0])
                    self.recipe_frame_list[j][i].ratio.set(text[j][i][1])
                    self.recipe_frame_list[j][i].update_label(text[j][i][1])

    def reset_menu(self):
        for j in range(RecipesFrame.nb_of_week):
            for i in range(RecipesFrame.nb_of_combo):
                self.recipe_frame_list[j][i].recipe_picker.set('None')
        self.ingredients_list.delete("0.0", "end")
    
    # def merge_ingredients(self):
    #     self.ingredients_list.delete("0.0", "end")
    #     menu = Menu('Hiver')
    #     for j in range(RecipesFrame.nb_of_week):
    #         for i in range(RecipesFrame.nb_of_combo):
    #             for recipe in all_recipes:
    #                 if recipe.name == self.recipe_frame_list[j][i].recipe_picker.get():
    #                     menu.add_recipe(recipe, self.recipe_frame_list[j][i].ratio.get())
    #                     print(recipe.ref + ': ' + recipe.name)
    #                     break
        
    #     shopping_list = menu.merge_ingredients()
    #     a = ''
    #     for name, amounts in dict(sorted(shopping_list.items(), key=itemgetter(0))).items():
    #         a += name + ':\t'
    #         for amount in amounts.items():
    #             a += str(amount[1]) + ' ' + amount[0] + '\t'
    #         a += '\n'
    #     self.ingredients_list.insert("0.0", a)

class IngredientsFrame(customtkinter.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.merged_ingredients = customtkinter.CTkTextbox(self, width=500, height=700, activate_scrollbars=True)
        self.merged_ingredients.grid(rowspan=6, columnspan=2)


class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        self.title("Shopping list")
        self.geometry("1600x1200")
        # self.grid_columnconfigure((0, 1), weight=1)
        self.recipes_frame = RecipesFrame(self)
        self.recipes_frame.grid(row=0, column=0, padx=10, pady=(10, 0), sticky="nswe")
        self.ingredients_frame = IngredientsFrame(self)
        self.ingredients_frame.grid(row=0, column=1, padx=10, pady=(10, 0), sticky="nswe")
        self.button = customtkinter.CTkButton(self, text="make shopping list", command=self.button_callback)
        self.button.grid(row=1, column=0, padx=20, pady=20, columnspan=2)
        
        # self.checkbox_1 = customtkinter.CTkCheckBox(self, text="checkbox 1")
        # self.checkbox_1.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="w")
        # self.checkbox_2 = customtkinter.CTkCheckBox(self, text="checkbox 2")
        # self.checkbox_2.grid(row=1, column=1, padx=20, pady=(0, 20), sticky="w")
        
    def button_callback(self):
        menu = Menu('Hiver')
        for j in range(RecipesFrame.nb_of_week):
            if self.recipes_frame.disable_button_list[j].get():
                continue
            for i in range(RecipesFrame.nb_of_combo):
                for recipe in all_recipes:
                    if recipe.name == self.recipes_frame.recipe_frame_list[j][i].recipe_picker.get():
                        menu.add_recipe(recipe, self.recipes_frame.recipe_frame_list[j][i].ratio.get())
                        print(recipe.ref + ': ' + recipe.name)
                        break
        shopping_list = menu.merge_ingredients()
        text = ''
        for name, amounts in dict(sorted(shopping_list.items(), key=itemgetter(0))).items():
            text += name + ':\t'
            for amount in amounts.items():
                text += str(amount[1]) + ' ' + amount[0] + '\t'
            text += '\n'
        self.ingredients_frame.merged_ingredients.delete("0.0", "end")
        self.ingredients_frame.merged_ingredients.insert("0.0", text)


app = App()
app.mainloop()
