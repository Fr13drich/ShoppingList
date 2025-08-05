"""main function of the module
Extract the name of the recipe along with the ingredients bill from my cooking books."""
import os
import logging
import configparser
import argparse
import pathlib
from reader import Reader
from reader import parse_ingredients_bill_dict
from recipe import Recipe

config = configparser.ConfigParser()
config.read('./config.cfg', encoding='utf-8')

logger = logging.getLogger(__name__)
FORMAT = '%(asctime)s %(message)s'
logging.basicConfig(filename=config['DEFAULT']['READER_LOG_FILE'],\
                    level=logging.INFO, encoding='utf-8', format=FORMAT)

def make_parser():
    """Create an ArgumentParser for this script.

    :return: A parser.
    """
    parser = argparse.ArgumentParser(
        description="Scan (OCR) pictures from cooking books."
    )

    # Add arguments for custom data files.
    parser.add_argument('--input_dir', default=config['DEFAULT']['BC_PICS'],
                        type=pathlib.Path,
                        help="Path to pictures.")
    parser.add_argument('--output_dir', default=config['DEFAULT']['RECIPES_DIR'],
                        type=pathlib.Path,
                        help="Path to output for recipe files.")
    return parser

def pics2recipe(input_dir, output_dir):
    """Main function. scan, parse and write to disk"""
    assert pathlib.Path(input_dir).is_dir()
    assert pathlib.Path(output_dir).is_dir()
    for root, _dirs, files in os.walk(input_dir):
        for name in files:
            assert pathlib.PurePosixPath(name).suffix == '.jpg'
            print('Reading ' + str(name) + ' from ' + root)
            ref, name, parsed_ingredients = Reader.read(str(pathlib.Path(root)), name)
            logger.info('%s, %s', ref, name)
            logger.info('%s', parsed_ingredients)
            recipe_dict = {'ref': ref, 'name':name, 'ingredients':parsed_ingredients}
            logger.info(recipe_dict['ref'])
            Recipe(ref=recipe_dict['ref'],
                    name=recipe_dict['name'],
                    ingredients_bill=parse_ingredients_bill_dict(
                        ingredients_bill_dict=recipe_dict['ingredients'],
                        recipe_ref=recipe_dict['ref'])
                    ).write_recipe_file(output_dir)
            print('Recipe ' + str(recipe_dict['name']) + ' ' + str(recipe_dict['ref']) + ' written')
            print('Run setup_db.py to insert the recipe into the database')
if __name__ == '__main__':
    read_the_book_parser = make_parser()
    args = read_the_book_parser.parse_args()
    if not os.path.exists(args.output_dir):
        os.makedirs(args.output_dir)
    pics2recipe(input_dir=args.input_dir, output_dir=args.output_dir)
