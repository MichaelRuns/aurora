"""
A text based game where the user may choose their own adventure, DND style.
"""
import re
import random
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
    def __init__(self):
        self.messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": "The game has started. Decide upon a unique and interesting setting."}
        ]
        self.stream_parser = CyaStreamParser()

    def start(self):
        while True:
            result = self._ask_ollama()

            if result.get("tool_call"):
                tool_result = self._execute_tool(result["tool_call"])
                self._handle_tool_result(result["tool_call"], tool_result)
            else:
                try:
                    user_input = input("\n> ")
                    if user_input.lower() in ["quit", "exit", "q"]:
                        print("Thanks for playing!")
                        break
                    self.messages.append({"role": "user", "content": user_input})
                except (KeyboardInterrupt, EOFError):
                    print("\nThanks for playing!")
                    break

    def _ask_ollama(self):
        full_response = ""
        tool_call = None
        self.stream_parser.reset()

        with requests.post(
                f"{BASE_URL}/api/chat",
                json={
                    "model": MODEL,
                    "messages": self.messages,
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
                    text_piece = chunk.get("message", {}).get("content", "")
                    full_response += text_piece
                    result = self.stream_parser.process_chunk(text_piece)
                    if result and result.get("tool_call"):
                        tool_call = result["tool_call"]

        # Append assistant response to history
        if full_response:
            self.messages.append({"role": "assistant", "content": full_response})

        return {"tool_call": tool_call}

    def _execute_tool(self, tool_call):
        tool_name = tool_call.get("tool")
        args = tool_call.get("args", "")

        if tool_name == "rollDice":
            return self._roll_dice(args)
        elif tool_name == "ask":
            return self._ask_player(args)
        else:
            return f"Unknown tool: {tool_name}"

    def _roll_dice(self, notation):
        # Parse dice notation like "d20", "2d6", "1d20"
        match = re.match(r"(\d*)d(\d+)", notation.strip())
        if not match:
            return f"Invalid dice notation: {notation}"

        count = int(match.group(1)) if match.group(1) else 1
        sides = int(match.group(2))

        rolls = [random.randint(1, sides) for _ in range(count)]
        total = sum(rolls)

        if count == 1:
            print(f"\n🎲 Rolled {notation}: {total}")
        else:
            print(f"\n🎲 Rolled {notation}: {rolls} = {total}")

        return str(total)

    def _ask_player(self, question):
        print(f"\n❓ DM asks: {question}")
        try:
            answer = input("> ")
            return answer
        except (KeyboardInterrupt, EOFError):
            return ""

    def _handle_tool_result(self, tool_call, result):
        tool_name = tool_call.get("tool", "unknown")
        self.messages.append({
            "role": "user",
            "content": f"[Tool Result] {tool_name} returned: {result}"
        })


if __name__ == '__main__':
    main()
