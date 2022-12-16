# This Python file uses the following encoding: utf-8

import os
import re
import concurrent.futures

from specialvals import DEBUGMODE


class ClassAnalyzer:
    def __init__(self):
        pass


    def _findClassAttributesExternal(self, cls, classes):
        class_attributes = dict()

        myFuncs = [_ for _ in classes[cls]]

        for clsx in classes:
            if clsx != cls:
                for func in classes[clsx]:
                    active_attribs = []
                    for line in classes[clsx][func]:
                        tmo = line.rstrip("\n")
                        if tmo.find("//") >= 0:
                            tmo = tmo[0:tmo.index("//")]

                        if cls in line:
                            regex = '( '+cls+'[\*]* [a-z0-9_]+ = )'
                            mo = re.search(regex, tmo)
                            mo2 = re.search('([a-z0-9_]+\-\>[a-zA-Z_<>0-9\*]+\()', tmo)

                            nomo = ""
                            if mo:
                                tx = mo.group().strip().rstrip('=').rstrip()
                                tx = tx.split(' ')[1]
                                active_attribs.append(tx)
                                nomo = '"' + tx + '";"' + tmo.strip().rstrip(';')
                            elif mo2:
                                tx = mo2.group().strip()
                                txa = tx[tx.index('>') + 1:]
                                txa = txa[0:tx.index('(')-1]
                                if txa in myFuncs:
                                    nomo = '"' + tx.split('(')[0] + '";"' + tmo.strip().rstrip(';')

                            if len(nomo) > 0:
                                nomo += '";"' + clsx + '";"' + func + '"\n'
                                key = nomo.split(';')[0]
                                if not key in class_attributes:
                                    class_attributes[key] = nomo
                            else:
                                for frag in active_attribs:
                                    self._benulf(line, classes, class_attributes, clsx, cls, func, fragger=frag)
                        else:
                            for frag in active_attribs:
                                self._benulf(line, classes, class_attributes, clsx, cls, func, fragger=frag)

        # TODO: remove these later when attribs found!
        with open(cls + ".endl", "w") as f:
            for attr in class_attributes:
                f.write(class_attributes[attr])

        return [class_attributes[_] for _ in class_attributes]


    def _benulf(self, line, classes, class_attributes, cls, orgCls, func, fragger="rdi"):
        tmo = line.rstrip("\n")
        if tmo.find("//") >= 0:
            tmo = tmo[0:tmo.index("//")]

        mo = re.search("([\*]*[\(]*\("+fragger+"[ +]*[^a-zA-Z0-9]+[ \+\*\[\]\(\)x0-9a-zA-Z]+\)[\)]*)", tmo)
        mo2 = re.search("([ ]"+fragger+"[ +]*[ \;][ \+\*\[\]\(\)x0-9a-zA-Z=]*)", tmo)
        mo3 = re.search("(STRUCT_[0-9\*]+ [a-z0-9_]+ = "+fragger+"[;])", tmo)

        nomo = ""
        if mo:
            tx = self._clamsFix(tmo, mo.group())
            nomo = '"' + tx + '";"' + tmo.strip().rstrip(';')
        elif mo2:
            tx = self._clamsFix(tmo, mo2.group())
            nomo = '"' + tx + '";"' + tmo.strip().rstrip(';')
        elif fragger + "*" in tmo or fragger + " " in tmo or (fragger == "rdi" and "this->" in tmo and not tmo[tmo.index("this->") + 6:].split("(")[0] in classes[cls]):
            nomo = '"' + fragger + '";"' + tmo.strip().rstrip(';')

        if len(nomo) > 0:
            nomo += '";"' + cls + '";"' + func + '"\n'
            key = nomo.split(';')[0]
            if not key in class_attributes:
                class_attributes[key] = nomo

        if mo3:
            xa = tmo[tmo.index("STRUCT_"):]
            xa = xa[0:xa.index(" ")]
            nomo = '"' + xa + '";"' + tmo.strip().rstrip(';') + '";"' + cls + '";"' + func + '"\n'
            key = nomo.split(';')[0]
            if not key in class_attributes:
                class_attributes[key] = nomo


    def _findClassAttributesS(self, cls, classes):
        class_attributes = dict()
        for func in classes[cls]:
            for line in classes[cls][func]:
                self._benulf(line, classes, class_attributes, cls, cls, func)

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
            class_attributes[cls].extend(self._findClassAttributesExternal(cls, classes))
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
