import os
import json
import spacy

nlp = spacy.load("fr_core_news_md")#, disable=['parser', 'ner']

def load_all_recipe_files(location='./json/'):
    all_ingredients_dict = dict()
    for _root, _dirs, files in os.walk(location):
        for name in files:
            print(name)
            with open(location + name, 'r', encoding='utf-16') as recipe_file:
                recipe_dict = json.load(recipe_file)
                for k, v in recipe_dict['ingredients'].items():
                    all_ingredients_dict[k] = v
    return all_ingredients_dict
# tokens = nlp("chien chat")
# for token in tokens:
#     print(token.text, token.has_vector, token.vector_norm, token.is_oov)
# ingredient = nlp("moutarde au miel")
all_ingredients_dict = load_all_recipe_files()
ingredient = nlp("1 g de yaourt nature")
# ingredient = nlp("100 g de beurre")
# for token in ingredient:
#     print(token.text, token.lemma_, token.pos_, token.tag_, token.dep_,
#             token.shape_, token.is_alpha, token.is_stop)
s = set()
d = dict()
for k, v in all_ingredients_dict.items():
    l = nlp(' '.join([str(v), k]))
    s.add(l[1].lemma_)
    # seq = [token.pos_ for token in l]
    # seq_str = ' '.join(seq)
    # if seq_str not in s:
    #     d[seq_str] = 0
    #     s.add(seq_str)
    #     print(seq_str)
    #     print(str([token.lemma_ for token in l]))
    # d[seq_str] += 1
    # print(str([token.pos_ for token in l]))
    # print(str([token.dep_ for token in l]))
print(s)
# print(len(s))
# print(d)


# for category in categories:
    # print('Catégorie: ' + str(category) + '\t\t' + str(nlp(category).similarity(ingredient)))
# oranges = nlp("légume")
# apples_oranges = apples.similarity(oranges)
# oranges_apples = oranges.similarity(apples)
# assert apples_oranges == oranges_apples
# print(apples_oranges)

# from spacy.tokens import Span
# nlp = spacy.load("fr_core_news_sm")
# city_getter = lambda span: any(city in span.text for city in ("New York", "Paris", "Berlin"))
# Span.set_extension("has_city", getter=city_getter)
# doc = nlp("I like me in Autumn")
# assert doc[1:4]._.has_city
