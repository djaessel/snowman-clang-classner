# This Python file uses the following encoding: utf-8

import os


class ClassStorer:
    export_dir = "generated_classes"

    # currently unused
    param_types = {
        "i": "int32_t",
        "v": "void", # no parameters
        "b": "bool",
        "Kb": "const bool", # const
        "RKb": "const bool &", # by reference const
        # when RK<d> --> RK4Item... --> "const Item &"
    }

    param_asm_names = [
         # "rdi", # skip first, is always class object pointer -> this
         "rsi",
         "rdx",
         "rcx",
         "r8",
         "r9",
         "a<x>",
    ]

    replaces = [
        # replace LLVM 1-Bit values with boolean
        ("uint1_t", "bool"), # pointers included - uxxxxx must come first!!!
        ("int1_t", "bool"), # pointers included
        ("unsigned char", "BYTE"), # pointers included
        ("signed char", "S_BYTE"), # pointers included
    ]

    all_valid_types = [
        "void","void*","void**","void***",
        "bool","bool*","bool**","bool***",
        "int8_t","int8_t*","int8_t**","int8_t***",
        "uint8_t","uint8_t*","uint8_t**","uint8_t***",
        "int16_t","int16_t*","int16_t**","int16_t***",
        "uint16_t","uint16_t*","uint16_t**","uint16_t***",
        "int32_t","int32_t*","int32_t**","int32_t***",
        "uint32_t","uint32_t*","uint32_t**","uint32_t***",
        "int64_t","int64_t*","int64_t**","int64_t***",
        "uint64_t","uint64_t*","uint64_t**","uint64_t***",
        "char","char*","char**","char***",
    #    "signed char","signed char*","signed char**","signed char***",
        "BYTE","BYTE*","BYTE**","BYTE***",
        "S_BYTE","S_BYTE*","S_BYTE**","S_BYTE***",
    ]

    all_valid_special_types = [
        "struct","struct*","struct**","struct***",
    ]


    def __init__(self, structer, classList):
        self.classList = classList
        self.structer = structer
        pass


    def classFunctionParameterFix(self, fname, assembly_func_name):
        if fname.find("(") < 0:
            print("classFunctionParameterFix", fname)
            input("ERROR") # FIXME: make real error handling
        telp = fname.split("(")[1].split(")")[0].split(",")

        fname = fname.split("(")[0] + "(" # base name without parameters

        if len(telp) > 1 or len(telp[0]) > 0:
            parax = assembly_func_name.split("(")[1].split(")")[0].split(",")
            for i, p in enumerate(telp):
                lasx = None
                if len(parax) > (i + 1):
                    lasxList = parax[i+1].split()
                    if len(lasxList) > 0:
                        lasx = lasxList[len(lasxList) - 1]
                # else:
                #     # FIXME: bug with sometimes missing parameters mentioned in assembly func name!!!
                #     # print(parax[i], len(parax), i, assembly_func_name, p, telp)
                #     # x = input("ROOOOOOOOOOOR")
                #     pass

                idx = i - 1
                if idx >= len(ClassStorer.param_asm_names):
                    idx = len(ClassStorer.param_asm_names) - 1
                nox = ClassStorer.param_asm_names[idx].replace("<x>", str(i))
                if lasx != None and lasx != nox:
                    nox = lasx
                fname += p + " " + nox + ","

        fname = fname.rstrip(",") + ")"
        return fname


    def update_new_cpp_file(self, file_path, classes):
        print("Update cleaned cpp file...", end="", flush=True)

        path_array = file_path.split("/")
        file_name = path_array[len(path_array) - 1]

        with open(ClassStorer.export_dir + "/" + file_name) as fr:
            lines = fr.readlines()

        with open(ClassStorer.export_dir + "/" + file_name, "w") as fw:
            for line in lines:
                line = self.replaceSymbolsInLine(line)
                fw.write(line.rstrip("\n") + "\n")

        print("DONE")


    def writeClassesJust(self, fixed_classes):
        if not os.path.exists(ClassStorer.export_dir):
            os.mkdir(ClassStorer.export_dir)

        print("WRITING FIXED CLASSES BEGIN")
        for cls in fixed_classes:
            start_lines = []
            my_funcs = []
            with open(ClassStorer.export_dir + "/" + cls + ".cpp") as fr:
                mol_mode = False
                for line in fr:
                    if cls + "::" in line:
                        my_funcs.append(line)
                        mol_mode = True
                    if not mol_mode:
                        start_lines.append(line)

            with open(ClassStorer.export_dir + "/" + cls + ".cpp", "w") as fw:
                for line in start_lines:
                    fw.write(line)

                for func in fixed_classes[cls]:
                    for fun in my_funcs:
                        if "::" + func + "(" in fun:
                            fw.write(fun) # write func head
                            break

                    for line in fixed_classes[cls][func]:
                        fw.write(line)

                    fw.write("\n\n\n")

        print("WRITING FIXED CLASSES END")
        print()


    def writeClasses(self):
        if not os.path.exists(ClassStorer.export_dir):
            os.mkdir(ClassStorer.export_dir)

        self.allFuncs = dict()
        for cls in self.classList:
            funcy = self.classList[cls]
            for func in funcy:
                folyr = None
                foly = func[1].split()
                for ll in foly:
                    if ll.find("_Z") == 0:
                        folyr = ll.split("(")[0]
                        break
                if folyr:
                    self.allFuncs[folyr] = func[0].strip()

        print("WRITING CLASSES BEGIN")
        for cls in self.classList:
            self.writeClassHeaderFile(cls)
            self.writeClassCodeFile(cls)
            self.writeStructsForHeader(cls)
        print("WRITING CLASSES END")
        print()


    def writeStructsForHeader(self, cls):
        structs = self.structer.get_structs()
        print("  Writing", cls, "class used structs...", end="", flush=True)

        with open(ClassStorer.export_dir + "/" + cls + ".cpp") as fread:
            allCode = fread.read()

        with open(ClassStorer.export_dir + "/" + cls + ".h") as fread:
            allHeader = fread.read()

        newStructCode = ""
        for struct in structs: # check for struct s0 !!! it starts with STRUCT_1 ???
            def_struct = struct.replace("STRUCT_", "s")
            if def_struct in allCode or def_struct in allHeader:
                newStructCode += "\n"
                for line in structs[struct]:
                    newStructCode += line + "\n"
                newStructCode += "\n"

        allHeader = allHeader.replace("// STRUCTS_GEN", newStructCode)
        with open(ClassStorer.export_dir + "/" + cls + ".h", "w") as fwrite:
            fwrite.write(allHeader + "\n")

        print("DONE")


    def writeClassHeaderFile(self, cls):
        print("  Writing", cls, "class header...", end="", flush=True)
        with open(ClassStorer.export_dir + "/" + cls + ".h", "w") as f:
            f.write("#ifndef " + cls.upper() + "_H" + "\n")
            f.write("#define " + cls.upper() + "_H" + "\n")
            f.write("\n")
            f.write("#define BYTE unsigned char" + "\n")
            f.write("#define S_BYTE signed char" + "\n")
            f.write("\n")
            f.write("// STRUCTS_GEN" + "\n") # to be replaced by structs later
            f.write("\n")
            f.write("class " + cls + "\n")
            f.write("{" + "\n")
            f.write("public:" + "\n")
            #f.write("  " + cls + "() {}" + "\n") # write empty constructor if nothing found - later check for depending object calls etc

            for func in self.classList[cls]:
                # func1 = func[1].rstrip("}").rstrip().rstrip("{").rstrip()
                return_type = "void" # void until proven otherwise
                #return_type = func1.split("(")[0].split("<")[0]
                #return_type = return_type[-1]
                #if return_type in return_types.keys():
                #    return_type = return_types[return_type]
                cpp_file_func_name = self.classFunctionParameterFix(func[0], func[1]) # make with actual parameters
                f.write(f"  {return_type} {cpp_file_func_name}; // {func[1]} \n") # add return value and maybe basic parameter names
                #f.write(func[1] + "\n")

            f.write("};" + "\n")
            f.write("\n")
            f.write("#endif // " + cls.upper() + "_H" + "\n")
            f.write("\n")
        print("DONE")


    def replaceSymbolsInLine(self, line):
        for repl in ClassStorer.replaces:
            line = line.replace(repl[0], repl[1])

        tmp = None
        decl = False
        commax = False
        while "_Z" in line and not tmp == line:
            tmp = line
            cutty = line[line.index("_Z"):]

            if cutty.find("(") >= 0:
                cutty = cutty[0:cutty.index("(")]
            elif cutty.find(")") >= 0:
                cutty = cutty[0:cutty.index(")")]
                decl = True
            elif cutty.find(";") >= 0:
                commax = True
                cutty = cutty[0:cutty.index(";")]
            else:
                print("ERROR")

            if cutty in self.allFuncs:
                if commax or decl:
                    line = line.replace(cutty, "UNKNOWN_OBJECT_RDI_1->" + self.allFuncs[cutty].split("(")[0]) + " // find rdi val and set as proper object"
                else:
                    rdix = line[line.index(cutty):]
                    if rdix.find(",") >= 0:
                        rdix = rdix[0:rdix.index(",")]
                        if rdix.find("(") >= 0:
                            rdix = rdix.split("(")[1]
                        los = rdix + ", "
                        molto = ""
                        rdix = rdix.split()
                        if len(rdix) > 0:
                            rdix = rdix[len(rdix) - 1]
                        else:
                            rdix = ""
                    elif rdix.find(")") >= 0:
                        rdix = rdix[0:rdix.index(")")]
                        if rdix.find("(") >= 0:
                            rdix = rdix.split("(")[1]
                        los = "(" + rdix + ")"
                        molto = "()"
                        rdix = rdix.split()
                        if len(rdix) > 0:
                            rdix = rdix[len(rdix) - 1]
                        else:
                            rdix = ""
                    rdix = rdix.strip()
                    if len(rdix) <= 0:
                        rdix = "UNKNOWN_OBJECT_RDI_2"
                    line = line.replace(cutty, rdix + "->" + self.allFuncs[cutty].split("(")[0]).replace(los, molto) + " // remove rdi val and set as proper object"

        return line


    def writeClassCodeFile(self, clsxxx):
        structs = self.structer.get_structs()
        print("  Writing", clsxxx, "class functions...", end="", flush=True)

        with open(ClassStorer.export_dir + "/" + clsxxx + ".cpp", "w") as f:
            f.write('#include "' + clsxxx + '.h"' + "\n")
            f.write("\n")

            classFuncs = self.classList[clsxxx]
            for func in classFuncs:
                variables = {"DUMMY": "DUMMY"}

                # func1 = func[1].rstrip("}").rstrip().rstrip("{").rstrip()
                return_type = "void" # void until proven otherwise
                #return_type = func1.split("(")[0].split("<")[0]
                #return_type = return_type[-1]
                #if return_type in return_types.keys():
                #    return_type = return_types[return_type]

                cpp_file_func_name = self.classFunctionParameterFix(func[0], func[1]) # make with actual parameters
                f.write(return_type + " " + clsxxx + "::" + cpp_file_func_name + "\n") # add return value and maybe basic parameter names

                func_body = func[2]

                to_be_deleted = []
                # extract variable declarations
                for i, line in enumerate(func_body):
                    # if regex:
                    monline = line.rstrip("\n").rstrip(";").strip()
                    for repl in ClassStorer.replaces:
                        monline = monline.replace(repl[0], repl[1])
                    monem = monline.split()
                    monemLen = len(monem)
                    if monemLen == 2:
                        if monem[0] in ClassStorer.all_valid_types:
                            variables[monem[1]] = monem[0]
                            to_be_deleted.append(i)
                        # else:
                        #     print("NOT VALID?", monem)
                    elif monemLen == 3:
                        if monem[0] in ClassStorer.all_valid_special_types:
                            # variables[monem[2]] = monem[1] # change later to meaningful name or fix
                            variables[monem[2]] = "STRUCT_" + monem[1][1:] # change later to meaningful name or fix
                            to_be_deleted.append(i)
                        # else:
                        #     print("NOT VALID?", monem)
                variables.pop("DUMMY") # remove DUMMY variable
                # remove just var definitions
                to_be_deleted.reverse()
                for i in to_be_deleted:
                    del func_body[i]

                if len(func_body) > 0 and len(func_body[0].strip()) == 0:
                    del func_body[0] # remove empty starting line

                used_as_pointer = []

                f.write("{\n")
                for line in func_body:
                    line = self.replaceSymbolsInLine(line)

                    for varx in variables:
                        if varx in line and not varx + " =" in line :
                            if ("(" + varx in line and varx + "," in line) or " " + varx + "," in line or varx + ")" in line or varx + " +" in line or varx + " -" in line or varx + " *" in line:
                                used_as_pointer.append(varx)

                    for uap in used_as_pointer:
                        if uap in variables:
                            variables.pop(uap) # only add type declaration for the first occurance

                    if "=" in line:
                        tmpp = line.split("=")[0].lstrip()
                        found_var = False
                        for varx in variables:
                            if varx + " " in tmpp and tmpp.find(varx) == 0 and line.find(varx) <= 4:
                                line = line.replace(varx + " =", variables[varx] + " " + varx + " =")
                                found_var = varx

                        if found_var:
                            variables.pop(found_var) # only add type declaration for the first occurance

                    if "struct" in line: # replace structs in code with "actual" name
                        for struct in structs:
                            tetraTmp = "struct " + struct.replace("STRUCT_", "s")
                            if tetraTmp in line:
                                if tetraTmp + " " in line:
                                    line = line.replace(tetraTmp + " ", struct + " ")
                                if tetraTmp + "***" in line: # TODO: check if triple pointer is max
                                    line = line.replace(tetraTmp + "***", struct + "***")
                                if tetraTmp + "**" in line:
                                    line = line.replace(tetraTmp + "**", struct + "**")
                                if tetraTmp + "*" in line:
                                    line = line.replace(tetraTmp + "*", struct + "*")

                    f.write(line + "\n")

                if len(used_as_pointer) > 0:
                    f.write("  // possible pointer usage or inline declarations" + "\n")
                    for uap in used_as_pointer:
                        f.write("  // " + uap + "\n")

                f.write("}\n\n\n")
        print("DONE")
