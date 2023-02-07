from distutils.core import setup, Extension

# Hint:
# python3 -m cython -o main.c -I /usr/include/python3.8/ main.py

module1 = Extension('Stopwatch', sources = ['Stopwatch.c'])
module2 = Extension('ClassStorer', sources = ['ClassStorer.c'])
module3 = Extension('Classner', sources = ['Classner.c'])
module4 = Extension('Structer', sources = ['Structer.c'])
module5 = Extension('snowmanclangclassner', sources = ['snowmanclangclassner.c'])

setup (name = 'PackageName',
        version = '1.0',
        description = 'This is a demo package',
        ext_modules = [module1,module2,module3,module4,module5])
