# This Python file uses the following encoding: utf-8


from specialvals import DEBUGMODE


class Gotogo:
    def __init__(self):
        pass


    def collect(self, classFunc):
        gotos = dict()
        adresses = dict()
        lastAddress = None
        for index, line in enumerate(classFunc):
            lxy = 0
            for c in line:
                if c != ' ':
                    break
                lxy += 1
            line = line.rstrip('\n').strip()
            if line.startswith("goto "):
                addressx = line.split(';')[0][5:]
                gotos[addressx] = [index, lxy]
            elif line.startswith("addr") and line.endswith(":"):
                addressx = line.rstrip(':')
                adresses[addressx] = [index + 1, -1]
                if lastAddress != None:
                    adresses[lastAddress][1] = index + 1
                lastAddress = addressx
            elif line.startswith("return "):
                if lastAddress != None:
                    adresses[lastAddress][1] = index + 1
                    lastAddress = None

        if lastAddress != None:
            adresses[lastAddress][1] = len(classFunc)

        resox = dict()
        for adr in gotos:
            desty = None
            if adr in adresses:
                desty = adresses[adr]
            #elif adr[0:2] == "0x":
            #    print("Not_Found1:", adr, ":", classFunc[gotos[adr][0]], end="")
            #elif adr[0] == "v":
            #    print("Not_Found2:", adr, ":", classFunc[gotos[adr][0]], end="")
            #else:
            #    print("Not_Found3:", adr, ":", classFunc[gotos[adr][0]], end="")

            resox[adr] = (
                gotos[adr],
                desty
            )

        return resox


    def processClasses(self, classes):
        for cls in classes:
            if cls == "Item":
                for func in classes[cls]:
                    gotoData = self.collect(classes[cls][func])

                    funcy = classes[cls][func]
                    for x in gotoData:
                        ggg = gotoData[x]
                        idx = ggg[0][0]
                        lenx = ggg[0][1]
                        gox = funcy[idx]
                        elss = "else" in gox
                        dex = ggg[1]
                        if dex != None:
                            if dex[1] > 0:
                                dessst = funcy[dex[0]:dex[1]]
                                del funcy[idx] # remove goto line
                                rev_dessst = dessst[::-1]

                                if elss:
                                    funcy.insert(idx, str(" "*(lenx-4)) + "else\n")
                                    funcy.insert(idx, str(" "*(lenx-4)) + "}\n")
                                funcy.insert(idx, str(" "*lenx) + "}\n")

                                for line in rev_dessst:
                                    funcy.insert(idx, str(" "*(lenx+4)) + line[4:])

                                funcy.insert(idx, str(" "*lenx) + "if(true){\n")
                                if elss:
                                    funcy.insert(idx, str(" "*(lenx-4)) + "{\n")

                    classes[cls][func] = funcy

                    with open(cls + "_" + func + ".cpp", "w") as f:
                        f.write("".join(funcy))

                    print(cls, func, len(gotoData))


