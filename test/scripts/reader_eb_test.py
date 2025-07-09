"""test the ouput of read_the_book.py on one recipe"""
import os
import configparser
import common

config = configparser.ConfigParser()
config.read('./config.cfg')

INPUT_DIR = config['TEST']['EB_PICS']
common.run_reader(INPUT_DIR)
def test_compare():
    for _root, _dirs, files in os.walk(common.TEST_RESULTS_DIR):
        print(files)
        for name in files:
            with open(file=common.TEST_RESULTS_DIR + name, mode='r', encoding='utf-8') as test_result:
                with open(file=common.RECIPE_DIR + name, mode='r', encoding='utf-16') as recipe_file:
                    print(name)
                    assert recipe_file.read() == test_result.read()
