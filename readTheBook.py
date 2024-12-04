"""Extract ingredients bills from my cooking book"""
import os
import json
from collections import Counter
from operator import itemgetter
import numpy as np
# import pytesseract
from PIL import Image, ImageOps, ImageEnhance
import easyocr
import cv2
from classes import Recipe


def read_1_BCbook_recipe(pic):
    """Return a list of ingredients and a list of instructions from a jpg."""
    reader = easyocr.Reader(['fr'])
    #improve image with cv
    # img = cv2.imread(pic)
    # #Apply dilation and erosion
    # kernel = np.ones((2, 2), np.uint8)
    # img = cv2.dilate(img, kernel, iterations=1)
    # img = cv2.erode(img, kernel, iterations=1)
    # cv2.imwrite("new1.jpg", img)
    #improve image with pillow
    img = Image.open(pic)
    img = ImageOps.exif_transpose(img)
    img = ImageOps.grayscale(img)
    

    img.save("new1.jpg")
    # left or right page?
    img_footpage = img.crop((0, img.height * 0.95, img.width, img.height))
    img_footpage.save('img_footpage.jpg')
    try:
        txt_footpage = reader.readtext(image='img_footpage.jpg', text_threshold=.7)
    except:
        print('No text found')

    # print(txt_footpage)
    # print(max(txt_footpage, key=itemgetter(2))[0][0][0])
    if max(txt_footpage, key=itemgetter(2))[0][0][0] < img_footpage.width/2:
        # left page then the coordinates of the receipe are:
        xr1, yr1, xr2, yr2 = img.width/3, 0, img.width, img.height
        # coordinates of the ingredients:
        xi1, xi2, yi1, yi2 = img.width/14, 0, img.width/3, img.height*.8
    else:
        # right page
        xr1, yr1, xr2, yr2 = 0, 0, 2 * img.width/3, img.height
        xi1, xi2, yi1, yi2 = 2 * img.width/3, 0, img.width*.95, img.height*.8

    img_recipe = img.crop((xr1, yr1, xr2, yr2))
    img_recipe.save('img_recipe.jpg')
    img_ingredients = img.crop((xi1, xi2, yi1, yi2))
    # enhancer = ImageEnhance.Sharpness(img_ingredients)
    # img_ingredients = enhancer.enhance(50)
    enhancer = ImageEnhance.Contrast(img_ingredients)
    img_ingredients = enhancer.enhance(1)
    img_ingredients.save('img_ingredients.jpg')
    try:
        ingredients = reader.readtext(image='img_ingredients.jpg', detail=0, paragraph=True, x_ths=2000, y_ths=.2, text_threshold=.1, height_ths=1000) #, ycenter_ths=.13
        # ingredients = reader.readtext(image='img_ingredients.jpg', detail=0, width_ths=1000, slope_ths=.100)
    except:
        print('No text found')

    print(ingredients)
    # ref = 'BCp' + ingredients[-1].split(sep=' ')[1]   
    ref = 'BCp' + txt_footpage[0][1].split(sep=' ')[0]
    print('txt_footpage:')
    print(txt_footpage)
    print('ref: ' + ref)

    try:
        instructions = reader.readtext(image='img_recipe.jpg', detail=0, paragraph=True, height_ths=0.3, x_ths=0.002) #, x_ths=0.2
    except:
        print('No text found')
    # print(instructions)
    return ref, ingredients, instructions

def parse_ingredients(raw_list_of_ingredients: list):
    """Return a dict(name, amount)"""
    # print(raw_list_of_ingredients)    
    result = dict()
    for item in raw_list_of_ingredients:
        splitted_item = str(item).split(sep=' ')
        if str(splitted_item[0]).isnumeric():
            amount = int(splitted_item[0])
            name = item[str(amount).__len__() + 1:]            
        else:
            amount = 1
            name = item
        # print("Name: " + name + " amount: " + str(amount))
        result.update({name: amount})
        # result.append((name,amount))
    return result

def read_files_from_dir(dir='./BCrecipesPics/'):
    """Browse the BC dir and OCRize each file"""
    for root, _dirs, files in os.walk(dir):
        # imgs = [os.path.join(root, name) for name in files]
        for name in files:
            ref, ingredients, instructions = read_1_BCbook_recipe(dir + name)
            parsed_ingredients = parse_ingredients(ingredients)
            outfile = 'json/' + ref + '.json'
            if os.path.exists(outfile):
                if input(outfile + " already exists. Should I overwrite?: ") != 'y':
                    continue
            with open(outfile, 'w') as outfile:
                json.dump(parsed_ingredients, outfile, indent=2, ensure_ascii=False)

read_files_from_dir()


# ref, ingredients, instructions = read_1_BCbook_recipe('BCrecipesPics/20241108_140646.jpg')
# parsed_ingredients = parse_ingredients(ingredients)
# a = Recipe(ref, parsed_ingredients)
# print(a.ingredients)

# ref, ingredients, instructions = read_1_BCbook_recipe('BCrecipesPics/20241130_120016.jpg')
# parsed_ingredients = parse_ingredients(ingredients)
# b = Recipe(ref, parsed_ingredients)
# print(b.ingredients)

# Cdict = Counter(a.ingredients) + Counter(b.ingredients)
# print(Cdict)

# with open('a.json', 'w') as outfile:
#         json.dump(a.ingredients, outfile, indent=2)

# with open('ab.json', 'w') as outfile:
#         json.dump(Cdict, outfile, indent=2)