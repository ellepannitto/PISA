import os

def check_dir(path):
    path = path+"/"
    os.makedirs(path, exist_ok=True)
    return path