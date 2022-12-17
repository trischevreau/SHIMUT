"""
This is the script to build an executable .exe file on windows.
"""

from distutils.core import setup
import py2exe
import os

print("[!] Building the executable file")

dirs_to_do = ["assets", "parameters", "data"]
Mydata_files = []
for dir in dirs_to_do:
    path_ = os.getcwd() + "\\" + dir + "\\"
    files = [path_+e for e in os.listdir(path_) if os.path.isfile(path_+e)]
    Mydata_files.append((dir, files))

print("[!] Files to include :")
for line in Mydata_files:
    print("[!] >", line)

setup(
    data_files=Mydata_files,
    script_args=['py2exe'],
    options={"py2exe": {"compressed": True}},
    windows=["main.py"],
    zipfile=None
)
