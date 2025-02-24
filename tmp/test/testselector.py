import requests
import json
import lxml.etree as ET
from parsel import Selector
from load import load_all_recipe_files

def wikipedia(ingredient_name):
    """return a wikipedia url and a list of hashtag (str)"""
    r = requests.get(f'https://fr.wikipedia.org/w/index.php?search={str(ingredient_name).replace(" ", "+")}', allow_redirects=True, timeout=10)
    if r.status_code != 200:
        print(r.status_code)
        return None, None
    # print('https://fr.wikipedia.org/wiki/Poireau' in str(r.content))
    url= None
    wiki_ref = None
    for line in r.iter_lines():
        if 'https://fr.wikipedia.org/wiki/' in str(line):
            url = str(line)[str(line).index('https://fr.wikipedia.org/wiki/'):-3]
            wiki_ref = str(url).split(sep='/')[-1]
            # print(wiki_ref)
            break
    selector = Selector(text=str(r.content))
    hashtags = selector.xpath('/html/body/div[2]/div/div[3]/main/div[3]/div[3]/div[1]/p[1]/a/text()| /a/@title').getall()
    #if there is no result, try p2:
    if not hashtags:
        hashtags = selector.xpath('/html/body/div[2]/div/div[3]/main/div[3]/div[3]/div[1]/p[2]/a/text()| /a/@title').getall()
    return wiki_ref, hashtags


def google():
    for recipe in all_recipes:
        for ingredient in recipe.ingredients:
            name = ingredient[0].name
            if hashtags.get(name) is None:
                print(name)
                r = requests.get(f'https://www.google.com/search?q={name}', allow_redirects=True, timeout=10)
                #https://www.google.com/search?sca_esv=36b6736e49a6695f&sxsrf=AHTn8zo1sOyFZii8xBAH0qTsEOduAW0xOQ:1739195970532&q=i%27m+lucky+google+search&spell=1&sa=X&ved=2ahUKEwjOq5LwobmLAxVdVqQEHWYfEXwQBSgAegQIGhAB&biw=1536&bih=638&dpr=1.25
                print('fr.wikipedia.org' in str(r.content))
                # print(r.content)
                selector = Selector(text=str(r.content))
                link_to_wikipedia = selector.xpath('/html/body/div[3]/div/div[12]/div/div[2]/div/div[3]/div[2]/div/div[2]/div/div[2]/div/div[1]/div/div/div/div[1]/div/div/div/div/div/div/div[1]/div[1]/div/div[2]/div/div/div/div[1]/span/a/text()| /a/@title').getall()
                # link_to_wikipedia = selector.xpath('/html/body/div[3]/div/div[12]/div/div[2]/div/div[3]/div[2]/div/div[2]/div/div[2]/div/div[1]/div/div/div/div[1]/div/div/div/div/div/div/div[1]/div[1]/div/div[2]/div/div/div/a/@href| /a/@title').getall()
                print(link_to_wikipedia)

def duckduckgo():
    for recipe in all_recipes:
        for ingredient in recipe.ingredients:
            name = ingredient[0].name
            if hashtags.get(name) is None:
                r = requests.get(f'https://duckduckgo.com/?t=h_&q=wikipedia+{str(name).replace(" ", "+")}', allow_redirects=True, timeout=10)
                selector = Selector(text=str(r.content))
                print(r.text)
                link_to_wikipedia = selector.xpath('/html/body/div[2]/div[6]/div[4]/div/div/div/div[2]/section[1]/ol/li[1]/div/div/div[1]/section/div/p/a/@href').get()
                print(link_to_wikipedia)

# all_recipes = load_all_recipe_files('./tmp_json/') #('./tmp_json/')
# hashtags = dict()
# for recipe in all_recipes:
#     for ingredient in recipe.ingredients:
#         name = ingredient[0].name
#         if hashtags.get(name) is None:
#             wikipedia(name)
def add_ing(elt):
    wiki_ref, hashtaglist = wikipedia(elt)
    print(str(elt) + ' ' + str(wiki_ref))
    if not synonyme_dict.get(wiki_ref):
        synonyme_dict[wiki_ref] = set()
    synonyme_dict[wiki_ref].add(str(elt))

ing = ['poireau', 'poireaux', 'poireau']
synonyme_dict = dict()
for elt in ing:
    found = False
    for value in synonyme_dict.values():
        # print('elt: ' + str(elt) + 'value: ' + str(value))
        if elt in value:
            # print(str(elt) + ' already exist')
            found = True
            break
    if not found:
        add_ing(elt)

print(synonyme_dict)

