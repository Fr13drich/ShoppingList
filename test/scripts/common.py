import os
import subprocess
import configparser

config = configparser.ConfigParser()
config.read('./config.cfg')

EXT = '.exe' if os.name == 'nt' else '3'
TEST_RESULTS_DIR = config['TEST']['TEST_RESULTS_DIR']
RECIPE_DIR = config['DEFAULT']['RECIPES_DIR']

def run_reader(input_dir: str):
    subprocess.run(['python' + EXT,  './read_the_book.py',
                    '--input_dir=' + input_dir, '--output_dir=' + TEST_RESULTS_DIR],
                    stdout=subprocess.PIPE, check=True)

def compare():
    """test the ouput of read_the_book.py"""
    for _root, _dirs, files in os.walk(TEST_RESULTS_DIR):
        for name in files:
            with open(file=TEST_RESULTS_DIR + name, mode='r', encoding='utf-16') as test_result:
                with open(file=RECIPE_DIR + name, mode='r', encoding='utf-16') as recipe_file:
                    assert recipe_file.read() == test_result.read()