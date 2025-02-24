"""Extract title and ingredients from pictures"""
import configparser
from abc import ABC, abstractmethod
from operator import itemgetter
from PIL import Image, ImageOps, ImageEnhance
import easyocr

config = configparser.ConfigParser()
config.read('./config.cfg')
reader = easyocr.Reader(['fr'])

class ReaderInterface(ABC):
    """Generic class to read text from a jpg picture."""

    allowed_books = []
    allowed_extensions = ['jpg']
    footpage_workfile = 'tmp/img_footpage.jpg'
    title_workfile = './tmp/img_recipe.jpg'
    ingredients_workfile = './tmp/img_ingredients.jpg'
    reader_result = None
    left = True

    @classmethod
    def can_parse(cls, location, name) -> bool:
        """Can I parse the picture?."""
        ext = name.split('.')[-1]
        # book = location in cls.allowed_books
        # print(book, cls.allowed_books, book in cls.allowed_books)
        return location in cls.allowed_books and ext in cls.allowed_extensions
    @staticmethod
    def autocrop(jpg):
        """Crop where there is no text."""
        results = reader.readtext(image=jpg, detail=1, paragraph=True, x_ths=2000, y_ths=.2,\
                                  text_threshold=.1, height_ths=1000)
        max_box = [10000, 10000, 0, 0]
        for box_coordinates in results:
            max_box[0] = min(max_box[0], int(box_coordinates[0][0][0]))
            max_box[1] = min(max_box[1], int(box_coordinates[0][0][1]))
            max_box[2] = max(max_box[2], int(box_coordinates[0][2][0]))
            max_box[3] = max(max_box[3], int(box_coordinates[0][2][1]))
        img = Image.open(jpg)
        img = img.crop(tuple(max_box))
        img.save(jpg)

    @classmethod
    def image_preprocessing(cls, pic):
        img = Image.open(pic)
        img = ImageOps.exif_transpose(img)
        img = ImageOps.grayscale(img)
        img.save("tmp/img.jpg")
        cls.autocrop("tmp/img.jpg")
        return "tmp/img.jpg"
    @classmethod
    def parse_ingredients(cls, raw_list_of_ingredients: list):
        """Return a dict(name, amount)"""
        result = {}
        for item in raw_list_of_ingredients:
            # print(item)
            splitted_item = str(item).split(maxsplit=1)
            if str(splitted_item[0]).isnumeric():
                amount = int(splitted_item[0])
                name = str(splitted_item[1]).lower()
            else:
                amount = 1
                name = str(item).lower()
            result.update({name: amount})
        return result
    @classmethod
    @abstractmethod
    def parse(cls, location, name):
        pass
    @classmethod
    @abstractmethod
    def get_title(cls, img):
        pass
    @classmethod
    @abstractmethod
    def get_ingredients(cls, img):
        pass
    @classmethod
    @abstractmethod
    def get_ref(cls, img):
        pass

class BcReader(ReaderInterface):
    """Read pictures from 'Bien cuisiner'."""
    allowed_books = [config['DEFAULT']['BC_PICS']]

    def __init__(self, location: str, name: str) -> None:
        """Construct."""
        super().__init__()
        self.location = location
        self.name = name
        self.left = True
    @classmethod
    def parse(cls, location: str, name: str):
        """Ingest the file."""
        if not cls.can_parse(location, name):
            raise ValueError('Cannot parse exception.')
        pic = cls.image_preprocessing('./' + location + '/' + name)
        img = Image.open(pic)
        ref = cls.get_ref(img)
        title = cls.get_title(img)
        ingredients = cls.get_ingredients(img)
        return ref, title, ingredients
    @classmethod
    def get_ref(cls, img):
        img_footpage = img.crop((0, img.height * 0.98, img.width, img.height))
        img_footpage.save(cls.footpage_workfile)
        try:
            reader_result = reader.readtext(image=cls.footpage_workfile, text_threshold=.1)
        except ValueError():
            print('No text found')
        if max(reader_result, key=itemgetter(2))[0][0][0] < img_footpage.width/2:
            cls.left = True
        else:
            cls.left = False
        return 'BCp' + str(reader_result[0][1]).split(sep=' ', maxsplit=1)[0]
    @classmethod
    def get_title(cls, img):
        if cls.left:
            recipe_coordinates =  img.width/3, 0, img.width, img.height
        else:
            recipe_coordinates = 0, 0, 2 * img.width/3, img.height
        img_recipe = img.crop(recipe_coordinates)
        img_recipe.save(cls.title_workfile)
        cls.autocrop(cls.title_workfile)
        try:
            instructions = reader.readtext(image=cls.title_workfile, detail=1, paragraph=True,\
                                           y_ths=.1, height_ths=0.2, min_size=50) #, x_ths=0.002, min_size=200
        except ValueError():
            print('No text found')
        for box in instructions:
            if box[0][0][0] < 100:
                title = box[1]
                break
        return title
    @classmethod
    def get_ingredients(cls, img):
        if cls.left:
            ingredients_coordinates = 0, 0, img.width/3, img.height*.85
        else:
            ingredients_coordinates = 2 * img.width/3, 0, img.width, img.height*.85
        img_ingredients = img.crop(ingredients_coordinates)
        enhancer = ImageEnhance.Contrast(img_ingredients)
        img_ingredients = enhancer.enhance(1)
        img_ingredients.save(cls.ingredients_workfile)
        cls.autocrop(cls.ingredients_workfile)
        # img = Image.open(self.ingredients_workfile)
        try:
            ingredients = reader.readtext(image=cls.ingredients_workfile, detail=1,\
                                          paragraph=True, y_ths=.5, height_ths=5)
            ingredients = list(map(itemgetter(1), ingredients))
        except ValueError():
            print('No text found')
        return ingredients

class CgReader(ReaderInterface):
    """Read pictures from 'Café gourmand'."""

    allowed_books = [config['DEFAULT']['CG_PICS']]

    def __init__(self, location: str, name: str) -> None:
        """Construct."""
        super().__init__()
        self.location = location
        self.name = name
    @classmethod
    def parse(cls, location: str, name: str):
        """Ingest the file."""
        if not cls.can_parse(location, name):
            raise ValueError('Cannot parse exception.')
        pic = cls.image_preprocessing('./' + location + '/' + name)
        cls.reader_result = reader.readtext(image=pic, detail=1, paragraph=True)
        img = Image.open(pic)
        ref = cls.get_ref(img)
        title = cls.get_title(img)
        ingredients = cls.get_ingredients(img)
        return ref, title, ingredients
    @classmethod
    def get_ref(cls, img):
        return 'CGp' + str(cls.reader_result[0][1]).split(sep=' ', maxsplit=1)[0]
    @classmethod
    def get_title(cls, img):
        title_coordinates = cls.reader_result[1][0][0][0], cls.reader_result[1][0][0][1],\
            cls.reader_result[1][0][2][0], cls.reader_result[1][0][2][1]
        img_title = img.crop(title_coordinates)
        img_title.save(cls.title_workfile)
        title = reader.readtext(image=cls.title_workfile, detail=1)[0][1]
        return title
    @classmethod
    def get_ingredients(cls, img):
        ingredients_coordinates = cls.reader_result[2][0][0][0], cls.reader_result[2][0][0][1],\
            cls.reader_result[2][0][2][0], cls.reader_result[2][0][2][1]
        img_ingredients = img.crop(ingredients_coordinates)
        img_ingredients.save(cls.ingredients_workfile)
        ingredients = reader.readtext(image=cls.ingredients_workfile, detail=0,\
                                      ycenter_ths=.5, width_ths=.7, height_ths=1)
        return ingredients

class Reader(ReaderInterface):
    allowed_books = [config['DEFAULT']['CG_PICS'], config['DEFAULT']['BC_PICS']]

    def __init__(self, location: str, name: str) -> None:
        """Construct."""
        super().__init__()
        self.location = location
        self.name = name
    @classmethod
    def parse(cls, location: str, name: str):
        if location == config['DEFAULT']['CG_PICS']:
            book_reader = CgReader
        elif location == config['DEFAULT']['BC_PICS']:
            book_reader = BcReader
        else:
            raise ValueError('Unsupported book: ' + location)
        return book_reader.parse(location=location, name=name)

if __name__ == '__main__':
    r, t, i = Reader.parse('./BCrecipesPics/', '20250131_142140.jpg')
    print(r)
    print(t)
    print(i)
