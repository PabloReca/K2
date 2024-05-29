import tkinter as tk
from pynput import keyboard
import mido
import threading
import time

# Mapeo de notas a mensajes CC
note_cc_mapping = {
    124: ('C', 1),  # Originalmente 105
    127: ('Db', 15),  # Originalmente 106
    128: ('D', 23),  # Originalmente 64
    129: ('Eb', 37),  # Originalmente 79
    130: ('E', 50),  # Originalmente 80
    131: ('F', 62),  # Originalmente 90
}

alt_note_cc_mapping = {
    124: ('F#', 72),  # Originalmente 105
    127: ('G', 82),  # Originalmente 106
    128: ('Ab', 91),  # Originalmente 64
    129: ('A', 105),  # Originalmente 79
    130: ('Bb', 115),  # Originalmente 80
    131: ('B', 127),  # Originalmente 90
}

current_modifiers = set()

# Listar puertos MIDI disponibles
print("Puertos MIDI disponibles:")
for port in mido.get_output_names():
    print(port)

# Configurar el puerto MIDI
try:
    midi_out = mido.open_output('K2 1')
    print("Puerto MIDI abierto con éxito.")
except IOError:
    print("Error al abrir el puerto MIDI. Asegúrate de que el nombre del puerto es correcto.")

def send_midi_cc(value):
    # Aseguramos que el mensaje se envía en el canal 1
    cc_message = mido.Message('control_change', channel=0, control=20, value=value)  # Canal 0 es el canal 1 en MIDI
    midi_out.send(cc_message)
    print(f"Mensaje MIDI enviado: CC {value}")

def get_note_and_modifiers(key_code):
    if 'Alt' in current_modifiers:
        return alt_note_cc_mapping.get(key_code, ('Unknown Note', None))
    else:
        return note_cc_mapping.get(key_code, ('Unknown Note', None))

def show_popup(note_name):
    popup = tk.Toplevel()
    popup.overrideredirect(True)  # Sin bordes ni botones
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
        if key == keyboard.Key.alt_l or key == keyboard.Key.alt_r:
            current_modifiers.add('Alt')
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
    if key == keyboard.Key.alt_l or key == keyboard.Key.alt_r:
        current_modifiers.discard('Alt')
    if key == keyboard.Key.esc:
        return False

# Configurar el listener del teclado
listener = keyboard.Listener(
    on_press=on_press,
    on_release=on_release
)
listener.start()

# Crear la ventana principal de Tkinter (oculta)
root = tk.Tk()
root.withdraw()  # Ocultar la ventana principal

# Ejecutar el bucle principal de Tkinter
root.mainloop()
