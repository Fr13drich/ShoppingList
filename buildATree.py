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
    with open(file='./parse_tree.json', mode='r', encoding='utf-16', ) as strategy_dict:
        root = json.load(strategy_dict)
    doc = nlp(ingredient_stream)
    ingredient_list = []
    cursor = root
    i = j = 0
    print(ingredient_stream)
    print([token.pos_ for token in doc])
    for token in doc:
        if cursor.get(token.pos_):
            # print(token.pos_)
            cursor = cursor[token.pos_]
            j += len(token.text_with_ws)
        elif cursor.get('strategy'):
            ingredient_list.append(ingredient_stream[i:j])
            strategy = cursor['strategy']
            i = j
            j += len(token.text_with_ws)
            cursor = root[token.pos_] if root.get(token.pos_) else root
            print(ingredient_list[-1] + ' ' + strategy)
        else:
            j += len(token.text_with_ws)
            i = j
            cursor = root
            print('skipped: ' + token.text)
    ingredient_list.append(ingredient_stream[i:j])
    strategy = cursor['strategy']
    print(ingredient_list[-1] + ' ' + strategy)
    return ingredient_list
#         break
# print(cursor['strategy'])

if __name__ == '__main__':
    # stream = "Huile d'olive"
    # parse_stream(stream)
    build_tree()
