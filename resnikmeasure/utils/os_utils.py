import os

def check_dir(path):
    os.makedirs(path, exist_ok=True)
    return path