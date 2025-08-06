"""Extract title and ingredients from pictures"""
import os
import configparser
import logging
from operator import itemgetter
from abc import ABC, abstractmethod
import spacy
import pytesseract
from spellchecker import SpellChecker
from PIL import Image, ImageOps
import easyocr
from reader import parser
config = configparser.ConfigParser()
config.read('./config.cfg', encoding='utf-8')
reader = easyocr.Reader(lang_list=['fr'], gpu=False)
logger = logging.getLogger(__name__)
nlp = spacy.load("fr_core_news_md")

class ReaderInterface(ABC):
    """Generic class to read text from a jpg picture."""
    allowed_books = []
    allowed_extensions = ['jpg']
    footpage_workfile = 'tmp/img_footpage.jpg'
    title_workfile = './tmp/img_recipe.jpg'
    ingredients_workfile = './tmp/img_ingredients.jpg'
    reader_result = None
    left_page = True

    @staticmethod
    def spell_check(i: str) -> str:
        """Spell check a string."""
        spell = SpellChecker(language='fr')
        doc = nlp(i)
        spell.word_frequency.load_words(['dégermer', 'dénoyauter', 'cerneaux', 'pistoles'])
        spell.word_frequency.load_words(config['DEFAULT'].get('UNIT_LIST', '').split(','))
        for token in doc:
            if spell.unknown([token.text]) and spell.unknown([token.lemma_]):
                logger.warning('Unknown word: %s', token.text)
                i = str(i).replace(token.text, spell.candidates(token.text).pop())
        return i

    @classmethod
    def can_read(cls, _location, name) -> bool:
        """Can I read that picture from that book?."""
        ext = name.split('.')[-1]
        return ext in cls.allowed_extensions #location in cls.allowed_books and
    @staticmethod
    def autocrop(jpg):
        """Crop where there is no text."""
        results = reader.readtext(image=jpg, detail=1, paragraph=True, x_ths=2000, y_ths=.2,\
                                  text_threshold=.1, height_ths=1000, min_size=50)
        # logger.info('before crop results of %s : %s', jpg, results)
        max_box = [10000, 10000, 0, 0]
        for box_coordinates in results:
            max_box[0] = min(max_box[0], int(box_coordinates[0][0][0]))
            max_box[1] = min(max_box[1], int(box_coordinates[0][0][1]))
            max_box[2] = max(max_box[2], int(box_coordinates[0][2][0]))
            max_box[3] = max(max_box[3], int(box_coordinates[0][2][1]))
        img = Image.open(jpg)
        img = img.crop(tuple(max_box))
        img.save(jpg)
        results = reader.readtext(image=jpg, detail=1, paragraph=True, x_ths=2000, y_ths=.2,\
                                  text_threshold=.1, height_ths=1000, min_size=50)
        # logger.info('after crop results of %s : %s', jpg, results)

    @classmethod
    def image_preprocessing(cls, pic):
        """"grayscaled and cropped pic"""
        img = Image.open(pic)
        img = ImageOps.exif_transpose(img)
        img = ImageOps.grayscale(img)
        img.save("tmp/img.jpg")
        cls.autocrop("tmp/img.jpg")
        return "tmp/img.jpg"
    # parse_ingredients method moved to parser.py
    @classmethod
    @abstractmethod
    def read(cls, location, name):
        """Ingest the picture."""
    @classmethod
    @abstractmethod
    def get_title(cls, img):
        """OCR and retrieve title"""
    @classmethod
    @abstractmethod
    def get_ingredients(cls, img):
        """OCR and retrieve ingredients"""
    @classmethod
    @abstractmethod
    def get_ref(cls, img):
        """OCR and build a reference base on the name of the book and the page number."""
class BcReader(ReaderInterface):
    """Read pictures from 'Bien cuisiner'."""
    allowed_books = [config['DEFAULT']['BC_PICS']]

    def __init__(self, location: str, name: str) -> None:
        """Construct."""
        super().__init__()
        self.location = location
        self.name = name
        self.left_page = True
    @classmethod
    def read(cls, location: str, name: str):
        """Ingest the file."""
        if not cls.can_read(location, name):
            raise ValueError('Cannot parse exception.')
        pic = cls.image_preprocessing(os.path.join(location, name))
        img = Image.open(pic)
        ref = cls.get_ref(img)
        title = cls.get_title(img)
        ingredients = cls.get_ingredients(img)
        print(ingredients)
        return ref, title, parser.parse_ingredients(ingredients)
    @classmethod
    def get_ref(cls, img):
        img_footpage = img.crop((0, img.height * 0.98, img.width, img.height))
        img_footpage.save(cls.footpage_workfile)
        try:
            reader_result = reader.readtext(image=cls.footpage_workfile, text_threshold=.1)
        except ValueError:
            print('No text found')
        if max(reader_result, key=itemgetter(2))[0][0][0] < img_footpage.width/2:
            cls.left_page = True
        else:
            cls.left_page = False
        ref = 'BCp' + str(reader_result[0][1]).split(sep=' ', maxsplit=1)[0]
        logger.info('ref: %s', ref)
        return ref
    @classmethod
    def get_title(cls, img):
        if cls.left_page:
            recipe_coordinates =  img.width/3, 0, img.width, img.height
        else:
            recipe_coordinates = 0, 0, 2 * img.width/3, img.height
        img_recipe = img.crop(recipe_coordinates)
        img_recipe.save(cls.title_workfile)
        cls.autocrop(cls.title_workfile)
        try:
            instructions = reader.readtext(image=cls.title_workfile, detail=1, paragraph=True,\
                                           y_ths=.2, height_ths=0.2, min_size=100)
        except ValueError:
            print('No text found')
        for box in instructions:
            if box[0][0][0] < 100:
                title = box[1]
                break
        logger.info('title: %s', title)
        return title
    @classmethod
    def get_ingredients(cls, img):
        if cls.left_page:
            ingredients_coordinates = 0, 0, img.width/3, img.height*.85
        else:
            ingredients_coordinates = 2 * img.width/3, 0, img.width, img.height*.85
        img_ingredients = img.crop(ingredients_coordinates)
        # enhancer = ImageEnhance.Contrast(img_ingredients)
        # img_ingredients = enhancer.enhance(1)
        img_ingredients.save(cls.ingredients_workfile)
        # cls.autocrop(cls.ingredients_workfile)
        # img = Image.open(self.ingredients_workfile)
        try:
            ingredients = reader.readtext(image=cls.ingredients_workfile, detail=1,
                                          text_threshold=0.5, paragraph=True,
                                          y_ths=.3, height_ths=5)
            # ingredients = list(map(itemgetter(1), ingredients))
        except ValueError:
            print('No text found')
        # remove annotations on the bottom
        # by checking the vertical distance between lines
        distance = ingredients[1][0][0][1] - ingredients[0][0][0][1]
        print(f'distance: {distance}')
        # y = ingredients[0][0][0][1]
        y = ingredients[0][0][2][1]
        print(ingredients)
        for i, ingredient in enumerate(ingredients):
            # if the distance is above the threshold it means it is a comment
            if ingredient[0][0][1] - y > 2 * distance:
                tmp_results = list(map(itemgetter(1), ingredients[:i]))
                results = []
                for item in tmp_results:
                    results += parser.parse_stream(item)
                return results
            # y = ingredient[0][0][1]
            y = ingredient[0][2][1]
        # return ingredients
        tmp_results =  list(map(itemgetter(1), ingredients))
        results = []
        for item in tmp_results:
            results += parser.parse_stream(item)
        return results

class CgReader(ReaderInterface):
    """Read pictures from 'Café gourmand'."""

    allowed_books = [config['DEFAULT']['CG_PICS']]

    def __init__(self, location: str, name: str) -> None:
        """Construct."""
        super().__init__()
        self.location = location
        self.name = name
    @classmethod
    def read(cls, location: str, name: str):
        """Ingest the file."""
        if not cls.can_read(location, name):
            raise ValueError('Cannot parse exception.')
        pic = cls.image_preprocessing(os.path.join(location, name))
        cls.reader_result = reader.readtext(image=pic, detail=1, paragraph=True)
        img = Image.open(pic)
        ref = cls.get_ref(img)
        title = cls.get_title(img)
        ingredients = cls.get_ingredients(img)
        return ref, title, parser.parse_ingredients(ingredients)
    @classmethod
    def get_ref(cls, img):
        ref = 'CGp' + str(cls.reader_result[0][1]).split(sep=' ', maxsplit=1)[0]
        logger.info('ref: %s', ref)
        return ref
    @classmethod
    def get_title(cls, img):
        title_coordinates = cls.reader_result[1][0][0][0], cls.reader_result[1][0][0][1],\
            cls.reader_result[1][0][2][0], cls.reader_result[1][0][2][1]
        img_title = img.crop(title_coordinates)
        img_title.save(cls.title_workfile)
        title = reader.readtext(image=cls.title_workfile, detail=1)[0][1]
        logger.info('title: %s', title)
        return title
    @classmethod
    def get_ingredients(cls, img):
        ingredients_coordinates = cls.reader_result[2][0][0][0], cls.reader_result[2][0][0][1],\
            cls.reader_result[2][0][2][0], cls.reader_result[2][0][2][1]
        img_ingredients = img.crop(ingredients_coordinates)
        img_ingredients.save(cls.ingredients_workfile)
        ingredients_list = reader.readtext(image=cls.ingredients_workfile, detail=0,
                                      ycenter_ths=.5, width_ths=.7, height_ths=1)
        ingredients_str = ' '.join(ingredients_list)
        parsed_ingredients_list = parser.parse_stream(ingredients_str)
        logger.info('the list: %s', parsed_ingredients_list)
        return parsed_ingredients_list

class EbReader(ReaderInterface):
    """En bocal"""
    allowed_books = [config['DEFAULT']['EB_PICS']]

    def __init__(self, location: str, name: str) -> None:
        """Construct."""
        super().__init__()
        self.location = location
        self.name = name

    @classmethod
    def read(cls, location: str, name: str):
        """Ingest the file."""
        if not cls.can_read(location, name):
            raise ValueError('Cannot parse exception.')
        pic = cls.image_preprocessing(os.path.join(location, name))
        cls.reader_result = reader.readtext(image=pic, detail=1, paragraph=True)
        # print(cls.reader_result)
        img = Image.open(pic)
        ref = cls.get_ref(img)
        title = cls.get_title(img)
        ingredients = cls.get_ingredients(img)
        return ref, title, parser.parse_ingredients(ingredients)
    @classmethod
    def get_ref(cls, img=None):
        doc = nlp(cls.reader_result[-1][1])
        # print(cls.reader_result[-1][1])
        for token in doc:
            # print(token.pos_)
            if token.pos_ in ['NUM', 'PRON']:
                logger.info('ref: EBp%s', token.text)
                return f"EBp{token.text}"
        raise ValueError
    @classmethod
    def get_title(cls, img):
        pic = './tmp/img.jpg'
        title = ""
        d = pytesseract.image_to_data(pic, lang='fra')
        lines = d.rsplit(sep='\n')[1:]
        for line in lines:
            values = line.rsplit()
            print(values)
            if len(values) == 12 and float(values[10]) > 50.0: # confidence above 50%
                if str(values[11]) == 'Préparation':
                    break
                title += ' ' + str(values[11])
        title = title.strip().capitalize()
        # s = pytesseract.image_to_string(pic, lang='fra')
        # empty_line = s.find('\n\n')
        # if empty_line > 0:
        #     s = s[empty_line+2:]
        #     empty_line = s.find('Préparation')
        #     if empty_line > 0:
        #         s = s[:empty_line]
        #         title = str(s).replace('\n', ' ')\
        #                       .replace('  ', ' ')\
        #                       .capitalize()\
        #                       .strip()
        print(f'title found by tesseract: {title}')
        if not title: # then try with easyocr results
            pic = './tmp/title.jpg'
            img = img.crop((cls.reader_result[1][0][0][0],\
                            cls.reader_result[1][0][0][1],\
                            cls.reader_result[1][0][2][0],\
                            cls.reader_result[1][0][2][1]\
                            ))
            img.save(pic)
            title = reader.readtext(image=pic, detail=0, low_text=.21, paragraph=True)
            title = ' '.join(title).capitalize()
        logger.info('title: %s', title)
        return title
    @classmethod
    def get_ingredients(cls, img):
        pic = './tmp/ingredients.jpg'
        for box in cls.reader_result[3:-1]:
            if 'Ingrédients' in box[1] and box[1].index('Ingrédients') == 0:
                crop_coordinates = (box[0][0][0], box[0][0][1], box[0][2][0], box[0][2][1])
                img = img.crop(crop_coordinates)
                img.save(pic)
                # print('---- easy ocr ----')
                # print(reader.readtext(image=pic, detail=0))
                ingredients_stream = pytesseract.image_to_string(img, lang='fra')
                # print('---- pytesseract ----')
                logger.info(ingredients_stream)
                # remove first line and put the rest in one line
                ingredients_stream = ' '.join(ingredients_stream.split(sep='\n')[1:])
                # ingredients_stream = ingredients_stream[ingredients_stream.find('\n')+2:]
                # put the stream in one line
                # ingredients_stream = ingredients_stream.replace('\n', ' ')
                # split
                ingredient_sep_list = '+-*°«e»'
                for sep in ingredient_sep_list:
                    ingredients_stream = ingredients_stream.replace(' ' + sep + ' ', '\n')
                ingredients_stream = ingredients_stream.replace("’", "'")
                logging.info('ingredients_stream: %s', ingredients_stream)
                # remove parenthesis
                s = ''
                parenthesis = False
                for i in ingredients_stream:
                    if i == '(':
                        parenthesis = True
                    elif i == ')':
                        parenthesis = False
                    elif not parenthesis:
                        s += i
                #remove double whistespace
                ingredients_stream = s.replace('  ', ' ')
                ingredients_list = str(ingredients_stream).split(sep='\n')
                break
        ingredients_list = [i.strip() for i in ingredients_list]
        parsed_ingredients_list = [parser.parse_stream(cls.spell_check(i))
                                   for i in ingredients_list]
        # parsed_ingredients_list = [parser.parse_stream(i.strip())[0] for i in ingredients_list]
        # return parsed_ingredients_list
        return parsed_ingredients_list


class Reader(ReaderInterface):
    """pick the right reader as per file location"""
    allowed_books = [config['DEFAULT']['CG_PICS'],\
                     config['DEFAULT']['BC_PICS'],\
                     config['DEFAULT']['EB_PICS']]

    def __init__(self, location: str, name: str) -> None:
        """Construct."""
        super().__init__()
        self.location = location
        self.name = name
    @classmethod
    def read(cls, location: str, name: str):
        if 'CG' in location: #== config['DEFAULT']['CG_PICS']:
            book_reader = CgReader
        elif 'BC' in location: #== config['DEFAULT']['BC_PICS']:
            book_reader = BcReader
        elif 'EB' in location: #== config['DEFAULT']['EB_PICS']:
            book_reader = EbReader
        else:
            raise ValueError('Unsupported book: ' + location)
        return book_reader.read(location=location, name=name)

if __name__ == '__main__':
    r, t, ing = Reader.read(config['DEFAULT']['EB_PICS'], '20250116_133249.jpg')
    print(r)
    print(t)
    print(ing)
