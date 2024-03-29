# This Python file uses the following encoding: utf-8

import os
# import multiprocessing as mp
from multiprocessing import Pool
import concurrent.futures
from os import getpid
from specialvals import DEBUGMODE


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
        ("__return_address()", "__builtin_extract_return_addr(__builtin_return_address(0))"), # return_address() from Decompiler GCC replacement(?)
        ("__zero_stack_offset()", "zero_stack_offset()"), # __zero_stack_offset() from Decompiler GCC replacement(?)
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
        "int","int*","int**","int***",
        "uint","uint*","uint**","uint***",
        "int64_t","int64_t*","int64_t**","int64_t***",
        "uint64_t","uint64_t*","uint64_t**","uint64_t***",
        "char","char*","char**","char***",
    #    "signed char","signed char*","signed char**","signed char***",
        "BYTE","BYTE*","BYTE**","BYTE***",
        "S_BYTE","S_BYTE*","S_BYTE**","S_BYTE***",
        "float","float*","float**","float***",
        "double","double*","double**","double***",
    ]

    all_valid_special_types = [
        "struct","struct*","struct**","struct***",
        # are there more?
    ]


    def __init__(self, structer, classList):
        self.classList = classList
        self.structer = structer
        pass


    def classFunctionParameterFix(self, fname, assembly_func_name):
        if fname.find("(") < 0:
            print("classFunctionParameterFix", ":", fname, ":", assembly_func_name)
            fname = assembly_func_name # temporary fix?
        else:
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


    def writeClassesJust(self, fixed_classes, class_includes):
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

            all_lines_x = []
            with open(ClassStorer.export_dir + "/" + cls + ".h") as fr:
                for line in fr:
                    if "// USED_CLASSES" in line:
                        line = ""
                        for include in class_includes[cls]:
                            line += '#include "' + include + '.h"\n'
                        line += "\n"
                    all_lines_x.append(line)

            with open(ClassStorer.export_dir + "/" + cls + ".h", "w") as fw:
                for line in all_lines_x:
                    fw.write(line.rstrip('\n') + '\n')

        print("WRITING FIXED CLASSES END")
        print()


    def _help_write_classes(self, partNum, maxPartCount):
        packSize = int(len(self.classList) / maxPartCount)
        startIndex = int(packSize * partNum)
        endIndex = startIndex + packSize
        if partNum + 1 == maxPartCount:
            endIndex = len(self.classList.keys())
        keyList = list(self.classList.keys())[startIndex:endIndex]
        for cls in keyList:
            self.writeClassHeaderFile(cls)
            self.writeClassCodeFile(cls)
            self.writeStructsForHeader(cls)
        #print("Process", partNum, "finished!")
        reserved = None
        return [len(keyList), reserved, os.getpid()]


    def writeClasses(self):
        if not os.path.exists(ClassStorer.export_dir):
            os.mkdir(ClassStorer.export_dir)

        self.allFuncs = dict()
        self.allFuncClass = dict()
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
                    self.allFuncClass[folyr] = cls

        if DEBUGMODE:
            print("WRITING CLASSES BEGIN")
        else:
            print("Writing classes...", end="", flush=True)

        #for cls in self.classList:
        #    self.writeClassHeaderFile(cls)
        #    self.writeClassCodeFile(cls)
        #    self.writeStructsForHeader(cls)
        #maxProcs = int(os.cpu_count() * 0.5) # 16 -> 8
        #running_procs = []
        #for i in range(maxProcs):
        #    proc = mp.Process(target=self._help_write_classes, args=(i, maxProcs))
        #    proc.start()
        #    running_procs.append(proc)
        #for p in running_procs:
        #    p.join()
        #print(f"Finished with {maxProcs} threads!")

        maxProcs = int(os.cpu_count() * 0.75) # 16 -> 12, 8 -> 6, 4 -> 3
        with concurrent.futures.ProcessPoolExecutor() as executor:
            results = [executor.submit(self._help_write_classes, i, maxProcs) for i in range(maxProcs)]

        values_list = []
        for f in concurrent.futures.as_completed(results):
            values = f.result()
            values_list.append(values)

        #for vx in values_list:
        #    print("Processed", vx[0], "classes with process", vx[2])

        if DEBUGMODE:
            print("WRITING CLASSES END")
            print()
        else:
            print("DONE")


    def writeStructsForHeader(self, cls):
        structs = self.structer.get_structs()
        if DEBUGMODE:
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

        if DEBUGMODE:
            print("DONE")


    def writeClassHeaderFile(self, cls):
        if DEBUGMODE:
            print("  Writing", cls, "class header...", end="", flush=True)
        with open(ClassStorer.export_dir + "/" + cls + ".h", "w") as f:
            f.write("#ifndef " + cls.upper() + "_H" + "\n")
            f.write("#define " + cls.upper() + "_H" + "\n")
            f.write("\n")
            f.write("#include <inttypes.h>\n")
            f.write("#include <iostream>\n")
            f.write("#include <stddef.h>\n")
            f.write("#include <boost/multiprecision/cpp_int.hpp>\n")
            f.write("#include <string>\n") # maybe add more later on (e.g. used classes)
            f.write("\n")
            f.write("/* CUSTOM INCLUDES */\n")
            f.write('#include "snowmany.h"\n')
            f.write("\n")
            f.write("/* GENERATED INCLUDES */\n")
            f.write("// USED_CLASSES" + "\n") # will be replaced with includes
            f.write("\n")
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
        if DEBUGMODE:
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

            operx = "operator"
            if cutty in self.allFuncs:
                if operx in self.allFuncs[cutty]:
                    lem = self.allFuncs[cutty]
                    cur_operator = lem[lem.index(operx) + len(operx):][0:]
                    cur_operator = cur_operator[0:cur_operator.index("(")] # FIXME: make correct operator handling!
                    sectox = lem.split("(")[1].split(")")[0]
                    secto = sectox.split(',')
                    cls = self.allFuncClass[cutty]
                    if commax or decl:
                        line = line.replace(cutty + "(" + sectox + ")", cls + "(UNKNOWN_OBJECT_RDI_1) " + cur_operator + " " + cls + "(" + secto[len(secto) - 1] + ")")
                    else:
                        rdix = line[line.index(cutty):]
                        if rdix.find(",") >= 0:
                            rdix = rdix[0:rdix.index(",")]
                            if rdix.find("(") >= 0:
                                rdix = rdix.split("(")[1]
                            los = rdix + ", "
                            molto = ""
                            #rdix = rdix.split(" ")
                            #if len(rdix) > 0:
                            #    rdix = rdix[len(rdix) - 1]
                            #else:
                            #    rdix = ""
                        elif rdix.find(")") >= 0:
                            rdix = rdix[0:rdix.index(")")]
                            if rdix.find("(") >= 0:
                                rdix = rdix.split("(")[1]
                            los = "(" + rdix + ")"
                            molto = "()"
                            #rdix = rdix.split(" ")
                            #if len(rdix) > 0:
                            #    rdix = rdix[len(rdix) - 1]
                            #else:
                            #    rdix = ""
                        rdix = rdix.strip()
                        if len(rdix) <= 0:
                            rdix = "UNKNOWN_OBJECT_RDI_2"
                        solom = line[line.index(cutty):]
                        solom = solom[solom.index("("):]
                        clam = 0
                        iid = -1
                        charActive = False
                        for i in range(len(solom)):
                            if not charActive and solom[i] == "(":
                                clam += 1
                            elif not charActive and solom[i] == ")":
                                clam -= 1
                            elif solom[i] == '"':
                                charActive = not charActive
                            if clam <= 0:
                                iid = i
                                break
                        if iid >= 0:
                            solom = solom[0:iid] + ")"
                            secto = solom.split(',')
                            endo = min(1, len(secto) - 1)
                        else:
                            endo = 0
                            print("ERROR", solom, line)
                        line = line.replace(cutty + solom, cls + "(" + rdix + ") " + cur_operator + " " + cls + "(" +  secto[endo].lstrip(" ").rstrip(')') + ")").rstrip('\n') + " // remove rdi val and set as proper object\n"

                else:
                    if commax or decl:
                        line = line.replace(cutty, "UNKNOWN_OBJECT_RDI_1->" + self.allFuncs[cutty].split("(")[0]) + " // find rdi val and set as proper object"
                    else: # FIXME: change the rdix code to work correctly or not use it at all!
                        rdix = line[line.index(cutty):]
                        if rdix.find(",") >= 0:
                            rdix = rdix[0:rdix.index(",")]
                            if rdix.find("(") >= 0:
                                rdix = rdix.split("(")[1]
                            los = rdix + ", "
                            molto = ""
                            rdix = rdix.split(" ")
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
                            rdix = rdix.split(" ")
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
        if DEBUGMODE:
            print("  Writing", clsxxx, "class functions...", end="", flush=True)

        with open(ClassStorer.export_dir + "/" + clsxxx + ".cpp", "w") as f:
            f.write('#include "' + clsxxx + '.h"' + "\n")
            f.write("\n")

            classFuncs = self.classList[clsxxx]
            for func in classFuncs:
                variables = dict()

                # func1 = func[1].rstrip("}").rstrip().rstrip("{").rstrip()
                return_type = "void" # void until proven otherwise
                #return_type = func1.split("(")[0].split("<")[0]
                #return_type = return_type[-1]
                #if return_type in return_types.keys():
                #    return_type = return_types[return_type]

                cpp_file_func_name = self.classFunctionParameterFix(func[0], func[1]) # make with actual parameters
                f.write(return_type + " " + clsxxx + "::" + cpp_file_func_name + "\n") # add return value and maybe basic parameter names

                func_body = func[2]

                used_as_pointer = dict()
                to_be_deleted = dict()

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
                            to_be_deleted[monem[1]] = i
                        # else:
                        #     print("NOT VALID?", monem)
                    elif monemLen == 3:
                        if monem[0] in ClassStorer.all_valid_special_types:
                            # variables[monem[2]] = monem[1] # change later to meaningful name or fix
                            variables[monem[2]] = "STRUCT_" + monem[1][1:] # change later to meaningful name or fix
                            to_be_deleted[monem[2]] = i
                        # else:
                        #     print("NOT VALID?", monem)

                # remove just var definitions
                # to_be_deleted.reverse()
                to_be_deleted_sorted_keys = sorted(to_be_deleted, key=to_be_deleted.get, reverse=True)
                for key in to_be_deleted_sorted_keys:
                    del func_body[to_be_deleted[key]]

                if len(func_body) > 0 and len(func_body[0].strip()) == 0:
                    del func_body[0] # remove empty starting line

                f.write("{\n")
                for line in func_body:
                    line = self.replaceSymbolsInLine(line)

                    for varx in variables:
                        if varx in line and not varx + " =" in line :
                            if ("(" + varx in line and varx + "," in line) or " " + varx + "," in line or varx + ")" in line or varx + " +" in line or varx + " -" in line or varx + " *" in line:
                                used_as_pointer[varx] = variables[varx]

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
                        f.write("  // " + used_as_pointer[uap] + " " + uap + "\n")

                f.write("}\n\n\n")
        if DEBUGMODE:
            print("DONE")
