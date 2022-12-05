# This Python file uses the following encoding: utf-8

import os
import multiprocessing as mp


class FunctionAnalyzer:
    def __init__(self):
        pass


    def _help_find_original_class(self, classes, fixed_classes, partNum, maxPartCount):
        packSize = int(len(classes) / maxPartCount)
        startIndex = int(packSize * partNum)
        endIndex = startIndex + packSize
        if partNum + 1 == maxPartCount:
            endIndex = len(classes.keys())
        keyList = list(classes.keys())[startIndex:endIndex]
        for cls in keyList:
            self._findOriginalClassS(cls, classes, fixed_classes)
        #print("Process", partNum, "finished!")


    def _findOriginalClassS(self, cls, classes, fixed_classes):
        print("Analyzing", cls, "...", end="", flush=True)
        tracerx = dict()
        fixed_classes[cls] = dict()
        #found_something = False
        for func in classes[cls]:
            fixed_classes[cls][func] = []
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

                fixed_classes[cls][func].append(line)
        print("DONE")

        print("Fixing", cls, "...", end="", flush=True)
        for func in fixed_classes[cls]:
            #found_something = False
            for i, line in enumerate(fixed_classes[cls][func]):
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

                            fixed_classes[cls][func][i] = line
                            # print(cls + ":", "[fixing 2.1]", trace, line)
                    elif trace + " = " in line:
                        linx = line.lstrip()
                        linx = linx.split(" = ")[0]
                        if len(linx.split()) <= 2:
                            #if not found_something:
                            #    print(cls + ":", func, "[fixing 2.2]")
                            #    found_something = True
                            line = line.replace(linx + " = ", tracerx[trace] + "* " + trace + " = ") # make pointer for class for now!
                            fixed_classes[cls][func][i] = line
                            # print(cls + ":", "[fixing 2.2]", trace, line)
        print("DONE")




    def findOriginalClass(self, classes):
        fixed_classes = dict()
        print("Analyzing - finding original classes...")

        maxProcs = int(os.cpu_count() * 0.5) # 16 -> 8
        running_procs = []
        for i in range(maxProcs):
            proc = mp.Process(target=self._help_find_original_class, args=(classes, fixed_classes, i, maxProcs))
            proc.start()
            running_procs.append(proc)
        for p in running_procs:
            p.join()
        print(f"Finished with {maxProcs} threads!")

        return fixed_classes

