import os

havok_dir = "../warband_mangled_source/havok-2013"


def old_process():
    files = os.listdir(".")
    for fil in files:
        ret = os.popen("locate /" + fil + " | grep " + havok_dir)
        if ret:
            pathx = ret.read().strip()
            if len(pathx) > 0:
                pathx = pathx[pathx.index(havok_dir) + len(havok_dir) + 1:].strip()
                if os.path.isfile("./" + fil):
                    os.system("rm ./" + fil)
                    with open("found_paths.csv", "a") as f:
                        f.write(fil + ";" + pathx + "\n")
                elif ".git" in pathx:
                    pass # just completely ignore git
                else:
                    print("ignored dir:", pathx)


def processFath():
    import glob

    dir_to_exclude = '.git'

    files = glob.glob(havok_dir + '/**/*.h', recursive=True)
    files_paths = [_ for _ in files if not dir_to_exclude in _]
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

    with open("found_paths.csv", "w") as f:
        for filex in files:
            file_name =  filex.split("/")[-1]
            if file_name in file_names_found:
                f.write(file_name+";"+filex+"\n")


# old_process()
processFath()

