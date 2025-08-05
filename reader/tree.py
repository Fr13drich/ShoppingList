"""Lexical tree"""
import json
import configparser

config = configparser.ConfigParser()
config.read('./config.cfg', encoding='utf-8')
def load_pattern(file=config['DEFAULT']['INGREDIENT_ENTRY_MORPHOLOGY_FILE']):
    """load a list of ingredient lines lexical morphology"""
    with open(file, 'r', encoding='utf-8', ) as morphology_file:
        return json.load(morphology_file)

def build_tree():
    """create a tree from à nested list"""
    shape = load_pattern()
    root = cursor = {}
    for k, v in shape.items():
        cursor = root
        tokens = str(k).split()
        for token in tokens:
            if not cursor.get(token):
                cursor[token] = {}
            cursor = cursor[token]
        cursor['strategy'] = v
        print(f'Adding {root} with strategy {v}')
    with open(file=config['DEFAULT']['TREE'], mode='w', encoding='utf-8') as f:
        json.dump(root, f, indent=2)

if __name__ == '__main__':
    build_tree()
