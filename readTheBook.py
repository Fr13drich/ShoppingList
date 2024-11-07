"""Extract ingredients bill from my cooking book"""

import easyocr
reader = easyocr.Reader(['fr'])
try:
    result = reader.readtext(image='fritata.jpg', detail = 0, paragraph=True, y_ths=0.3 )
except:
    print('No text found')
# for detection in result:
#     print(detection[1])
print(result)

# from PIL import Image
# import pytesseract
# pytesseract.pytesseract.tesseract_cmd = r'C:\\Program Files\\Tesseract-OCR\\tesseract'

# Perform OCR on an image
# text = pytesseract.image_to_string('RecipesPics/BCp117.jpg', lang='fra')
# text = pytesseract.image_to_string('screenshot.png')
# print(text)


