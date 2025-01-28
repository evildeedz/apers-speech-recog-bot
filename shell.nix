{
  pkgs ? import <nixpkgs> { },
}:
pkgs.mkShell {
  packages = [
    (pkgs.python3.withPackages (python-pkgs: [
      python-pkgs.pyqt6
      python-pkgs.pyautogui
      python-pkgs.speechrecognition
      python-pkgs.pyaudio
      python-pkgs.openai-whisper
      python-pkgs.soundfile
      python-pkgs.pyinstaller
    ]))
  ];
}
