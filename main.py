import json
import sys

from PyQt5.QtCore import QEvent, Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout,
                             QLineEdit, QPushButton, QListWidget, QListWidgetItem,
                             QMessageBox, QComboBox)


class SongWidget(QWidget):
    def __init__(self, song=None, key=None, parent=None):
        super().__init__(parent)
        self.initUI(song, key)
        self.setupConnections()

    def initUI(self, song, key):
        layout = QHBoxLayout(self)
        self.songEdit = QLineEdit(song if song else '')
        self.songEdit.setPlaceholderText("Enter song title")
        self.songEdit.setFixedSize(200, 30)
        self.keySelect = QComboBox()
        self.keySelect.addItems(["C", "D", "E", "F", "G", "A", "B"])
        if key:
            self.keySelect.setCurrentText(key)
        else:
            self.keySelect.setCurrentIndex(-1)

        self.deleteButton = QPushButton("x")
        self.deleteButton.clicked.connect(self.removeSelf)

        layout.addWidget(self.songEdit)
        layout.addWidget(self.keySelect)
        layout.addWidget(self.deleteButton)

    def setupConnections(self):
        self.songEdit.textChanged.connect(self.onDataChanged)
        self.keySelect.currentIndexChanged.connect(self.onDataChanged)

    def onDataChanged(self):
        parentWidget = self.parent().parent()
        if isinstance(parentWidget, MusicLibraryWidget):
            parentWidget.saveSongs()

    def removeSelf(self):
        self.setParent(None)
        self.deleteLater()


class MusicLibraryWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.loadSongs()

    def initUI(self):
        self.setGeometry(100, 100, 600, 700)
        self.setWindowTitle('Music Library')
        mainLayout = QVBoxLayout(self)

        self.songList = QListWidget()
        self.songList.setDragDropMode(QListWidget.InternalMove)
        self.songList.installEventFilter(self)
        self.songList.setStyleSheet(
            "QListWidget::item:selected { background-color: #add8e6; }"
            "QListWidget::item:selected:focus { background-color: #add8e6; }"
        )
        mainLayout.addWidget(self.songList)
        self.addEntryRow()

    def addEntryRow(self):
        songWidget = SongWidget()
        listItem = QListWidgetItem(self.songList)
        listItem.setSizeHint(songWidget.sizeHint())
        self.songList.setItemWidget(listItem, songWidget)
        listItem.setFlags(listItem.flags() & ~Qt.ItemIsDragEnabled)
        songWidget.deleteButton.setText('+')
        songWidget.deleteButton.clicked.disconnect()
        songWidget.deleteButton.clicked.connect(lambda: self.addSong(songWidget))
        songWidget.keySelect.setCurrentIndex(-1)

    def addSong(self, songWidget):
        song = songWidget.songEdit.text()
        key = songWidget.keySelect.currentText()
        if song and key:
            self.addSongToUI(song, key)
            songWidget.songEdit.clear()
            songWidget.keySelect.setCurrentIndex(-1)
            self.saveSongs()
        else:
            QMessageBox.warning(self, "Error", "Both song title and key must be filled.")

    def addSongToUI(self, song, key):
        newSongWidget = SongWidget(song, key)
        newListItem = QListWidgetItem(self.songList)
        newListItem.setSizeHint(newSongWidget.sizeHint())
        self.songList.setItemWidget(newListItem, newSongWidget)

    def saveSongs(self):
        songs = []
        for index in range(self.songList.count()):
            widget = self.songList.itemWidget(self.songList.item(index))
            song = widget.songEdit.text().strip()
            key = widget.keySelect.currentText().strip()
            if song and key:
                songs.append({'index': index, 'song': song, 'key': key})

        with open('songs.json', 'w') as file:
            json.dump(songs, file, indent=4)

    def loadSongs(self):
        try:
            with open('songs.json', 'r') as file:
                songs = json.load(file)
            for song in sorted(songs, key=lambda x: x['index']):
                self.addSongToUI(song['song'], song['key'])
        except FileNotFoundError:
            # El archivo no existe, por lo tanto, puede ser la primera vez que se ejecuta la aplicación.
            print("No se encontró el archivo songs.json, se creará uno nuevo al guardar canciones.")
        except json.JSONDecodeError:
            # El archivo está vacío o mal formado, continuar sin cargar nada.
            print("El archivo songs.json está vacío o mal formado, se ignorará.")

    def eventFilter(self, source, event):
        if event.type() == QEvent.ChildAdded or event.type() == QEvent.ChildRemoved:
            self.saveSongs()
        elif event.type() == QEvent.ChildPolished:  # Puede indicar un reordenamiento
            self.saveSongs()
        return super().eventFilter(source, event)


app = QApplication(sys.argv)
font = QFont()
font.setPixelSize(18)
app.setFont(font)
window = MusicLibraryWidget()
window.show()
sys.exit(app.exec_())
