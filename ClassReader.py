# This Python file uses the following encoding: utf-8

import os
from ClassStorer import ClassStorer
from collections import OrderedDict
from specialvals import *


class ClassReader:
    def __init__(self):
        pass


    def get_classes(self):
        return OrderedDict(sorted(self.classes.items())) # return sorted dict but keep unsorted in original


    def readClasses(self):
        self.classes = dict()

        classCodeFiles = [file for file in os.listdir(ClassStorer.export_dir) if ".cpp" in file]
        for file in classCodeFiles:
            class_name = file.split(".")[0] # remove file extension to get class name for now
            self.classes[class_name] = dict()

            with open(ClassStorer.export_dir + "/" + file) as fr:
                func_body = False
                cur_func_name = None
                for line in fr:
                    if class_name + "::" in line:
                        cur_func_name = line.split("::")[1].split("(")[0]
                        self.classes[class_name][cur_func_name] = []
                        func_body = True
                    elif func_body:
                        self.classes[class_name][cur_func_name].append(line)
                        if line.rstrip("\n") == "}":
                            cur_func_name = None
                            func_body = False


