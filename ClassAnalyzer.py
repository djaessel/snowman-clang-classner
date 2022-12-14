# This Python file uses the following encoding: utf-8

import os
import re
import concurrent.futures

from specialvals import DEBUGMODE


class ClassAnalyzer:
    def __init__(self):
        pass


    def _findClassAttributesS(self, cls, classes):
        class_attributes = []
        for func in classes[cls]:
            for line in classes[cls][func]:
                mo = re.search("\*\(rdi [+ ]*[x0-9]*\)", line)
                if mo:
                    for g in mo.group():
                        class_attributes.append(g)

        with open(cls + ".endl", "w") as f:
            for attr in class_attributes:
                f.write(attr + "\n")

        return class_attributes


    def _help_findClassAttributes(self, classes, partNum, maxPartCount):
        packSize = int(len(classes) / maxPartCount)
        startIndex = int(packSize * partNum)
        endIndex = startIndex + packSize
        if partNum + 1 == maxPartCount:
            endIndex = len(classes.keys())
        keyList = list(classes.keys())[startIndex:endIndex]
        class_attributes = dict()
        for cls in keyList:
            class_attributes[cls] = self._findClassAttributesS(cls, classes)
        #print("Process", partNum, "finished!")
        return [len(keyList), class_attributes, os.getpid()]


    def findClassAttributes(self, classes):
        print("Analyzing - adding class imports...")

        maxProcs = int(os.cpu_count() * 0.75) # 16 -> 12, 8 -> 6, 4 -> 3
        with concurrent.futures.ProcessPoolExecutor() as executor:
            results = [executor.submit(self._help_findClassAttributes, classes, i, maxProcs) for i in range(maxProcs)]

        values_list = []
        for f in concurrent.futures.as_completed(results):
            values = f.result()
            values_list.append(values)

        class_attributes = dict()
        for vx in values_list:
            for fc in vx[1]:
                class_attributes[fc] = vx[1][fc]
            #print("Processed", vx[0], "classes with process", vx[2])

        print("Analyzing - adding class imports...DONE")

        return class_attributes
