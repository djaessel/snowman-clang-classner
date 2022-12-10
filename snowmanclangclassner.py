#!/usr/bin/python3

import sys

from Classner import Classner
from ClassStorer import ClassStorer
from ClassReader import ClassReader
from Structer import Structer
from Stopwatch import Stopwatch
from ReinterpretAlter import ReinterpretAlter
from FunctionAnalyzer import FunctionAnalyzer
from specialvals import DEBUGMODE


def main():
    skip_class_write = False
    skip_reinterpret = False
    file_path = ""

    if len(sys.argv) > 1:
        file_path = sys.argv[1]
        if len(sys.argv) > 2:
            if sys.argv[2] == "-sc":
                skip_class_write = True
            if len(sys.argv) > 3:
                if sys.argv[3] == "-sr":
                    skip_reinterpret = True

    if file_path == "":
        print("No file given!")
        return

    stopwatch = Stopwatch()
    stopwatch.start()

    print("Processing cpp file ...\n")
    
    structer = Structer()
    structer.readStructs(file_path)

    classner = Classner()
    classner.readClassFunctions(file_path)
    classes = classner.get_classes()

    classStorer = ClassStorer(structer, classes)

    if not skip_class_write:
        classStorer.writeClasses()
        classStorer.update_new_cpp_file(file_path, classes)
    
    if not skip_reinterpret:
        reinterp = ReinterpretAlter()
        reinterp.removeReinterpret(classes)

    classReader = ClassReader()
    classReader.readClasses()
    modified_classes = classReader.get_classes()

    # remove default cpp file from class check - change later with different behavior
    path_array = file_path.split("/")
    file_name = path_array[len(path_array) - 1].split(".")[0]
    modified_classes.pop(file_name)

    analyzer = FunctionAnalyzer()
    fixed_classes = analyzer.findOriginalClass(modified_classes)

    classStorer.writeClassesJust(fixed_classes)

    print("\nProcessing DONE", flush=True)

    stopwatch.stop()
    stopwatch.printElapsed()



if __name__ == "__main__":
    main()

