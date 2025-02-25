"""Extract ingredients bills from my cooking books."""
import os
import logging
import json
import configparser
from Reader import Reader

config = configparser.ConfigParser()
config.read('./config.cfg')

logger = logging.getLogger(__name__)
logging.basicConfig(filename=config['DEFAULT']['READER_LOG_FILE'],\
                    level=logging.INFO, encoding='utf-16')


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
            with open(outfile, 'w', encoding='utf-16') as outfile:
                json.dump({'ref': ref, 'name':name, 'ingredients':parsed_ingredients},\
                          outfile, indent=2, ensure_ascii=False)

if __name__ == '__main__':
    pics2json(config["DEFAULT"]["BC_PICS"])
