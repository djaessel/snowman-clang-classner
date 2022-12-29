import os
import glob

havok_dir = "../warband_mangled_source/havok-2013"
havok_name = "havok-2013"
dir_to_exclude = '.git'
output_file = "found_paths.csv"


def processFath():
    files = glob.glob(havok_dir + '/**/*.h', recursive=True)
    # files_paths = [_ for _ in files if not dir_to_exclude in _]
    files_names = [_.split("/")[-1] for _ in files if not dir_to_exclude in _]

    # print(f'List of file names with path: {files_paths}')
    # print(f'List of file names: {files_names}')

    file_names_found = []
    for header_file in files_names:
        if os.path.exists(header_file) and os.path.isfile(header_file):
            os.system("rm ./" + header_file)
            file_names_found.append(header_file)
        source_file = header_file.replace(".h", ".cpp")
        if os.path.exists(source_file) and os.path.isfile(source_file):
            os.system("rm ./" + source_file)


    cortess = dict()
    with open(output_file, "w") as f:
        for filex in files:
            file_name =  filex.split("/")[-1]
            if file_name in file_names_found:
                filex = filex[filex.index(havok_name):].replace(havok_name, havok_dir)
                f.write(file_name + ";" + filex + "\n")
                cortess[file_name] = filex

    flof = os.listdir(".")
    for fx in flof:
        if ".h" in fx:
            alla = ""
            with open(fx) as f:
                alla = f.read()
                for incl in cortess:
                    alla = alla.replace('"' + incl + '"', '"' + cortess[incl] + '"')
            with open(fx, "w") as f:
                f.write(alla)


processFath()

