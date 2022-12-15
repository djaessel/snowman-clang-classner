# This Python file uses the following encoding: utf-8

import os
import re
import concurrent.futures

from specialvals import DEBUGMODE


class ClassAnalyzer:
    def __init__(self):
        pass


    def _findClassAttributesS(self, cls, classes):
        class_attributes = dict()
        for func in classes[cls]:
            for line in classes[cls][func]:
                tmo = line.rstrip("\n")
                if tmo.find("//") >= 0:
                    tmo = tmo[0:tmo.index("//")]

                mo = re.search("[\*]*[\(]*\(rdi[ +]*[^a-zA-Z0-9]+[ \+\*\[\]\(\)x0-9a-zA-Z]+\)[\)]*", tmo)
                mo2 = re.search(" rdi[ +]*[^a-zA-Z0-9]+[ \+\*\[\]\(\)x0-9a-zA-Z]*", tmo)
                mo3 = re.search("(STRUCT_[0-9\*]+ [a-z0-9_]+ = rdi[;])", tmo)

                nomo = ""
                if mo:
                    tx = self._clamsFix(tmo, mo.group())
                    nomo = '"' + tx + '";"' + tmo.strip().rstrip(';') + '"\n'
                elif mo2:
                    tx = self._clamsFix(tmo, mo2.group())
                    nomo = '"' + tx + '";"' + tmo.strip().rstrip(';') + '"\n'
                elif "rdi*" in tmo or "rdi " in tmo or ("this->" in tmo and not tmo[tmo.index("this->") + 6:].split("(")[0] in classes[cls]):
                    nomo = '"rdi";"' + tmo.strip().rstrip(';') + '"\n'

                if len(nomo) > 0:
                    key = nomo.split(';')[0]
                    if not key in class_attributes:
                        class_attributes[key] = nomo

                if mo3:
                    xa = tmo[tmo.index("STRUCT_"):]
                    xa = xa[0:xa.index(" ")]
                    nomo = '"' + xa + '";"' + tmo.strip().rstrip(';') + '"\n'
                    key = nomo.split(';')[0]
                    if not key in class_attributes:
                        class_attributes[key] = nomo


        with open(cls + ".endl", "w") as f:
            for attr in class_attributes:
                f.write(class_attributes[attr])

        return [class_attributes[_] for _ in class_attributes]


    def _clamsFix(self, allText, text):
        clam = 0
        lok = False
        for c in text:
            if c == "(":
                clam += 1
                lok = True
            elif c == ")":
                clam -= 1
        tx = text.rstrip("\n").strip()
        xon = allText[allText.index(tx) + len(tx):]
        for c in xon:
            if c == "(":
                clam += 1
            elif c == ")":
                clam -= 1
            tx += c
            if clam <= 0:
                break
        while clam < 0:
            rev_tx = tx[::-1]
            lastIndex = len(tx) - rev_tx.index(")") - 1
            tx = tx[0:lastIndex]
            clam += 1
        tx = tx.rstrip(';')
        lok = lok and tx[len(tx) - 1] != ")"
        if lok:
            rev_tx = tx[::-1]
            x = 0
            for c in rev_tx:
                if c == ")":
                    break
                x += 1
            tx = tx[0:len(tx) - x]
        return tx


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
