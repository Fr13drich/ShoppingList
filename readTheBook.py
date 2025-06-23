"""Extract ingredients bills from my cooking books."""
import os
import logging
import json
import configparser
from Reader import Reader
from Recipe import Recipe

config = configparser.ConfigParser()
config.read('./config.cfg')

logger = logging.getLogger(__name__)
FORMAT = '%(asctime)s %(message)s'
logging.basicConfig(filename=config['DEFAULT']['READER_LOG_FILE'],\
                    level=logging.INFO, encoding='utf-16', format=FORMAT)


def pics2json(location):
    for _root, _dirs, files in os.walk(location):
        for name in files:
            print('Reading ' + str(name) + ' from ' + location)
            ref, name, parsed_ingredients = Reader.parse(location, name)
            outfile = config['DEFAULT']['READER_OUTPUT_DIR'] + ref + '.json'
            logger.info('%s, %s', ref, name)
            logger.info('%s', parsed_ingredients)
            if os.path.exists(outfile):
                if input(outfile + " already exists. Should I overwrite?: ") != 'y':
                    continue
            with open(outfile, 'w', encoding='utf-16') as raw_dict:
                json.dump({'ref': ref, 'name':name, 'ingredients':parsed_ingredients},\
                            raw_dict, indent=2, ensure_ascii=False)
            logger.info('Written: %s', outfile)
            json2recipe(outfile)

def json2recipe(file):
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
                    ingredients_bill=Recipe.parse_ingredients_bill_dict(\
                        ingredients_bill_dict=recipe_dict['ingredients'],\
                        recipe_ref=recipe_dict['ref']))
    new.write_recipe_file()
    logger.info('Recipe written: %s %s', new.ref, new.name)

if __name__ == '__main__':
    pics2json(location=config["DEFAULT"]["BC_PICS"])
    # for root, dirs, files in os.walk(config["DEFAULT"]["READER_OUTPUT_DIR"]):
    #     for name in files:
    #         print(root)
    #         print(dirs)
    #         print(name)
    #         json2recipe(root + name)
