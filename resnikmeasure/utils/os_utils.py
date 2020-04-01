import os
import glob


def check_dir(path):
    path = path+"/"
    os.makedirs(path, exist_ok=True)
    return path


def get_filepaths(dirpaths_list):
    for folder in dirpaths_list:
        for filename in glob.glob(folder+"/*"):
            yield filename