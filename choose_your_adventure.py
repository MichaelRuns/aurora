"""
A text based game where the user may choose their own adventure, DND style. 
"""
import re
import requests
import json
from CYA_PROMPTS import SYSTEM_PROMPT
from stream_parser import CyaStreamParser




BASE_URL: str = "http://localhost:11434"
MODEL: str = "llama3.2:3b"

def main():
   cya_game = CYA_GAME()
   cya_game.start()

class CYA_GAME():
    conversation: str
    history: list
    def __init__(self):
        self.conversation = "[role: system] the game has started. Decide upon an unique and interesting setting"
        self.stream_parser = CyaStreamParser()
        self.history = []

    def start(self):
        self._ask_ollama()

    def _ask_ollama(self):
        with requests.post(
                f"{BASE_URL}/api/generate",
                json={
                    "model": MODEL,
                    "prompt": self.conversation,
                    "system": SYSTEM_PROMPT,
                    "stream": True,
                    "options": {
                        "temperature": 0.4,
                        "num_predict": 1024,
                        "num_ctx": 8192
                    }
                },
                timeout=120,
                stream=True
            ) as response:
                for line in response.iter_lines():
                    if not line:
                        continue
                    chunk = json.loads(line)
                    text_piece = chunk.get("response", "")
                    self.stream_parser.process_chunk(text_piece)
    
    def save_narrator_msg(self, output):
        narrator_msg = "<NARRATOR>" + json.dumps(output) + "</NARRATOR>"
        self.conversation += narrator_msg
    def debug():
        pass


if __name__ == '__main__':
    main()