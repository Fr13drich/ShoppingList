"""test the ouput of read_the_book.py on one recipe"""
import configparser
import common

config = configparser.ConfigParser()
config.read('./config.cfg')

INPUT_DIR = config['TEST']['BC_PICS']
common.run_reader(INPUT_DIR)
def test_answer():
    common.compare()
