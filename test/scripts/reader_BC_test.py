"""test the ouput of read_the_book.py on one BC recipe"""
import subprocess
#BCp384
p = subprocess.run('python.exe ./read_the_book.py ./test/',
                           stdout=subprocess.PIPE, check=True)

def test_answer():
    """test the ouput of read_the_book.py on one BC recipe"""
    with open(file='./data/recipe_files/BCp384.json', mode='r', encoding='utf-16') as recipe_file:
        with open(file='./test/BCp384.json', mode='r', encoding='utf-16') as test_result:
            assert recipe_file.read() == test_result.read()
