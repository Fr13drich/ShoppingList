from spellchecker import SpellChecker

spell = SpellChecker(language='fr')
spell.distance = 1
# find those words that may be misspelled
misspelled = spell.unknown(['500', 'g', 'de', 'petiles', 'carolles'])

for word in misspelled:
    # Get the one `most likely` answer
    print(spell.correction(word))

    # Get a list of `likely` options
    print(spell.candidates(word))

if 'carottes' in spell.edit_distance_2('carolles'):
    print('carottes youpee')