#!/usr/bin/python3

import os
import sys

from Classner import Classner
from ClassStorer import ClassStorer
from ClassReader import ClassReader
from Structer import Structer
from Stopwatch import Stopwatch
from ReinterpretAlter import ReinterpretAlter
from FunctionAnalyzer import FunctionAnalyzer
from ClassAnalyzer import ClassAnalyzer
from Gotogo import Gotogo

from specialvals import DEBUGMODE


def main():
    skip_class_write = False
    skip_reinterpret = False
    skip_analyze = False
    skip_remove_included = False
    skip_class_analyze = False
    file_path = ""

    if len(sys.argv) > 1:
        file_path = sys.argv[1]
        if len(sys.argv) > 2:
            if "-sc" in sys.argv:
                skip_class_write = True
            if "-sr" in sys.argv:
                skip_reinterpret = True
            if "-sa" in sys.argv:
                skip_analyze = True
            if "-si" in sys.argv:
                skip_remove_included = True
            if "-sa2" in sys.argv:
                skip_class_analyze = True
            if "--skip-all" in sys.argv:
                skip_class_write = True
                skip_reinterpret = True
                skip_analyze = True
                skip_remove_included = True
                skip_class_analyze = True

    if file_path == "":
        print("No file given!")
        return

    stopwatch = Stopwatch()
    stopwatch.start()

    print("Processing cpp file ...\n")
    
    structer = Structer()
    structer.readStructs(file_path)

    classner = Classner()
    classner.readClassFunctions(file_path, skip_class_write)
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

    if not skip_analyze:
        analyzer = FunctionAnalyzer()
        fixed_classes = analyzer.findOriginalClass(modified_classes)
        class_includes = analyzer.addUsedClassImports(fixed_classes, classes)
        classStorer.writeClassesJust(fixed_classes, class_includes)

    if not skip_remove_included:
        os.system("cd generated_classes && python3 remove_included.py")

    if not skip_class_analyze:
        classAnalyzer = ClassAnalyzer()
        classAnalyzer.findClassAttributes(modified_classes)

    gotogo = Gotogo()
    gotogo.processClasses(modified_classes)
    os.system("mv *_*.cpp endl/class_info/") # FIXME: change later

    print("\nProcessing DONE", flush=True)

    stopwatch.stop()
    stopwatch.printElapsed()



if __name__ == "__main__":
    main()

