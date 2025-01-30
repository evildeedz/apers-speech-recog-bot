import os
import platform
import sys

import pyautogui
import speech_recognition as sr
from dotenv import load_dotenv
from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtWidgets import (
    QApplication,
    QLabel,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

load_dotenv()


class VoiceRecognitionThread(QThread):
    command_recognized = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.running = False
        self.recognizer = sr.Recognizer()
        # Adjust this to tweak chunk length in seconds
        self.phrase_time_limit = 1

    def run(self):
        self.running = True
        with sr.Microphone() as source:
            # Optional: reduce background noise
            self.recognizer.adjust_for_ambient_noise(source)
            while self.running:
                try:
                    print("Listening for a short chunk...")
                    # Capture a short chunk of audio
                    audio = self.recognizer.listen(
                        source, phrase_time_limit=self.phrase_time_limit
                    )

                    # Recognize chunk with OpenAI
                    command = self.recognizer.recognize_openai(
                        audio, language="en"
                    ).lower()

                    print("Heard chunk:", command)

                    # Check for trigger words
                    triggered = False
                    for word in command.split():
                        if word in ["next", "world", "anyway", "tafel"]:
                            triggered = True
                            break

                    if triggered:
                        self.command_recognized.emit(f"Triggered command: {command}")
                        pyautogui.press("space")
                    else:
                        self.command_recognized.emit(f"Chunk recognized: {command}")

                except sr.WaitTimeoutError:
                    self.command_recognized.emit("...silence...")
                    continue
                except sr.UnknownValueError:
                    self.command_recognized.emit("Could not understand (chunk).")
                except sr.RequestError as e:
                    self.command_recognized.emit(f"API unavailable/error: {e}")
                # Loop continues for the next chunk

    def stop(self):
        self.running = False
        self.quit()
        self.wait()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Chunked Live-ish Recognition")
        self.setGeometry(100, 100, 400, 200)

        self.layout = QVBoxLayout()
        self.status_label = QLabel("Click 'Start' to begin listening.")
        self.layout.addWidget(self.status_label)

        self.start_button = QPushButton("Start Listening")
        self.start_button.clicked.connect(self.start_listening)
        self.layout.addWidget(self.start_button)

        self.stop_button = QPushButton("Stop Listening")
        self.stop_button.clicked.connect(self.stop_listening)
        self.stop_button.setEnabled(False)
        self.layout.addWidget(self.stop_button)

        container = QWidget()
        container.setLayout(self.layout)
        self.setCentralWidget(container)

        # Thread
        self.voice_thread = VoiceRecognitionThread()
        self.voice_thread.command_recognized.connect(self.update_status)

    def start_listening(self):
        self.voice_thread.start()
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.status_label.setText("Listening in short chunks...")

    def stop_listening(self):
        self.voice_thread.stop()
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.status_label.setText("Stopped listening")

    def update_status(self, message):
        self.status_label.setText(f"Status: {message}")


def main():
    if platform.system() == "Windows":
        os.environ["QT_QPA_PLATFORM"] = "windows"
    elif platform.system() == "Linux":
        os.environ["QT_QPA_PLATFORM"] = "xcb"

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
