# This Python file uses the following encoding: utf-8

import re


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
        lines_to_remove = []
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

                    lines_to_remove.append(line_index)
                    next_is_decl = False
                elif class_body:
                    if line == "}":
                        class_body = False
                    else:
                        class_functions[cur_class_index][2].append(line)
                    lines_to_remove.append(line_index)
                elif line.startswith("/*"):
                    line = line.strip()
                    if line.endswith("*/") and "::" in line:
                        line = line[3:len(line)-2].strip()

                        regex = re.compile(r'([a-zA-Z0-9-_]+::[a-zA-Z0-9-_]+\([a-zA-Z,<>:0-9-_& \*]*\))')
                        mo = regex.search(line)
                        # FIXME: a lot of classes and their functions are still not included
                        # TODO: handle functions that have different names/class structures later!!! Do not forget!!!
                        if mo:
                            if len(mo.group(0)) > 0:
                                class_functions.append([line]) # probably correct function name, without return type
                                next_is_decl = True

                                # here because some class functions are skipped at the moment for some reasons
                                lines_to_remove.append(line_index)


        print("DONE", flush=True)

        self.save_new_cpp_file(file_path, lines_to_remove)
        self.sort_funcs_into_classes(class_functions)

        print()


    def save_new_cpp_file(self, file_path, lines_to_remove):
        print("Writing cleaned cpp file...", end="", flush=True)
        with open(file_path) as fr:
            path_array = file_path.split("/")
            file_name = path_array[len(path_array) - 1]

            lines = []
            for line in fr:
                lines.append(line)

            # remove already processed lines (e.g. in class files)
            lines_to_remove.sort()
            lines_to_remove.reverse()
            for idx in lines_to_remove:
                del lines[idx]

            with open(Classner.export_dir + "/" + file_name, "w") as fw:
                for line in lines:
                    fw.write(line)

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

