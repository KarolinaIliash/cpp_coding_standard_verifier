
path_dir = r'D:\Downloads\QuantLib-master'

from os import listdir
from os.path import isfile, join, isdir
from typing import List

def get_files(root: str, cur_dir: str) -> List[str]:
    out = [] # type: List[str]
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



files_list = get_files(path_dir, path_dir)

import files

import sys
import os

for i in range(0,0):
    print(i)

os.remove("out.txt")
f = open("out.txt", 'w')
f.close()

os.remove("out2.txt")
f = open("out2.txt", 'w')
f.close()

import time
start_time = time.time()

#for f in files_list:
#   fl = file.CppFile(path_dir + f)
#   fl.scan()
f1 = files.CppFile(r"D:\Downloads\QuantLib-master\ql\cashflow.hpp")
f1.scan()

f2 = files.CppFile(r"D:\Downloads\QuantLib-master\ql\cashflow.cpp")
f2.scan()

f1.verify()
f2.verify()



print("--- %s seconds ---" % (time.time() - start_time))

