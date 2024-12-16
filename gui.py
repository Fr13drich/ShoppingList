import customtkinter

def combobox_callback(choice):
    print("combobox dropdown clicked:", choice)
    app.ingredients_frame.ingredients_list.insert("0.0", choice)

class RecipesFrame(customtkinter.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.recipe_picker_1 = customtkinter.CTkComboBox(self, values=["option 1", "option 2"], command=combobox_callback)
        self.recipe_picker_1.grid(row=0, column=0, padx=10, pady=(10, 0), sticky="w")

class IngredientsFrame(customtkinter.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.ingredients_list = customtkinter.CTkTextbox(self)
        self.ingredients_list.grid(row=0, column=0, sticky="nsew")
        self.ingredients_list.insert("0.0", "new text to insert")

class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        self.title("Shopping list")
        self.geometry("800x300")
        self.grid_columnconfigure((0, 1), weight=1)
        self.recipes_frame = RecipesFrame(self)
        self.recipes_frame.grid(row=0, column=0, padx=10, pady=(10, 0), sticky="nsw")
        self.ingredients_frame = IngredientsFrame(self)
        self.ingredients_frame.grid(row=0, column=1, padx=10, pady=(10, 0), sticky="nsw")


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
