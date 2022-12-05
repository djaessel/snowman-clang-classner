# This Python file uses the following encoding: utf-8

import os
# import multiprocessing as mp
from multiprocessing import Pool
import concurrent.futures
from os import getpid


class FunctionAnalyzer:
    def __init__(self):
        pass


    def _help_find_original_class(self, classes, partNum, maxPartCount):
        packSize = int(len(classes) / maxPartCount)
        startIndex = int(packSize * partNum)
        endIndex = startIndex + packSize
        if partNum + 1 == maxPartCount:
            endIndex = len(classes.keys())
        keyList = list(classes.keys())[startIndex:endIndex]
        fixed_classes = dict()
        for cls in keyList:
            fixed_classes[cls] = self._findOriginalClassS(cls, classes)
        #print("Process", partNum, "finished!")
        return [len(keyList), fixed_classes, os.getpid()]


    def _findOriginalClassS(self, cls, classes):
        print("Analyzing", cls, "...", end="", flush=True)
        tracerx = dict()
        fixed_class = dict()
        #found_something = False
        for func in classes[cls]:
            fixed_class[func] = []
            for line in classes[cls][func]:
                for cls2 in classes:
                    for func2 in classes[cls2]:
                        if "->" + func2 in line:
                            lll = "->" + func2
                            skip = False
                            for trx in tracerx:
                                if trx + lll in line:
                                    skip = True
                                    break
                            if not skip and (lll + "(" in line or lll + ";" in line or lll + ")" in line):
                                #if not found_something:
                                #    print(cls + ":", "[fixing 1]")
                                #    found_something = True
                                # print("FOUND TRACE:", cls2, func2, line.rstrip("\n"))
                                idx = line.index("->" + func2)
                                tmpx = line[0:idx].split(" ")
                                if len(tmpx) > 0:
                                    tmpx = tmpx[len(tmpx) - 1]
                                else:
                                    tmpx = ""
                                tmpx = tmpx.lstrip("&").lstrip("*") # remove extras # TODO: check again alter
                                if func2 in classes[cls]:
                                    line = line.replace(tmpx + "->" + func2, "this->" + func2)
                                elif len(tmpx) > 0 and not tmpx in tracerx:
                                    tracerx[tmpx] = cls2 # store actual class type for variable
                                else:
                                    print(cls2, ">", "ERROR: EMPTY RDI_OBJECT!", line.rstrip("\n")) # FIXME: fix this in original generation of these rdi->func() lines

                fixed_class[func].append(line)
        print("DONE")

        print("Fixing", cls, "...", end="", flush=True)
        for func in fixed_class:
            #found_something = False
            for i, line in enumerate(fixed_class[func]):
                for trace in tracerx:
                    if " " + trace + ";" in line:
                        linx = line.strip().split(";")[0]
                        declax = linx.split()
                        if len(declax) <= 2:
                            #if not found_something:
                            #    print(cls + ":", func, "[fixing 2.1]")
                            #    found_something = True
                            line = line.replace(linx + ";", tracerx[trace] + "* " + trace + ";") # make pointer for class for now!
                            if "STRUCT_" in declax[0]:
                                line = "  // was STRUCT before --> " + declax[0] + "\n" + line

                            fixed_class[func][i] = line
                            # print(cls + ":", "[fixing 2.1]", trace, line)
                    elif trace + " = " in line:
                        linx = line.lstrip()
                        linx = linx.split(" = ")[0]
                        if len(linx.split()) <= 2:
                            #if not found_something:
                            #    print(cls + ":", func, "[fixing 2.2]")
                            #    found_something = True
                            line = line.replace(linx + " = ", tracerx[trace] + "* " + trace + " = ") # make pointer for class for now!
                            fixed_class[func][i] = line
                            # print(cls + ":", "[fixing 2.2]", trace, line)
        print("DONE")
        return fixed_class




    def findOriginalClass(self, classes):
        print("Analyzing - finding original classes...")

        #maxProcs = int(os.cpu_count() * 0.5) # 16 -> 8
        #running_procs = []
        #for i in range(maxProcs):
        #    proc = mp.Process(target=self._help_find_original_class, args=(classes, i, maxProcs))
        #    proc.start()
        #    running_procs.append(proc)
        #for p in running_procs:
        #    p.join()
        #print(f"Finished with {maxProcs} threads!")

        maxProcs = os.cpu_count()
        with concurrent.futures.ProcessPoolExecutor() as executor:
            results = [executor.submit(self._help_find_original_class, args=(classes, i, maxProcs)) for i in range(maxProcs)]

        values_list = []
        for f in concurrent.futures.as_completed(results):
            values = f.result()
            values_list.append(values)

        fixed_classes = dict()
        for vx in values_list:
            for fc in vx[1]:
                fixed_classes[fc] = vx[1][fc]
            print("Processed", vx[0], "classes with process", vx[2])

        return fixed_classes

