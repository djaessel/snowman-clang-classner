# This Python file uses the following encoding: utf-8

import re


class Structer:
    def __init__(self):
        self.structs = {"STRUCT_DUMMY": "struct DUMMY {}"}
        pass


    def get_structs(self):
        return self.structs


    def readStructs(self, file_path):
        self.structs.clear()
        with open(file_path) as f:
            cur_struct_name = None
            struct_body = False
            for line in f:
                line = line.rstrip("\n")
                if line.startswith("struct ") and line.endswith("{"):
                    regex = re.compile(r'(struct [a-zA-Z0-9-_]+[ ][\{])')
                    mo = regex.search(line)
                    if mo:
                        if len(mo.group(0)) > 0:
                            line = line.strip()
                            line = line.replace("struct s", "struct STRUCT_")
                            struct_name = line.split()[1]
                            self.structs[struct_name] = [line] # probably correct function name, without return type
                            cur_struct_name = struct_name
                            struct_body = True
                elif struct_body:
                    self.structs[cur_struct_name].append(line)
                    if line == "};":
                        struct_body = False
