import os
import sys
import tkinter as tk
from pynput import keyboard
import mido
import yaml
import threading
import time

# Obtener el directorio del script
if getattr(sys, 'frozen', False):
    base_path = os.path.dirname(sys.executable)
else:
    base_path = os.path.dirname(os.path.abspath(__file__))
yaml_path = os.path.join(base_path, 'note_cc_mapping.yml')

# Cargar el mapeo desde el archivo YAML
with open(yaml_path, 'r') as file:
    config = yaml.safe_load(file)
    note_cc_mapping = {int(k): (v.split(',')[0], int(v.split(',')[1])) for k, v in config['note_cc_mapping'].items()}

try:
    # Asegúrate de que el backend rtmidi esté disponible
    mido.set_backend('mido.backends.rtmidi')
    midi_out = mido.open_output('K2 1')
    print("Puerto MIDI abierto con éxito.")
except IOError:
    print("Error al abrir el puerto MIDI. Asegúrate de que el nombre del puerto es correcto.")
except ImportError:
    print("Error al importar el backend rtmidi. Asegúrate de que python-rtmidi está instalado.")

def send_midi_cc(value):
    cc_message = mido.Message('control_change', channel=0, control=20, value=value)
    midi_out.send(cc_message)
    print(f"Mensaje MIDI enviado: CC {value}")

def get_note_and_modifiers(key_code):
    return note_cc_mapping.get(key_code, ('Unknown Note', None))

def show_popup(note_name):
    popup = tk.Toplevel()
    popup.overrideredirect(True)
    popup.configure(bg='red')

    screen_width = popup.winfo_screenwidth()
    screen_height = popup.winfo_screenheight()

    window_width = 300
    window_height = 100

    x = (screen_width - window_width) / 2
    y = (screen_height - window_height) / 2

    popup.geometry(f'{window_width}x{window_height}+{int(x)}+{int(y)}')

    label = tk.Label(popup, text=f'KEY: {note_name}', font=('Helvetica', 24), fg='white', bg='red')
    label.pack(expand=True)

    popup.after(1000, popup.destroy)

def on_press(key):
    try:
        key_code = key.vk if hasattr(key, 'vk') else key.value.vk
        note_tuple = get_note_and_modifiers(key_code)
        if note_tuple[1] is not None:
            print(f"Key pressed: {key_code} {note_tuple[0]} {note_tuple[1]}")
            send_midi_cc(note_tuple[1])
            show_popup(note_tuple[0])
        else:
            print(f"Unknown key pressed: {key_code}")
    except AttributeError:
        print(f'Special key pressed: {key}')

def on_release(key):
    if key == keyboard.Key.esc:
        return False

listener = keyboard.Listener(
    on_press=on_press,
    on_release=on_release
)
listener.start()

root = tk.Tk()
root.withdraw()

root.mainloop()