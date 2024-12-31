"""Extract ingredients bills from my cooking book"""
import os
import json
from collections import Counter
from operator import itemgetter
import numpy as np
# import pytesseract
from PIL import Image, ImageOps, ImageEnhance
import easyocr
from classes import Recipe

reader = easyocr.Reader(['fr'])
def read_1_CGbook_recipe(pic):
    img = Image.open(pic)
    img = ImageOps.exif_transpose(img)
    img = ImageOps.grayscale(img)
    img.save("img.jpg")
    autocrop("img.jpg")
    text = reader.readtext(image="img.jpg", detail=1, paragraph=True)
    ref = 'CG' + str(text[0][1]).split(sep=' ', maxsplit=1)[0]
    title_coordinates = text[1][0][0][0], text[1][0][0][1], text[1][0][2][0], text[1][0][2][1]
    ingredients_coordinates = text[2][0][0][0], text[2][0][0][1], text[2][0][2][0], text[2][0][2][1]
    img = Image.open("img.jpg")
    img_title = img.crop(title_coordinates)
    img_ingredients = img.crop(ingredients_coordinates)
    img_title.save('img_title.jpg')
    img_ingredients.save('img_ingredients.jpg')
    name = reader.readtext(image="img_title.jpg", detail=1)[0][1]
    ingredients = reader.readtext(image="img_ingredients.jpg", detail=0, ycenter_ths=.5, width_ths=.7, height_ths=1)
    # print(reader.readtext(image="img_ingredients.jpg", detail=0, paragraph=True, y_ths=.03))
    return ref, name, ingredients

def read_1_BCbook_recipe(pic):
    """Return a list of ingredients and a list of instructions from a jpg."""
    img = Image.open(pic)
    img = ImageOps.exif_transpose(img)
    img = ImageOps.grayscale(img)
    img.save("img.jpg")
    autocrop("img.jpg")
    img = Image.open("img.jpg")
    # left or right page?
    img_footpage = img.crop((0, img.height * 0.98, img.width, img.height))
    img_footpage.save('img_footpage.jpg')
    try:
        txt_footpage = reader.readtext(image='img_footpage.jpg', text_threshold=.1)
    except:
        print('No text found')
    if max(txt_footpage, key=itemgetter(2))[0][0][0] < img_footpage.width/2:
        # if page number is written on the left side then the coordinates of the recipe are:
        recipe_coordinates =  img.width/3, 0, img.width, img.height
        # coordinates of the ingredients:
        ingredients_coordinates = img.width/20, 0, img.width/3, img.height*.85
    else:
        # right page
        recipe_coordinates = 0, 0, 2 * img.width/3, img.height
        ingredients_coordinates = 2 * img.width/3, 0, img.width*(19/20), img.height*.85
    img_recipe = img.crop(recipe_coordinates)
    img_recipe.save('img_recipe.jpg')
    img_ingredients = img.crop(ingredients_coordinates)
    # enhancer = ImageEnhance.Sharpness(img_ingredients)
    # img_ingredients = enhancer.enhance(50)
    enhancer = ImageEnhance.Contrast(img_ingredients)
    img_ingredients = enhancer.enhance(1)
    img_ingredients.save('img_ingredients.jpg')
    autocrop('img_ingredients.jpg')
    img = Image.open('img_ingredients.jpg')
    # merge_box_y = (img.height/img_ingredients.height) * .11
    # print(img.height)
    # print(img_ingredients.height)
    # print(merge_box_y)
    try:
        ingredients = reader.readtext(image="img_ingredients.jpg", detail=1, ycenter_ths=.5, width_ths=.7, height_ths=1)
        # ingredients = reader.readtext(image='img_ingredients.jpg', detail=1, paragraph=True) #, ycenter_ths=.5, y_ths=.1, x_ths=1)
        # ingredients = reader.readtext(image='img_ingredients.jpg', detail=1, paragraph=True, width_ths=.7, y_ths=.03, x_ths=1.5) #, add_margin=.2, text_threshold=.1, ycenter_ths=.13, width_ths=2, ycenter_ths=.13 , height_ths=1000
        # ingredients = reader.readtext(image='img_ingredients.jpg', detail=1, width_ths=.7, height_ths=.1)
        print(ingredients)
        ingredients = list(map(itemgetter(1), ingredients))
        print(ingredients)
    except:
        print('No text found')
    ref = 'BCp' + txt_footpage[0][1].split(sep=' ')[0]
    print('ref: ' + ref)
    autocrop('img_recipe.jpg')
    try:
        instructions = reader.readtext(image='img_recipe.jpg', detail=1, paragraph=True, height_ths=0.3) #, x_ths=0.002, min_size=200
        # name = reader.readtext(image='img_recipe.jpg', detail=0, min_size=1950) #entre 1900 et 2000
    except:
        print('No text found')
    # print(instructions)
    for box in instructions:
        if box[0][0][0] < 100:
            name = box[1]
            break
    print(name)
    return ref, name, ingredients

def autocrop(jpg):
    """crop where there is no text"""
    results = reader.readtext(image=jpg, detail=1, paragraph=True, x_ths=2000, y_ths=.2, text_threshold=.1, height_ths=1000)
    max_box = [10000, 10000, 0, 0]
    for box_coordinates in results:
        # print(max_box, box_coordinates[0])
        max_box[0] = min(max_box[0], int(box_coordinates[0][0][0]))
        max_box[1] = min(max_box[1], int(box_coordinates[0][0][1]))
        max_box[2] = max(max_box[2], int(box_coordinates[0][2][0]))
        max_box[3] = max(max_box[3], int(box_coordinates[0][2][1]))       
    img = Image.open(jpg)
    img = img.crop(tuple(max_box))
    img.save(jpg)

def parse_ingredients(raw_list_of_ingredients: list):
    """Return a dict(name, amount)"""
    print(raw_list_of_ingredients)
    result = {}
    for item in raw_list_of_ingredients:
        print(item)
        splitted_item = str(item).split(maxsplit=1)
        if str(splitted_item[0]).isnumeric():
            amount = int(splitted_item[0])
            name = str(splitted_item[1]).lower()
        else:
            amount = 1
            name = str(item).lower()
        result.update({name: amount})
    return result

def BC2json(location='./BCrecipesPics/'):
    """Browse the BC dir and OCRize each file"""
    for _root, _dirs, files in os.walk(location):
        for name in files:
            ref, name, ingredients = read_1_BCbook_recipe(location + name)
            parsed_ingredients = parse_ingredients(ingredients)
            outfile = 'json/' + ref + '.json'
            print(name)
            if os.path.exists(outfile):
                if input(outfile + " already exists. Should I overwrite?: ") != 'y':
                    continue
            with open(outfile, 'w', encoding='utf-16') as outfile:
                json.dump({'ref': ref, 'name':name, 'ingredients':parsed_ingredients}, outfile, indent=2, ensure_ascii=False)

def pics2json(location='./CGrecipesPics/'):
    """Browse the CG dir and OCRize each file"""
    for _root, _dirs, files in os.walk(location):
        for name in files:
            ref, name, ingredients = read_1_CGbook_recipe(location + name)
            parsed_ingredients = parse_ingredients(ingredients)
            outfile = 'json/' + ref + '.json'
            print(str(ref) + ', ' + str(name))
            print(parsed_ingredients)
            if os.path.exists(outfile):
                if input(outfile + " already exists. Should I overwrite?: ") != 'y':
                    continue
            with open(outfile, 'w', encoding='utf-16') as outfile:
                json.dump({'ref': ref, 'name':name, 'ingredients':parsed_ingredients}, outfile, indent=2, ensure_ascii=False)

BC2json()
