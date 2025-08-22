"""tk recipe editor"""
import tkinter
import tkinter.messagebox
import tkinter.filedialog
import customtkinter

from recipe import Recipe
from reader import parser


class InputFrame(customtkinter.CTkFrame):
    """Frame representing a single recipe."""
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        self.recipe_name_label = customtkinter.CTkLabel(self, text="Recipe Name:")
        self.recipe_name = customtkinter.CTkEntry(self)
        self.recipe_ref_label = customtkinter.CTkLabel(self, text="Recipe Reference:")
        self.recipe_ref = customtkinter.CTkEntry(self)
        self.ingredients = customtkinter.CTkTextbox(self, height=400, width=200)
        self.recipe_name_label.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        self.recipe_name.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        self.recipe_ref_label.grid(row=1, column=0, padx=5, pady=5, sticky="ew")
        self.recipe_ref.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        self.ingredients.grid(row=2, column=0, padx=5, pady=5, columnspan=2, sticky="nsew")

class OutputFrame(customtkinter.CTkFrame):
    """Frame displaying the parsed recipe."""
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        self.parsed_recipe = customtkinter.CTkTextbox(self, height=500, width=200)
        self.parsed_recipe.pack()


class ButtonFrame(customtkinter.CTkFrame):
    """Frame containing buttons for the application."""
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        self.save_button = customtkinter.CTkButton(self, text="Save Recipe",
                                                   command=self.master.save_recipe)
        self.save_button.grid(row=0, column=0, padx=5, pady=5)
        self.load_button = customtkinter.CTkButton(self, text="Load Recipe")
        self.load_button.grid(row=0, column=1, padx=5, pady=5)
        self.parse_button = customtkinter.CTkButton(self, text="Parse Recipe",
                                                    command=self.master.create_recipe)
        self.parse_button.grid(row=0, column=2, padx=5, pady=5)

class App(customtkinter.CTk):
    """Main application class for the recipe editor."""
    def __init__(self):
        super().__init__()
        self.title("Recipe Editor")
        self.geometry("600x800")
        self.grid_columnconfigure((0, 1), weight=1)
        self.input_frame = InputFrame(self)
        self.input_frame.grid(row=0, column=0, sticky="nsew")
        self.output_frame = OutputFrame(self)
        self.output_frame.grid(row=0, column=1, sticky="nsew")
        self.button_frame = ButtonFrame(self)
        self.button_frame.grid(row=1, column=0, columnspan=2, sticky="ew")

    def create_recipe(self):
        """Create a recipe from the input fields."""
        recipe_name = self.input_frame.recipe_name.get()
        recipe_ref = self.input_frame.recipe_ref.get()
        ingredients = self.input_frame.ingredients.get("1.0", "end-1c").splitlines()
        # Here you would typically call a function to process the recipe
        recipe = Recipe(ref=recipe_ref, name=recipe_name,
                    ingredients_bill=parser.parse_ingredients_bill_dict(
                        ingredients_bill_dict=parser.parse_ingredients(ingredients),
                        recipe_ref=recipe_ref)
        )
        print(f"Creating recipe: {recipe_name}")
        print(f"Ingredients:\n{ingredients}")
        print(f"Recipe created successfully: {recipe}")

    def save_recipe(self):
        """Save the recipe to a file."""
        recipe_name = self.input_frame.recipe_name.get()
        recipe_ref = self.input_frame.recipe_ref.get()
        ingredients = self.input_frame.ingredients.get("1.0", "end-1c").splitlines()
        recipe = Recipe(ref=recipe_ref, name=recipe_name,
                    ingredients_bill=parser.parse_ingredients_bill_dict(
                        ingredients_bill_dict=parser.parse_ingredients(ingredients),
                        recipe_ref=recipe_ref)
        )

        # filename = tkinter.filedialog.asksaveasfile(mode='w', defaultextension=".json").name
        # if not filename: # asksaveasfile return `None` if dialog closed with "cancel".
        #     return
        recipe.write_recipe_file()
        tkinter.messagebox.showinfo("Success", f"Recipe '{recipe_name}' saved successfully.")

if __name__ == '__main__':
    app = App()
    app.mainloop()
