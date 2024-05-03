import sys
from datetime import datetime

import Quartz
import mido
from AppKit import NSApplication, NSApp
from Foundation import NSObject, NSLog
from PyQt5.QtCore import QTimer, Qt, pyqtSignal, QObject
from PyQt5.QtGui import QFont, QColor, QPalette
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout
from mido import Message

class MidiManager:
    def __init__(self):
        self.outport = mido.open_output(name='K2', virtual=True)

    def send_cc_message(self, value):
        message = Message('control_change', control=20, value=value)
        self.outport.send(message)
        return True


class AlertManager(QObject):
    show_alert = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.app = QApplication(sys.argv)
        self.setup_alert_window()
        self.timer = QTimer()
        self.timer.setInterval(1500)
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.window.hide)

    def setup_alert_window(self):
        self.window = QWidget()
        self.window.setWindowTitle('Alerta de Cambio de Nota')
        self.window.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(255, 0, 0))
        self.window.setPalette(palette)
        self.window.setAutoFillBackground(True)
        self.window.resize(300, 150)
        layout = QVBoxLayout()
        self.label = QLabel("Key Change:")
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setFont(QFont('Arial', 32))
        self.label.setStyleSheet("color: white;")
        layout.addWidget(self.label)
        self.window.setLayout(layout)

        self.show_alert.connect(self.show_message)

    def show_message(self, message):
        self.label.setText(f"Key Change: {message}")
        self.window.show()
        self.timer.start()


class AppDelegate(NSObject):
    def applicationDidFinishLaunching_(self, notification):
        NSLog("K2 launched.")


def get_note_and_modifiers(key_code, modifiers, is_key_down):
    # Mapeo de keycodes a valores CC y nombres de notas
    note_cc_mapping = {
        105: ('C', 1),
        106: ('Db', 15),
        64: ('D', 23),
        79: ('Eb', 37),
        80: ('E', 50),
        90: ('F', 62),
    }
    alt_note_cc_mapping = {
        105: ('F#', 72),
        106: ('G', 82),
        64: ('Ab', 91),
        79: ('A', 105),
        80: ('Bb', 115),
        90: ('B', 127),
    }
    note_tuple = alt_note_cc_mapping.get(key_code, note_cc_mapping.get(key_code, (
        'Unknown Note', None))) if 'Alt' in modifiers else note_cc_mapping.get(key_code, ('Unknown Note', None))
    return note_tuple if is_key_down and note_tuple[1] is not None else None


def key_event_callback(proxy, type_, event, refcon):
    key_code = Quartz.CGEventGetIntegerValueField(event, Quartz.kCGKeyboardEventKeycode)
    is_key_down = type_ == Quartz.kCGEventKeyDown

    if not is_key_down:
        return event

    modifier_flags = Quartz.CGEventGetFlags(event)
    modifiers = []
    if modifier_flags & Quartz.kCGEventFlagMaskShift:
        modifiers.append('Shift')
    if modifier_flags & Quartz.kCGEventFlagMaskAlternate:
        modifiers.append('Alt')
    if modifier_flags & Quartz.kCGEventFlagMaskControl:
        modifiers.append('Control')
    if modifier_flags & Quartz.kCGEventFlagMaskCommand:
        modifiers.append('Cmd')

    note_tuple = get_note_and_modifiers(key_code, modifiers, is_key_down)

    if note_tuple:
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        print(f"Key pressed: {key_code} {note_tuple[0]} + {timestamp}")
        if midi_manager.send_cc_message(note_tuple[1]):
            alert_manager.show_alert.emit(note_tuple[0])

    return event


def main():
    global alert_manager, midi_manager
    alert_manager = AlertManager()
    midi_manager = MidiManager()
    app = NSApplication.sharedApplication()
    delegate = AppDelegate.alloc().init()
    NSApp().setDelegate_(delegate)
    NSApp().finishLaunching()

    event_mask = (Quartz.CGEventMaskBit(Quartz.kCGEventKeyDown) |
                  Quartz.CGEventMaskBit(Quartz.kCGEventKeyUp))
    event_tap = Quartz.CGEventTapCreate(Quartz.kCGSessionEventTap,
                                        Quartz.kCGHeadInsertEventTap,
                                        Quartz.kCGEventTapOptionDefault,
                                        event_mask,
                                        key_event_callback,
                                        None)

    if not event_tap:
        print("Failed to create event tap")
        exit(1)

    run_loop_source = Quartz.CFMachPortCreateRunLoopSource(None, event_tap, 0)
    Quartz.CFRunLoopAddSource(Quartz.CFRunLoopGetCurrent(), run_loop_source, Quartz.kCFRunLoopCommonModes)
    Quartz.CGEventTapEnable(event_tap, True)

    NSApp().run()


if __name__ == '__main__':
    main()
