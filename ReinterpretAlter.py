# This Python file uses the following encoding: utf-8

from ClassStorer import ClassStorer


class ReinterpretAlter:
    def __init__(self):
        pass


    def removeReinterpret(self, classList):
        print("Removing interpret statements...")

        for cls in classList:
            lines = []
            print(cls, "removing interprets...", end="", flush=True)
            with open(ClassStorer.export_dir + "/" + cls + ".cpp") as fr:
                for line in fr:
                    indy = line.find("reinterpret_cast<")
                    while indy >= 0:
                        #clammer = 1 # include removed clammer
                        #for c in line[0:indy]:
                        #    if c == "(":
                        #        clammer += 1
                        tempx = len(line[indy:].split("(")[0]) + 1 #2 # clammer plus exclusive end
                        line = line[0:indy] + line[tempx:] # remove all in between
                        #closeClammer = 0
                        #checls = -1
                        #iff = len(line) - 1
                        #for c in line[iff:0:-1]:
                        #    if c == ")":
                        #        closeClammer += 1
                        #    if closeClammer == clammer:
                        #        checls = iff
                        #        break
                        #    iff -= 1
                        #line = line[0:checls] + line[checls + 1:] # remove closing clammer
                    lines.append(line)

            with open(ClassStorer.export_dir + "/" + cls + ".cpp", "w") as fw:
                for line in lines:
                    fw.write(line + "\n")

            print("DONE")
