import os
import subprocess
import configparser

config = configparser.ConfigParser()
config.read('./config.cfg')

EXT = '.exe' if os.name == 'nt' else '3'
TEST_RESULTS_DIR = config['TEST']['TEST_RESULTS_DIR']
RECIPE_DIR = config['DEFAULT']['RECIPES_DIR']

def run_reader(input_dir: str):
    """Run the reader script with the specified input directory."""
    if not os.path.exists(TEST_RESULTS_DIR):
        os.makedirs(TEST_RESULTS_DIR)
    subprocess.run(['python' + EXT,  './read_the_book.py',
                    '--input_dir=' + input_dir, '--output_dir=' + TEST_RESULTS_DIR],
                    stdout=subprocess.PIPE, check=True)

def compare(recipe_file, test_result):
    """test the ouput of read_the_book.py"""
    return recipe_file.read() == test_result.read()
