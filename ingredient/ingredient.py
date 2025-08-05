"""Describe the class Ingredient"""
import os
from urllib.parse import unquote
import configparser
import logging
import json
import spacy
import requests

config = configparser.ConfigParser()
config.read('./config.cfg')
nlp = spacy.load("fr_core_news_md")
logger = logging.getLogger(__name__)

class Ingredient:
    """An ingredient for cooking"""
    knowkn_ingredients_list = []
    def __init__(self, *, name: str, lemma: str, recipe_refs: set, wiki_ref=None, category=None,\
                 synonymes=None, other_recipe_ref=None):
        self.name = name
        self.lemma = lemma
        self.wiki_ref = wiki_ref # if wiki_ref else Ingredient.get_wiki_ref(name)
        self.category = category
        self.synonymes = synonymes if synonymes else set([name, lemma])
        self.recipe_refs = set(recipe_refs) #if recipe_refs else set()
        self.other_recipe_ref = other_recipe_ref
        # prefered_unit
        # possible_units
        Ingredient.knowkn_ingredients_list.append(self)
        logger.info('Created: %s', str(self))

    def write_ingredient_file(self):
        """write an ingredient on disk in json"""
        name = self.wiki_ref if self.wiki_ref else self.name
        filename = name + '.json'
        with open(os.path.join(config['DEFAULT']['INGREDIENTS_DIR'],
                  str(filename).encode('utf-8').decode('utf-8')),\
                  'w', encoding='utf-8') as outfile:
            json.dump(self.serialize(), outfile, indent=2, ensure_ascii=False)
        logger.info('%s written', filename)

    def __str__(self):
        return str('Ingredient: ' + str(self.name)
                   + ' Wiki ref: ' + str(self.wiki_ref)
                   + ' Synonymes: '  + str(self.synonymes)
                   + ' recipe_refs: '  + str(self.recipe_refs)
                   + ' lemma: '  + str(self.lemma)
                  )

    @classmethod
    def add(cls, *, name: str, lemma: str, recipe_refs: set,\
            wiki_ref=None, category=None, other_recipe_ref=None):
        """ Add a new ingredient in the ingredients list if necessary
        otherwise update and return an existing ingredient"""
        # look for the name in all synonymes list
        for knowkn_ingredient in cls.knowkn_ingredients_list:
            if name in knowkn_ingredient.synonymes or\
                (' '.join([token.lemma_ for token in nlp(name)]) == knowkn_ingredient.lemma):
                knowkn_ingredient.synonymes.add(name)
                if recipe_refs\
                and not set(recipe_refs).issubset(set(knowkn_ingredient.recipe_refs)):
                    logger.info('Intersection: %s',
                                set(recipe_refs).issubset(set(knowkn_ingredient.recipe_refs)))
                    knowkn_ingredient.recipe_refs = knowkn_ingredient.recipe_refs.union(recipe_refs)
                    Ingredient.write_ingredient_file(knowkn_ingredient)
                return knowkn_ingredient
        new_ingredient = Ingredient(name=name, lemma=lemma, wiki_ref=wiki_ref, category=category,\
                                    synonymes=set([name]), recipe_refs=recipe_refs,\
                                    other_recipe_ref=other_recipe_ref)
        # new_ingredient.write_ingredient_file()
        return new_ingredient

    @classmethod
    def get_wiki_ref(cls, name):
        """search for the name in wikipedia. Return the last part of the url aka wiki_ref"""
        wiki_ref = None
        #shorten the name
        # words = str(name).rsplit(sep=, maxsplit=5)
        # words = re.split(r"['()\s]+", name)
        words_lemma = [token.lemma_ if (token.pos_ == "NOUN")\
                                    else token.text for token in nlp(name)]
        words_pos = [token.pos_ for token in nlp(name)]
        logger.info('lemmas: %s', words_lemma)
        nb_words = len(words_lemma)
        for i in range(nb_words):
            # search_str = '+'.join([s  for s in words[:nb_words-i]])
            # search_str = '+'.join(words[:nb_words-i])
            search_str = '+'.join(words_lemma[:nb_words-i])
            if 'NOUN' in words_pos[:nb_words-i]:
                logger.info('search string: %s', search_str)
                r = Ingredient.send_search_request(search_str)
                if r:
                    wiki_ref = Ingredient.parse_response(r)
                if wiki_ref:
                    return wiki_ref
        #try in reverse mode
        for i in range(nb_words):
            search_str = '+'.join(words_lemma[i:])
            if 'NOUN' in words_pos[:nb_words-i]:#paprika est vu comme un adjectif par spacy...
                logger.info('search string (reverse): %s', search_str)
                r = Ingredient.send_search_request(search_str)
                if r:
                    wiki_ref = Ingredient.parse_response(r)
                if wiki_ref:
                    return wiki_ref
        return wiki_ref

    @staticmethod
    def send_search_request(search_str: str):
        """Handle the get requests to Wikipedia. Return the response"""
        language_code = 'fr'
        number_of_results = 1
        headers = {
            # 'Authorization': 'Bearer YOUR_ACCESS_TOKEN',
            'User-Agent': 'YOUR_APP_NAME (YOUR_EMAIL_OR_CONTACT_PAGE)'
            }
        base_url = 'https://api.wikimedia.org/core/v1/wikipedia/'
        endpoint = '/search/page'
        url = base_url + language_code + endpoint
        parameters = {'q': search_str, 'limit': number_of_results}
        try:
            r = requests.get(url, headers=headers, params=parameters,
                allow_redirects=True, timeout=10)
        except ConnectionError:
            logger.info('No internet!')
            return None
        logger.info('Response received from Wikipedia.')
        # r.encoding = r.encoding = r.apparent_encoding
        if r.status_code != 200:
            logger.info('Bad response %s', r.status_code)
            return None
        return r

    @staticmethod
    def parse_response(response):
        """Parse the response of a get request to Wikipedia.
        May be usefull to categorize an ingredient"""
        wiki_ref = None
        for line in response.iter_lines():
            if config['DEFAULT']['WIKI_URL'] in str(line):
                if 'Recherche' in str(line):
                    return None # no search result
                url = str(line)[str(line).index(config['DEFAULT']['WIKI_URL']):-3]
                #get rid of trailing hashtags if any
                url = url[:url.find('#')] if '#' in url else url
                # url = unquote(url)
                wiki_ref = unquote(str(url).rsplit(sep='/', maxsplit=1)[-1])
                logger.info('Found ref in wikipedia: %s', wiki_ref)
                break
        return wiki_ref

    # def categorize(self):
    #     r = requests.get('https://fr.wikipedia.org/w/index.php?search=beurre',\
    #                       allow_redirects=True, timeout=10)
    #     selector = Selector(text=str(r.content))
    #     selector.xpath('//h1/text()').r

    def serialize(self):
        """produce a dictionary containing relevant attributes for JSON serialization."""
        return dict({'name': self.name,
                     'lemma': self.lemma,
                     'wiki_ref': self.wiki_ref if self.wiki_ref else "",
                     'category': self.category,
                     'synonymes': list(self.synonymes),
                     'recipe_refs': list(self.recipe_refs),
                     'other_recipe_ref': self.other_recipe_ref if self.other_recipe_ref else ""
                    })
