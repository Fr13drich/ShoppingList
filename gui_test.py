""""Test gui. Load a menu. Merge ingredients."""
from gui import App

EXPECTED_OUTPUT = """

ail: 13 gousse
beurre: 470 gramme
cacao en poudre: 180 gramme
citron: 1 p
cognac: 50 millilitre
concombre: 2 p
confiture de pêche: 2 cuil. à soupe
cuil. à soupe de thym séché: 1 p
cuisses de poulet: 16 p
eau: 960 millilitre
eau tiède: 1300 millilitre
farine: 590 gramme
farine de seigle: 500 gramme
farine de type 55: 1000 gramme
gingembre de 2,5 cm: 2 morceau
gingembre en poudre: 1 cuil. à soupe
gros oignon: 1 p
gros sel: 2 cuil. à café
huile: 4 cuil. à soupe
huile d'olive vierge extra: 14 cuil. à soupe
huile végétale: 4 cuil. à soupe 30 millilitre
ketchup: 500 millilitre
lait: 1000 millilitre
lamelles de gingembre en saumure: 4 cuil. à soupe
levure chimique: 1 cuil. à café
levure fraîche de boulanger: 40 gramme
marjolaine séchée: 1 cuil. à café
mayonnaise: 2 cuil. à soupe 8 cuil. à café
moutarde au miel: 1 cuil. à soupe
moutarde forte: 2 cuil. à soupe
nori: 8 feuille
oignons: 260 gramme
oignons verts: 2 p
orange: 1 p
paprika doux: 1 cuil. à soupe 2 cuil. à café
pennes: 400 gramme
pepperoncinis ou petits piments rouges: 3 p
persil frais: 1 botte
petits pains de la veille: 4 p
poivre: 3 pincée
poivre noir: 6 pincée
poivron séché: 1 p
pommes de terre: 800 gramme
poudre d'amandes: 150 gramme
poudre de curry: 1 cuil. à soupe
riz pour sushis: 600 gramme
romarin frais: 1 brin
sauce barbecue: 300 millilitre
sauce de soja: 19 cuil. à soupe
sauce worcester: 1 cuil. à café
sel: 12 pincée 1 pincee
sirop d'érable: 2 cuil. à soupe
spaghettis: 500 gramme
sucre: 10 cuil. à soupe 2 cuil. à café 450 gramme
sucre vanille: 50 gramme
surimi: 200 gramme
tabasco: 1 cuil. à café
thon en saumure: 150 gramme
viande de bœuf hachée: 750 gramme
vinaigre de riz: 8 cuil. à soupe
wasabi: 2 cuil. à café
yaourt nature: 2 cuil. à soupe
œufs: 23 p

"""
app = App()
app.recipes_frame.load_menu('./data/listes/avril.json')
app.recipes_frame.generate_shopping_list()

assert app.ingredients_frame.merged_ingredients.get('1.0', 'end') == EXPECTED_OUTPUT
print(app.ingredients_frame.merged_ingredients.get('1.0', 'end'))
