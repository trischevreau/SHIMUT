import sys
from cx_Freeze import setup, Executable

script = 'main.py'

include_files = ['README.md', 'LICENSE.md', 'assets/', 'data/', 'parameters/']
includes = []
excludes = []
packages = ['PIL', 'pygame', 'tkinter', 'pychord', 'midiutil', 'sqlite3']

base = None
if sys.platform == "win32":
    base = "Win32GUI"    # Tells the build script to hide the console.

setup(
    name='SHIMUT',
    description='Software to Help Illiterate Musicians Use (musical) Theory',
    executables=[Executable(script, base=base)],
    options={
        'build_exe': {
            'includes':includes,
            'excludes':excludes,
            'include_files':include_files,
            'packages': packages,
        },
    },
)
