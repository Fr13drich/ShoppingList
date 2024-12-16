import json
from classes import Recipe, Menu

menu_porc = ['BCp710', 'BCp398', 'BCp336', 'BCp108', 'BCp117', 'BCp94'] # bcp de pdt et gaspillage de lait (ajouter des crepes???)
menu_boeuf = ['BCp117', 'BCp202', 'BCp156', 'BCp158', 'BCp538', 'BCp336']
# m = ['BCp710', 'BCp398', 'BCp94']
recipe_list = []
for item in menu_boeuf:
    with open('json/' + item + '.json', 'r', encoding='utf-16') as outfile:
        recipe_dict = json.load(outfile)
        # print(recipe_dict)
        recipe_list.append(Recipe(item, recipe_dict['name'], recipe_dict['ingredients']))

# print(recipe_list)
a = Menu('Hiver', recipe_list)
t = a.merge_ingredients()
print('shopping list: ')
for item in t.items():
    print(item[0] + ': ' + str(item[1]))

