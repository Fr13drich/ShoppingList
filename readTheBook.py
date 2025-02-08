"""Extract ingredients bills from my cooking book"""
import os
import json
from classes import Recipe
from book import Reader

def parse_ingredients(raw_list_of_ingredients: list):
    """Return a dict(name, amount)"""
    result = {}
    for item in raw_list_of_ingredients:
        # print(item)
        splitted_item = str(item).split(maxsplit=1)
        if str(splitted_item[0]).isnumeric():
            amount = int(splitted_item[0])
            name = str(splitted_item[1]).lower()
        else:
            amount = 1
            name = str(item).lower()
        result.update({name: amount})
    return result


# def choose_strategy(location):
#     if location[2:4] == 'CG':
#         return read_1_CGbook_recipe
#     elif location[2:4] == 'BC':
#         return read_1_BCbook_recipe
#     elif location[2:4] == 'EB':
#         return read_1_EBbook_recipe
#     else:
#         return None

def pics2json(location):
    # strategy = choose_strategy(location)
    for _root, _dirs, files in os.walk(location):
        for name in files:
            print('Reading ' + str(name) + 'from' + location)
            ref, name, ingredients = Reader.parse(location, name)
            parsed_ingredients = parse_ingredients(ingredients)
            outfile = 'json/' + ref + '.json'
            print(str(ref) + ', ' + str(name))
            print(parsed_ingredients)
            if os.path.exists(outfile):
                if input(outfile + " already exists. Should I overwrite?: ") != 'y':
                    continue
            with open(outfile, 'w', encoding='utf-16') as outfile:
                json.dump({'ref': ref, 'name':name, 'ingredients':parsed_ingredients}, outfile, indent=2, ensure_ascii=False)


pics2json('./BCrecipesPics/')
# pics2json('./EBrecipesPics/')
