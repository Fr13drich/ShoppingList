"""Test the output of read_the_book.py on one recipe.

Runs the OCR and parsing pipeline on a test image directory and compares the
resulting recipe files to expected outputs.
"""

import os
import configparser
# import common

config = configparser.ConfigParser()
config.read('./config.cfg', encoding='utf-8')

INPUT_DIR = config['TEST']['EB_PICS']
# common.run_reader(INPUT_DIR)

def test_compare():
    """Compare generated recipe files to expected test results.

    Asserts that the contents of each generated recipe file match the expected output.
    """
    for _root, _dirs, files in os.walk(common.TEST_RESULTS_DIR):
        print(files)
        for name in files:
            with open(file=os.path.join(common.TEST_RESULTS_DIR, name), mode='r', encoding='utf-8') as test_result:
                with open(file=os.path.join(common.RECIPE_DIR, name), mode='r', encoding='utf-8') as recipe_file:
                    print(name)
                    assert recipe_file.read() == test_result.read()
