"""Build a tree."""
import json
import configparser
import spacy
config = configparser.ConfigParser()
config.read('./config.cfg')
nlp = spacy.load("fr_core_news_md")

def load_morphology(file=config['DEFAULT']['INGREDIENT_BILL_MORPHOLOGY_FILE']):
    with open(file, 'r', encoding='utf-8', ) as morphology_file:
        return json.load(morphology_file)

def build_tree():
    shape = load_morphology()
    root = cursor = dict()
    for k, v in shape.items():
        cursor = root
        tokens = str(k).split()
        for token in tokens:
            if not cursor.get(token):
                cursor[token] = dict()
            cursor = cursor[token]
        cursor['strategy'] = v
    print(root)

    with open(file='./parse_tree.json', mode='w', encoding='utf-16') as f:
        json.dump(root, f, indent=2)

def parse_stream(ingredient_stream: str):
    """Split a str containing potentialy multiple ingredients
       Return a list of str
       '1 pincée de sel, 1 pincée de poivre' returns ['1 pincée de sel', '1 pincée de poivre']
    """
    with open(file='./parse_tree.json', mode='r', encoding='utf-16', ) as strategy_dict:
        root = json.load(strategy_dict)
    doc = nlp(ingredient_stream)
    ingredient_list = []
    cursor = root
    i = j = 0
    strategy = ingredient_str = None
    # print(ingredient_stream)
    # print([token.pos_ for token in doc])
    for token in doc:
        print(token.pos_)
        if cursor.get('strategy'):
            strategy = cursor['strategy']
            # print(f'potential strategy: {strategy}')
            ingredient_str = ingredient_stream[i:j]
            # print(f'tmp ingredient_str: {ingredient_str}')
        if cursor.get(token.pos_):
            cursor = cursor[token.pos_]
            j += len(token.text_with_ws)
            # print(f'current {ingredient_stream[i:j]}')
        else:
            if strategy:
                ingredient_list.append(ingredient_str)
                strategy = None

            j += len(token.text_with_ws)
            i = j
            cursor = root
            # print('skipped: ' + token.text)
    if i != j:
        ingredient_list.append(ingredient_stream[i:j])
    # if cursor.get('strategy'):
    #     strategy = cursor['strategy']
    # strategy = cursor['strategy']
    print(ingredient_list)
    return ingredient_list

def get_strategy(ingredient_line: str):
    with open(file='./parse_tree.json', mode='r', encoding='utf-16', ) as strategy_dict:
        root = json.load(strategy_dict)
    doc = nlp(ingredient_line)
    cursor = root
    strategy = None # maybe to be replaced with a default strategy
    for token in doc:
        if cursor.get(token.pos_):
            cursor = cursor[token.pos_]
            if cursor.get('strategy'):
                strategy = cursor['strategy']
        else:
            break
    return strategy #if strategy else None

if __name__ == '__main__':
    stream = "1 l de sauce béchamel, fluide (voir p. 156) 1 l de lait"
    parse_stream(stream)
    # build_tree()
    # print(get_strategy("1 l de sauce béchamel, fluide (voir p. 156)"))
