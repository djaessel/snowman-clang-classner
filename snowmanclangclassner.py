#!/usr/bin/python3

import sys

from Classner import Classner
from ClassStorer import ClassStorer
from Structer import Structer
from Stopwatch import Stopwatch
from ReinterpretAlter import ReinterpretAlter


def main():
    skip_class_write = False
    file_path = ""
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
        if len(sys.argv) > 2:
            if sys.argv[2] == "-sc":
                skip_class_write = True

    if file_path == "":
        print("No file given!")
        return

    stopwatch = Stopwatch()
    stopwatch.start()

    print("Processing cpp file ...\n")
    
    structer = Structer()
    structer.readStructs(file_path)
    stopwatch.printElapsed()

    classner = Classner()
    classner.readClassFunctions(file_path)
    classes = classner.get_classes()
    stopwatch.printElapsed()

    if not skip_class_write:
        classStorer = ClassStorer(structer, classes)
        classStorer.writeClasses()
    
    reinterp = ReinterpretAlter()
    reinterp.removeReinterpret(classes)

    print("Processing DONE", flush=True)

    stopwatch.stop()
    stopwatch.printElapsed()



if __name__ == "__main__":
    main()

