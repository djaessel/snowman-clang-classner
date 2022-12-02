# This Python file uses the following encoding: utf-8

import re
import os


class Classner:
    export_dir = "generated_classes"

    def __init__(self):
        self.classes = {"DUMMY": []}
        pass

    def get_classes(self):
        return self.classes


    def readClassFunctions(self, file_path):
        class_functions = []
        line_index = -1
        ignored_lines = []
        print("Reading class functions...", end="", flush=True)
        with open(file_path) as f:
            cur_class_index = -1
            next_is_decl = False
            class_body = False
            for line in f:
                line_index += 1
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

                        regex = re.compile(r'([a-zA-Z0-9-_]+::[a-zA-Z0-9-_]+\([a-zA-Z,.<>:0-9-_& \*]*\))')
                        mo = regex.search(line)
                        # FIXME: a lot of classes and their functions are still not included
                        # TODO: handle functions that have different names/class structures later!!! Do not forget!!!
                        if mo:
                            if len(mo.group(0)) > 0:
                                class_functions.append([line]) # probably correct function name, without return type
                                next_is_decl = True
                elif "_Z" in line:
                    regex = re.compile(r'(_Z[a-zA-Z0-9-_]+\([a-zA-Z,.<>:0-9-_& \*]*\))')
                    mo = regex.search(line)
                    # FIXME: a lot of classes and their functions are still not included
                    # TODO: handle functions that have different names/class structures later!!! Do not forget!!!
                    if mo:
                        if len(mo.group(0)) > 0:
                            if not ";" in line: # ignore just names, only except with function body!
                                class_functions.append(["NO_COMMENT"]) # probably correct function name, without return type
                                cur_class_index = len(class_functions) - 1
                                class_functions[cur_class_index].append(line) # decompilated mangled name
                                class_functions[cur_class_index].append([]) # body of function
                                class_body = True
                else:
                    ignored_lines.append(line + "\n")


        print("DONE", flush=True)

        self.save_new_cpp_file(file_path, ignored_lines)
        self.sort_funcs_into_classes(class_functions)


    def save_new_cpp_file(self, file_path, lines_to_store):
        print("Writing cleaned cpp file...", end="", flush=True)

        if not os.path.exists(Classner.export_dir):
            os.mkdir(Classner.export_dir)

        path_array = file_path.split("/")
        file_name = path_array[len(path_array) - 1]
        with open(Classner.export_dir + "/" + file_name, "w") as fw:
            fw.writelines(lines_to_store)

        print("DONE")


    def sort_funcs_into_classes(self, funcs):
        self.classes.clear()
        print("Sort functions into classes...", end="", flush=True)
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

                if not class_name in self.classes.keys():
                    self.classes[class_name] = []

                self.classes[class_name].append((ddd[1], func[1], func[2]))
        print("DONE", flush=True)

