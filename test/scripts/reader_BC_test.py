"""test the ouput of read_the_book.py on one recipe"""
import os
import subprocess
EXT = '.exe' if os.name == 'nt' else '3'
TEST_RESULTS_DIR = './test/test_results/'
RECIPE_DIR = './data/recipe_files/'

p = subprocess.run(['python' + EXT,  './read_the_book.py', TEST_RESULTS_DIR],
                           stdout=subprocess.PIPE, check=True)

def test_answer():
    """test the ouput of read_the_book.py"""
    for _root, _dirs, files in os.walk(TEST_RESULTS_DIR):
        for name in files:
            with open(file=TEST_RESULTS_DIR + name, mode='r', encoding='utf-16') as test_result:
                with open(file=RECIPE_DIR + name, mode='r', encoding='utf-16') as recipe_file:
                    assert recipe_file.read() == test_result.read()
