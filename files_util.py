from os import listdir
from os.path import isfile, join, isdir
from typing import List

def get_files(root: str, cur_dir: str) -> List[str]:
    out = []  # type: List[str]
    if isfile(cur_dir):
        out.append(cur_dir)
        return out
    l = listdir(cur_dir)
    for f in l:
        if isfile(join(cur_dir, f)) and (f.endswith('.hpp')
                                         or f.endswith('.h') or f.endswith('.cpp') or f.endswith('.c')):
            out.append(join(cur_dir, f).replace(root, ''))
        elif isdir(join(cur_dir, f)):
            out.extend(get_files(root, join(cur_dir, f)))
    return out

