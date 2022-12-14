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
                tmo = line
                if tmo.find("//") >= 0:
                    tmo = tmo[0:tmo.index("//")]
                mo = re.search("[\*]*[\(]*\(rdi[ +]*[^a-zA-Z0-9]+[ \+\*\[\]\(\)x0-9a-zA-Z]+\)[\)]*", tmo)
                mo2 = re.search(" rdi[ +]*[^a-zA-Z0-9]+[ \+\*\[\]\(\)x0-9a-zA-Z]*", tmo)
                if mo:
                    class_attributes.append(mo.group() + ";" + tmo.lstrip("(").rstrip(")"))
                elif mo2:
                    class_attributes.append(mo2.group() + ";" + tmo.lstrip("(").rstrip(")"))
                elif "rdi*" in tmo or "rdi " in tmo or ("this->" in tmo and not tmo[tmo.index("this->") + 6:].split("(")[0] in classes[cls]):
                    class_attributes.append("rdi;" + tmo)

        with open(cls + ".endl", "w") as f:
            for attr in class_attributes:
                f.write(attr)

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
        print("Analyzing - adding class attributes...")

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

        print("Analyzing - adding class attributes...DONE")

        return class_attributes
