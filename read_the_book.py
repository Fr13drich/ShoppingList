"""main function of the module
Extract the name of the recipe along with the ingredients bill from my cooking books."""
import os
import sys
import logging
import json
import configparser
from reader import Reader
from reader import parse_ingredients_bill_dict
from recipe import Recipe

config = configparser.ConfigParser()
config.read('./config.cfg')

logger = logging.getLogger(__name__)
FORMAT = '%(asctime)s %(message)s'
logging.basicConfig(filename=config['DEFAULT']['READER_LOG_FILE'],\
                    level=logging.INFO, encoding='utf-16', format=FORMAT)


def pics2json(location, output_dir=None):
    """main loop of read_the_book"""
    for root, _dirs, files in os.walk(location):
        for name in files:
            print('Reading ' + str(name) + ' from ' + root)
            ref, name, parsed_ingredients = Reader.read(str(root) + '/', name)
            outfile = config['DEFAULT']['READER_OUTPUT_DIR'] + ref + '.json'
            logger.info('%s, %s', ref, name)
            logger.info('%s', parsed_ingredients)
            # if os.path.exists(outfile):
            #     if input(outfile + " already exists. Should I overwrite?: ") != 'y':
            #         continue
            with open(outfile, 'w', encoding='utf-16') as raw_dict:
                json.dump({'ref': ref, 'name':name, 'ingredients':parsed_ingredients},\
                            raw_dict, indent=2, ensure_ascii=False)
            logger.info('Written: %s', outfile)
            json2recipe(outfile, output_dir)

def json2recipe(file, output_dir=None):
    """
    File layout:
    ref: str,
    name: str,
        ingredients: {str: int, ...}
    """
    # if input(f"Create recipe from {file} ?: ") == 'y':
    with open(file=file, mode='r', encoding='utf-16') as recipe_file:
        recipe_dict = json.load(recipe_file)
        logger.info(recipe_dict['ref'])
        new = Recipe(ref=recipe_dict['ref'],\
                    name=recipe_dict['name'],\
                    ingredients_bill=parse_ingredients_bill_dict(\
                        ingredients_bill_dict=recipe_dict['ingredients'],\
                        recipe_ref=recipe_dict['ref']))
    new.write_recipe_file(output_dir)
    logger.info('Recipe written: %s %s', new.ref, new.name)

if __name__ == '__main__':
    try:
        OUTPUT_DIR = sys.argv[1] if os.path.exists(sys.argv[1]) else None
    except IndexError:
        OUTPUT_DIR = None
    pics2json(location='./data/pics/', output_dir=OUTPUT_DIR)
    # pics2json(location=config["DEFAULT"]["BC_PICS"], output_dir=OUTPUT_DIR)
    # if sys.argv[1]:
    #     print(sys.argv[1])
    #     if os.path.exists(sys.argv[1]):
    #         pics2json(location=sys.argv[1])
    #     else:
    #         pics2json(location=config["DEFAULT"]["BC_PICS"])
    # # for root, dirs, files in os.walk(config["DEFAULT"]["READER_OUTPUT_DIR"]):
    #     for name in files:
    #         print(root)
    #         print(dirs)
    #         print(name)
    #         json2recipe(root + name)
