"""test the ouput of read_the_book.py on one recipe"""
import os
import configparser
import common

config = configparser.ConfigParser()
config.read('./config.cfg')
TEST_RESULTS_DIR = config['TEST']['TEST_RESULTS_DIR']
RECIPE_DIR = config['DEFAULT']['RECIPES_DIR']
# INPUT_DIR = config['TEST']['BC_PICS']
# common.run_reader(INPUT_DIR)
def test_answer():
    for _root, _dirs, files in os.walk(TEST_RESULTS_DIR):
        print(files)
        for name in files:
            with open(file=os.path.join(TEST_RESULTS_DIR, name), mode='r', encoding='utf-16') as test_result:
                with open(file=os.path.join(RECIPE_DIR, name), mode='r', encoding='utf-16') as recipe_file:
                    print(name)
                    assert common.compare(recipe_file, test_result)

if __name__ == '__main__':
    test_answer()
