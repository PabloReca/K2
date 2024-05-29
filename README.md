
# k2 Application

## Description

The k2 application is a Python-based tool that maps keyboard inputs to MIDI control change messages. It uses the `pynput` library to listen for keyboard events and `mido` to send MIDI messages. A Tkinter GUI is used to display notifications when keys are pressed.

## Features

- Listens for keyboard events.
- Maps keys to MIDI control change messages based on a YAML configuration file.
- Displays a popup notification with the key information when a key is pressed.

## Requirements

- Python 3.x
- `pynput` library
- `mido` library
- `python-rtmidi` backend
- `yaml` library
- `tkinter` library

## Installation

1. Clone the repository or download the source code.
2. Set up a virtual environment (optional but recommended):
    ```sh
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```
3. Install the required libraries:
    ```sh
    pip install -r requirements.txt
    ```

## Configuration

Create a `note_cc_mapping.yml` file in the same directory as the script. This file should contain mappings of key codes to MIDI control change messages. An example format is provided below:

```yaml
note_cc_mapping:
  65: "C,64"
  83: "D,65"
  68: "E,66"
```

In this example, key code 65 (A key) is mapped to the note C with control change value 64.

## Usage

Run the application with the following command:

```sh
python k2.py
```

The application will open a MIDI output port and start listening for keyboard events. When a mapped key is pressed, it will send the corresponding MIDI control change message and display a popup notification.

## Note

Ensure that the MIDI output port name in the script matches the one available on your system. Modify the following line in `k2.py` if necessary:

```python
midi_out = mido.open_output('K2 1')
```

## Troubleshooting

- If you encounter an error opening the MIDI port, ensure the port name is correct and that `python-rtmidi` is installed.
- If the script fails to load the YAML file, ensure the file path is correct and that the file is properly formatted.

## License

This project is licensed under the MIT License. See the LICENSE file for more details.

---

This README provides a basic overview of the k2 application, its features, installation instructions, and usage guidelines. For further details, refer to the source code and configuration files.
