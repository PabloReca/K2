from cx_Freeze import setup, Executable
import os

base = None
if os.name == 'nt':
    base = 'Win32GUI'  # Esto evita que aparezca la consola en Windows

executables = [Executable("k2.py", base=base, icon="k2_logo.ico")]

setup(
    name="K2 Application",
    version="1.0",
    description="Aplicación para enviar mensajes MIDI",
    options={
        'build_exe': {
            'packages': ['os', 'sys', 'tkinter', 'pynput', 'mido', 'yaml', 'threading', 'time'],
            'include_files': ['note_cc_mapping.yml'],
            'include_msvcr': True,
        },
    },
    executables=executables
)
