#!/usr/bin/python3

import os
import re
import sys



def readClassFunctions(file_path):
    class_functions = []
    with open(file_path) as f:
        cur_class_index = -1
        next_is_decl = False
        class_body = False
        for line in f:
            line = line.rstrip("\n")
            if next_is_decl:
                line = line.strip()
                cur_class_index = len(class_functions) - 1
                if ";" in line: # remove just names, only except with function body!
                    del class_functions[cur_class_index]
                else:
                    class_functions[cur_class_index].append(line) # decompilated mangled name
                    class_functions[cur_class_index].append([]) # body of function
                    class_body = True

                next_is_decl = False
            elif class_body:
                if line == "}":
                    class_body = False
                else:
                    class_functions[cur_class_index][2].append(line)
            elif line.startswith("/*"):
                line = line.strip()
                if line.endswith("*/") and "::" in line:
                    line = line[3:len(line)-2].strip()
                    regex = re.compile(r'([a-zA-Z0-9-_]+::[a-zA-Z0-9-_]+\([a-zA-Z,<>:0-9-_\*]*\))')
                    mo = regex.search(line)
                    # TODO: handle functions that have different names/class structures later!!! Do not forget!!!
                    if mo:
                        if len(mo.group(0)) > 0:
                            class_functions.append([line]) # probably correct function name, without return type
                            next_is_decl = True
    return class_functions



def sort_funcs_into_classes(funcs):
    classes = {"DUMMY": []}
    for func in funcs:
        ddd = func[0].split("::")
        if len(ddd) > 1:
            class_name = ddd[0]
            #if class_name.strip() == "std":
            #    continue # skip somtimes strange std function -> can be imported anyway (hopefully)
            if len(ddd) > 2:
                continue # skip any namespace functions - they are usually importable and not from the main proram

            class_name = class_name.replace("non-virtual thunk to", "").strip() # maybe add that info later on

            regex = re.compile(r'[^<>]+[<>]+[^<>]+[<>]+[^<>]*')
            mo = regex.search(class_name)
            if mo and len(mo.group(0)) > 0:
                continue # skip weird class functions for now

            if not class_name in classes.keys():
                classes[class_name] = []

            classes[class_name].append((ddd[1], func[1], func[2]))
    classes.pop("DUMMY") # remove initial dummy class
    return classes


def writeClasses(classList):
    export_dir = "generated_classes"

    if not os.path.exists(export_dir):
        os.mkdir(export_dir)

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

    for cls in classList:
        with open(export_dir + "/" + cls + ".h", "w") as f:
            f.write("#ifndef " + cls.upper() + "_H" + "\n")
            f.write("#define " + cls.upper() + "_H" + "\n")
            f.write("\n")
            f.write("\n")
            f.write("class " + cls + "\n")
            f.write("{" + "\n")
            f.write("public:" + "\n")
            #f.write("  " + cls + "() {}" + "\n") # write empty constructor if nothing found - later check for depending object calls etc
            
            for func in classList[cls]:
                func1 = func[1].rstrip("}").rstrip().rstrip("{").rstrip()
                return_type = "void" # void until proven otherwise
                #return_type = func1.split("(")[0].split("<")[0]
                #return_type = return_type[-1]
                #if return_type in return_types.keys():
                #    return_type = return_types[return_type]
                f.write("  " + return_type + " " + func[0] + ";\n") # add return value and maybe basic parameter names
                #f.write(func[1] + "\n")

            f.write("};" + "\n")
            f.write("\n")
            f.write("#endif // " + cls.upper() + "_H" + "\n")
            f.write("\n")

        with open(export_dir + "/" + cls + ".cpp", "w") as f:
            f.write('#include "' + cls + '.h"' + "\n")
            f.write("\n")

            for func in classList[cls]:
                func1 = func[1].rstrip("}").rstrip().rstrip("{").rstrip()
                return_type = "void" # void until proven otherwise
                #return_type = func1.split("(")[0].split("<")[0]
                #return_type = return_type[-1]
                #if return_type in return_types.keys():
                #    return_type = return_types[return_type]
                cpp_file_func_name = func[0] # make with actual parameters

                if cpp_file_func_name.find("(") < 0:
                    print(cpp_file_func_name)
                    x = input("ERROR")
                telp = cpp_file_func_name.split("(")[1].split(")")[0].split(",")
                cpp_file_func_name = cpp_file_func_name.split("(")[0] + "(" # base name without parameters

                if len(telp) > 1 or len(telp[0]) > 0:
                    for i, p in enumerate(telp):
                        cpp_file_func_name += p + " " + param_asm_names[i].replace("<x>", str(i)) + ","

                cpp_file_func_name = cpp_file_func_name.rstrip(",") + ")"

                f.write(return_type + " " + cls + "::" + cpp_file_func_name + "\n") # add return value and maybe basic parameter names
                
                func_body = func[2]
                f.write("{\n")
                for line in func_body[1:-1]:
                    line = line.replace("uint1_t", "bool").replace("int1_t", "bool") # replace LLVM 1-Bit values with boolean
                    f.write(line + "\n")
                f.write("}\n\n\n")



def writeClassFunctions(c_functions):
    with open("class_functions.txt", "w") as f:
        for func in c_functions:
            f.write(func + "\n")


def main():
    file_path = ""
    if len(sys.argv) > 1:
        file_path = sys.argv[1]

    if file_path == "":
        print("No file given!")
        return

    print("Processing cpp file ...", end=" ")
    
    funcs = readClassFunctions(file_path)
    # writeClassFunctions(funcs)
    classes = sort_funcs_into_classes(funcs)
    # print(classes["Game"])
    writeClasses(classes)
    
    print("DONE")


main()



