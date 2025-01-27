import os
import sys

import pyautogui
import speech_recognition as sr
from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtWidgets import (
    QApplication,
    QLabel,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class VoiceRecognitionThread(QThread):
    command_recognized = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.running = False
        self.recognizer = sr.Recognizer()

    def run(self):
        self.running = True
        with sr.Microphone() as source:
            self.recognizer.adjust_for_ambient_noise(source)
            while self.running:
                try:
                    print("Listening for the command 'Next'...")
                    audio = self.recognizer.listen(source, timeout=10)
                    command = self.recognizer.recognize_whisper(audio).lower()
                    print(command)
                    if "next" in command:
                        self.command_recognized.emit("Next")
                        pyautogui.press("space")
                    else:
                        self.command_recognized.emit(f"Unrecognized command: {command}")
                except sr.UnknownValueError:
                    self.command_recognized.emit(
                        "Sorry, I couldn't understand the audio."
                    )
                except sr.RequestError:
                    self.command_recognized.emit(
                        "Speech recognition service is unavailable."
                    )
                except sr.WaitTimeoutError:
                    self.command_recognized.emit("Listening timed out.")

    def stop(self):
        self.running = False
        self.quit()
        self.wait()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Voice-Controlled Spacebar")
        self.setGeometry(100, 100, 400, 200)

        # Main layout
        self.layout = QVBoxLayout()

        # Status label
        self.status_label = QLabel("Status: Click 'Start' to begin listening")
        self.layout.addWidget(self.status_label)

        # Start button
        self.start_button = QPushButton("Start Listening")
        self.start_button.clicked.connect(self.start_listening)
        self.layout.addWidget(self.start_button)

        # Stop button
        self.stop_button = QPushButton("Stop Listening")
        self.stop_button.clicked.connect(self.stop_listening)
        self.stop_button.setEnabled(False)
        self.layout.addWidget(self.stop_button)

        # Set central widget
        container = QWidget()
        container.setLayout(self.layout)
        self.setCentralWidget(container)

        # Voice recognition thread
        self.voice_thread = VoiceRecognitionThread()
        self.voice_thread.command_recognized.connect(self.update_status)

    def start_listening(self):
        self.voice_thread.start()
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.status_label.setText("Status: Listening...")

    def stop_listening(self):
        self.voice_thread.stop()
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.status_label.setText("Status: Stopped listening")

    def update_status(self, message):
        self.status_label.setText(f"Status: {message}")


def main():
    os.environ["QT_QPA_PLATFORM"] = "xcb"
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
