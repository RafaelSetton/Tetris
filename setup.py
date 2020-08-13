import cx_Freeze

executables = [cx_Freeze.Executable("Tetris.py", base="Win32GUI")]
cx_Freeze.setup(name="Tetris",
                options={"build_exe": {'packages': ['pygame'], 'include_files': ['Images/']}},
                executables=executables
                )
