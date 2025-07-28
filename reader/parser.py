"""parser.py
This module contains functions to parse ingredient strings"""
import json
import configparser
import logging
import spacy
from recipe import IngredientEntry
from ingredient import Ingredient
config = configparser.ConfigParser()
config.read('./config.cfg')
nlp = spacy.load("fr_core_news_md")
logger = logging.getLogger(__name__)

UNIT_LIST = ['millilitre', 'tour', 'tranche',  'l', 'pincée', 'brin',
                 'bâton', 'bille', 'branche', 'botte', 'kilogramme', 'gramme', 'tête',
                 'trait', 'gousses', 'gousse', 'pincee', 'feuille', 'grain', 'morceau',
                 'c. à s.', 'càs', 'cuillère à soupe', 'cuillères à soupe',
                 'c. à c.', 'càc', 'cuillère à café', 'cuillères à café',
                 ]
    # juxtaposant_list = ['de', 'd\'', 'à']

def parse_ingredients(raw_list_of_ingredients: list):
    """Return a dict(name, amount)"""
    result = {}
    for item in raw_list_of_ingredients:
        split_item = str(item).split(maxsplit=1)
        print(split_item)
        amount = str(split_item[0])
        if amount.isnumeric():
            amount = int(amount)
            name = str(split_item[1]).lower()
        elif ',' in amount:
            amount = float('.'.join(amount.split(sep=',')))
            name = str(split_item[1]).lower()
        else:
            amount = 1
            name = str(item).lower()
        result.update({name: amount})
    return result

def parse_stream(ingredient_stream: str):
    """Split a str containing potentialy multiple ingredients
       Return a list of str
       '1 pincée de sel, 1 pincée de poivre' returns ['1 pincée de sel', '1 pincée de poivre']
    """
    with open(file=config['DEFAULT']['TREE'], mode='r', encoding='utf-8', ) as strategy_dict:
        root = json.load(strategy_dict)
    logger.info('raw ingredient stream befor parsing: %s', ingredient_stream)
    doc = nlp(ingredient_stream)
    ingredient_list = []
    cursor = root
    i = j = 0
    strategy = ingredient_str = None
    for token in doc:
        # print(token.pos_)
        if cursor.get('strategy'):
            strategy = cursor['strategy']
            logger.info('potential strategy: %s', strategy)
            # print(f'potential strategy: {strategy}')
            ingredient_str = ingredient_stream[i:j]
            logger.info('tmp ingredient_str: %s', ingredient_str)
            # print(f'tmp ingredient_str: {ingredient_str}')
        if cursor.get(token.pos_):
            cursor = cursor[token.pos_]
            strategy = cursor.get('strategy', strategy)
            # strategy = cursor['strategy'] if cursor.get('strategy') else strategy
            j += len(token.text_with_ws)
            # print(f'current {ingredient_stream[i:j]}')
        else:
            if strategy:
                ingredient_list.append(ingredient_str.strip())
                strategy = None
            cursor = root
            if cursor.get(token.pos_):
                logger.info('new ingredient item: %s', token.text)
                cursor = cursor[token.pos_]
                i = j
                j += len(token.text_with_ws)
                ingredient_str = ingredient_stream[i:j]
            else:
                j += len(token.text_with_ws)
                i = j
                logger.info('skipped: %s', token.text)
            # print('skipped: ' + token.text)
    if i != j:
        if strategy:
            ingredient_list.append(ingredient_stream[i:j].strip())
        else:
            ingredient_list[-1] += ' ' + ingredient_stream[i:j].strip()
    print(ingredient_list)
    logger.info('ingredient_list: %s', ingredient_list)
    return ingredient_list

def get_strategy(ingredient_line: str):
    """search the tree for a strategy"""
    with open(file=config['DEFAULT']['TREE'], mode='r', encoding='utf-8', ) as strategy_dict:
        root = json.load(strategy_dict)
    doc = nlp(ingredient_line)
    cursor = root
    strategy = None
    print([token.pos_ for token in doc])
    print([token.lemma_ for token in doc])
    for token in doc:
        if cursor.get(token.pos_):
            cursor = cursor[token.pos_]
            if cursor.get('strategy'):
                strategy = cursor['strategy']
        else:
            break
    return strategy

def strategy01(d: str, text_list, lemma_list, pos_list, book_ref: str):
    """quantity in first position then the ingredient name"""
    logger.info('strategy01 %s %s', book_ref, pos_list)
    #check for a ref to another recipe
    # if pos_list[-5:] == ["PUNCT", "VERB", "NOUN", "NUM", "PUNCT"]:
    #     other_recipe_ref = book_ref + 'p' + str(text_list[-2])
    #     lemma_list = lemma_list[:-5]
    #     d = d[0:d.index(' (')] if d.find('(') else d
    # if lemma_list[1] in UNIT_LIST:
    #     lemma = ' '.join(lemma_list[3:])
    #     unit = str(lemma_list[1])
    #     jxt = str(text_list[2])
    #     name = d[d.index(text_list[3]):]  #' '.join(text_list[3:])
    # else:
    lemma = lemma_list[1]
    unit = 'p'
    jxt = ''
    name = d[d.index(text_list[1]):]
    # lemma = ' '.join(lemma_list[1:])
    return (unit, jxt, name, lemma, None)
def strategy013(d: str, text_list, lemma_list, pos_list, book_ref: str):
    """shape is: amount unit jxt name"""
    other_recipe_ref = None
    #check for a ref
    if pos_list[-5:] == ["PUNCT", "VERB", "NOUN", "NUM", "PUNCT"]:
        other_recipe_ref = book_ref + 'p' + str(text_list[-2])
        lemma_list = lemma_list[:-5]
        d = d[0:d.index(' (')] if d.find('(') else d
    if "PUNCT" in pos_list:
        d= d[0:d.index(text_list[pos_list.index("PUNCT")])] #remove all after punct
    #check for a unit
    if lemma_list[1] in UNIT_LIST or text_list[1] in UNIT_LIST:
        lemma = ' '.join(lemma_list[3:])
        unit = lemma_list[1] if lemma_list[1] in UNIT_LIST else text_list[1]
        jxt = str(text_list[2])
        name = d[d.index(text_list[3]):]  #' '.join(text_list[3:])
    else:
        lemma = lemma_list[1]
        unit = 'p'
        jxt = ''
        name = d[d.index(text_list[1]):]
    return (unit, jxt, name, lemma, other_recipe_ref)
def strategy0135(d: str, text_list, lemma_list, pos_list, book_ref: str):
    """name from position 3 to 5"""
    other_recipe_ref = None
    #check for a ref
    if pos_list[-5:] == ["PUNCT", "VERB", "NOUN", "NUM", "PUNCT"]:
        other_recipe_ref = book_ref + 'p' + str(text_list[-2])
        lemma_list = lemma_list[:-5]
        d = d[0:d.index(' (')] if d.find('(') else d
    lemma = ' '.join(lemma_list[3:5])
    unit = str(lemma_list[1])
    jxt = str(text_list[2])
    name = d[d.index(text_list[3]):d.index(text_list[4])+len(text_list[4])]
    return (unit, jxt, name, lemma, other_recipe_ref)
def strategy0156(d: str, text_list, lemma_list, pos_list, book_ref: str):
    """name from position until the end (without ref to sub recipe)"""
    other_recipe_ref = None
    #check for a ref
    if pos_list[-5:] == ["PUNCT", "VERB", "NOUN", "NUM", "PUNCT"]:
        # buils a recipe ref based on the page number found(NUM)
        other_recipe_ref = book_ref + 'p' + str(text_list[-2])
        lemma_list = lemma_list[:-5]
        d = d[0:d.index(' (')] if d.find('(') else d
    lemma = ' '.join(lemma_list[6:])
    # unit = ' '.join(lemma_list[1:5])
    unit = d[d.index(text_list[1]):d.index(text_list[5])-1]
    jxt = str(text_list[5])
    name = d[d.index(text_list[6]):]
    return (unit, jxt, name, lemma, other_recipe_ref)
def strategy04(d: str, text_list, lemma_list, pos_list, book_ref: str):
    """Ingredient name in position 4. No unit nor jxt."""
    other_recipe_ref = None
    #check for a reference to another recipe
    if pos_list[-5:] == ["PUNCT", "VERB", "NOUN", "NUM", "PUNCT"]:
        other_recipe_ref = book_ref + 'p' + str(text_list[-2])
        lemma_list = lemma_list[:-5]
        d = d[0:d.index(' (')] if d.find('(') else d
    lemma = ' '.join(lemma_list[4:])
    unit = 'p'
    name = d[d.index(text_list[4]):]
    return (unit, '', name, lemma, other_recipe_ref)
def strategy34(d: str, text_list, lemma_list, pos_list, book_ref=None):
    """Le jus de 1 citron -> 1 citron"""
    print(pos_list)
    other_recipe_ref = book_ref
    lemma = lemma_list[-1]
    unit = 'p'
    jxt = ''
    name = d[d.index(text_list[-1]):]
    return (unit, jxt, name, lemma, other_recipe_ref)
def strategy0146(d: str, text_list, lemma_list, pos_list, book_ref=None):
    """'NUM', 'PROPN', 'PUNCT', 'ADP', 'NOUN', 'ADP', 'NOUN'"""
    print(pos_list)
    lemma = ' '.join(lemma_list[4:])
    name = d[d.index(text_list[4]):]
    unit = str(text_list[1])
    jxt = str(text_list[3])
    return (unit, jxt, name, lemma, book_ref)
def strategy01357(d: str, text_list, lemma_list, pos_list, book_ref=None):
    """'NUM', 'NOUN', 'ADP', 'NOUN', 'ADP', 'NOUN', 'ADP', 'NOUN'"""
    if ' '.join(text_list[1:4]) in UNIT_LIST:
        lemma = ' '.join(lemma_list[-3:])
        name = d[d.index(text_list[-3]):]
        unit = ' '.join(text_list[1:4])
        jxt = text_list[4]
    elif lemma_list[1] in UNIT_LIST:
        lemma = ' '.join(lemma_list[3:])
        name = d[d.index(text_list[3]):]
        unit = lemma_list[1]
        jxt = text_list[2]
    else:
        print(pos_list)
        raise ValueError('A very specific bad thing happened.')
    return (unit, jxt, name, lemma, book_ref)

def strategy_name_only(d: str, _text_list, lemma_list, _pos_list, _book_ref: str):
    """Sel"""
    lemma = ' '.join(lemma_list)
    unit = 'p'
    name = d
    jxt = ''
    return (unit, jxt, name, lemma, None)

# def choose_strategy(s: str):
#     """Return the right parsing function"""
#     if s == "strategy01":
#         return strategy01
#     if s == "strategy013":
#         return strategy013
#     if s == "strategy0135":
#         return strategy0135
#     if s == "strategy0156":
#         return strategy0156
#     if s == "strategy04":
#         return strategy04
#     if s == "strategy34":
#         return strategy34
#     if s == "strategy_name_only":
#         return strategy_name_only

def parse_ingredients_bill_dict(ingredients_bill_dict: dict, recipe_ref: str):
    """Return a list of IngredientEntry objects from a dict of ingredients"""
    entries = []
    for d , amount in ingredients_bill_dict.items():
        doc = nlp(' '.join([str(amount), d]))
        try:
            # strategy = choose_strategy(get_strategy(' '.join([str(amount), d])))
            strategy = globals()[get_strategy(' '.join([str(amount), d]))]
        except KeyError:
            logger.warning('Key error on %s', d)
        unit, jxt, name, lemma, other_recipe_ref =\
            strategy(d, text_list=[token.text for token in doc],
                        lemma_list=[token.lemma_ for token in doc],
                        pos_list=[token.pos_ for token in doc],
                        book_ref = recipe_ref[0:recipe_ref.rindex('p')]
                            if 'p' in recipe_ref else None)
        entries.append(IngredientEntry(amount, unit, jxt,\
                    Ingredient.add(name=name,lemma=lemma, recipe_refs=set([str(recipe_ref)]),\
                                    other_recipe_ref=other_recipe_ref)))
    return entries
