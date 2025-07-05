"""test the ouput of read_the_book.py on one recipe"""
import os
import subprocess
EXT = '.exe' if os.name == 'nt' else '3'
#BCp384
p = subprocess.run(['python' + EXT,  './read_the_book.py', './test/'],
                           stdout=subprocess.PIPE, check=True)
# p = subprocess.run('pwd',stdout=subprocess.PIPE, check=True, shell=True)
# print(p.stdout)

def test_answer():
    """test the ouput of read_the_book.py on one BC recipe"""
    with open(file='./data/recipe_files/BCp384.json', mode='r', encoding='utf-16') as recipe_file:
        with open(file='./test/BCp384.json', mode='r', encoding='utf-16') as test_result:
            assert recipe_file.read() == test_result.read()
