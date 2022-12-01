#!/usr/bin/python3

import os
import re
import sys


def createVariableList(filePath):
    variables = {"DUMMY": "DUMMY"}
    replaces = [
        ("uint1_t", "bool"), # pointers included - uxxxxx must come first!!!
        ("int1_t", "bool"), # pointers included
    ]
    all_valid_types = [
        "void","void*","void**", 
        #"int1_t","int_1_t*","int_1_t**",
        #"uint1_t","uint_1_t*","uint_1_t**",
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
        "signed char","signed char*","signed char**","signed char***",
    ]

    with open(filePath) as f:
        for line in f:
            # if regex:
            monline = line.rstrip("\n").rstrip(";").strip()
            for repl in replaces:
                monline = monline.replace(repl[0], repl[1])
            monem = monline.split()
            if len(monem) == 2 and monem[0] in all_valid_types:
                variables[monem[1]] = monem[0]
            # elif len(monem) == 2:
            #     print("NOT VALID?", monem)
    
    variables.pop("DUMMY") # remove start dummy item
    print(variables)
    return variables


file_path = ""

if len(sys.argv) > 1:
    file_path = sys.argv[1]

if len(file_path) > 0:
    createVariableList(file_path)
else:
    print("ERROR: No file given!")

