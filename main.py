#!/usr/bin/python3

import sys

from Classner import Classner
from ClassStorer import ClassStorer
from Structer import Structer
from Stopwatch import Stopwatch


def main():
    file_path = ""
    if len(sys.argv) > 1:
        file_path = sys.argv[1]

    if file_path == "":
        print("No file given!")
        return

    stopwatch = Stopwatch()
    stopwatch.start()

    print("Processing cpp file ...", end=" ")
    
    structer = Structer()
    structer.readStructs(file_path)

    classner = Classner()
    classner.readClassFunctions(file_path)
    classes = classner.get_classes()

    classStorer = ClassStorer(structer, classes)
    classStorer.writeClasses()
    
    print("DONE")

    stopwatch.stop()
    stopwatch.printElapsed()



if __name__ == "main":
    main()

