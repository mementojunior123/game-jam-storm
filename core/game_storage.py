from sys import platform as PLATFORM
from typing import Any
if PLATFORM == 'emscripten':
    from platform import window
    
class GameStorage:
    def __init__(self) -> None:
        self.high_score : int = 0
        self.upgrade_tokens : int = 0
    
    def load_from_file(self, file_path : str = 'assets/data/game_info.json'):
        pass

    def save_to_file(self, file_path : str = 'assets/data/game_info.json'):
        pass

    def load_from_web(self):
        self.high_score = int(self.get_web('high_score'))
        self.upgrade_tokens = int(self.get_web('upgrade_tokens'))

    def save_to_web(self):
        self.set_web('high_score', self.high_score)
        self.set_web('upgrade_tokens', self.upgrade_tokens)

    def get_web(self, key : str) -> str:
        window.localStorage.getItem(key)

    def set_web(self, key : str, value : Any):
        window.localStorage.setItem(key, str(value) )