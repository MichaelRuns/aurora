"""
A text based game where the user may choose their own adventure, DND style.
"""
import re
import random
import requests
import json
from CYA_PROMPTS import SYSTEM_PROMPT, ART_SYSTEM_PROMPT
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
            {"role": "user", "content": "The game has started. Decide upon a unique and interesting setting. You may choose to ask the play once about what kind of story they want"}
        ]
        self.stream_parser = CyaStreamParser()

    def start(self):
        while True:
            result = self._ask_ollama()

            if result.get("tool_call"):
                tool_result = self._execute_tool(result["tool_call"])
                self._handle_tool_result(result["tool_call"], tool_result)
            else:
                # LLM didn't use ask() tool - remind it to prompt the player
                self.messages.append({
                    "role": "user",
                    "content": "[System] You did not take an action. You should call a tool to pass the turn to the user or the system."
                })

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
                        "temperature": 0.7,
                        "num_predict": 1024,
                        "num_ctx": 8192,
                        "stop": ["</call>"]
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

        # Check for unclosed <call> tag (stop token triggered before </call>)
        if not tool_call:
            final_result = self.stream_parser.finalize()
            if final_result and final_result.get("tool_call"):
                tool_call = final_result["tool_call"]

        # Append assistant response to history (add </call> if it was truncated)
        if full_response:
            if tool_call:
                full_response += "</call>"
            self.messages.append({"role": "assistant", "content": full_response})

        return {"tool_call": tool_call}

    def _execute_tool(self, tool_call):
        tool_name = tool_call.get("tool")
        args = tool_call.get("args", "")

        if tool_name == "rollDice":
            return self._roll_dice(args)
        elif tool_name == "ask":
            return self._ask_player(args)
        elif tool_name == "choice":
            return self._choice_player(args)
        elif tool_name == "art":
            return self._generate_art(args)
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
        print(f"\n❓ {question}")
        try:
            answer = input("> ")
            return answer
        except (KeyboardInterrupt, EOFError):
            return ""

    def _choice_player(self, args):
        parts = [p.strip() for p in args.split("|")]
        if len(parts) < 3:
            # Fallback to ask if not enough options
            return self._ask_player(args)

        question = parts[0]
        options = parts[1:]

        print(f"\n❓ {question}")
        for i, option in enumerate(options, 1):
            print(f"  {i}. {option}")

        try:
            while True:
                choice = input("> ").strip()
                # Accept number or text
                if choice.isdigit():
                    idx = int(choice) - 1
                    if 0 <= idx < len(options):
                        return options[idx]
                    print(f"Please enter a number between 1 and {len(options)}")
                else:
                    # Accept text input as custom response
                    return choice
        except (KeyboardInterrupt, EOFError):
            return options[0] if options else ""

    def _generate_art(self, description):
        print("\n🎨 Generating art...\n")
        try:
            response = requests.post(
                f"{BASE_URL}/api/chat",
                json={
                    "model": MODEL,
                    "messages": [
                        {"role": "system", "content": ART_SYSTEM_PROMPT},
                        {"role": "user", "content": description}
                    ],
                    "stream": False,
                    "options": {"temperature": 0.9, "num_predict": 512}
                },
                timeout=60
            )
            art = response.json()["message"]["content"]
            print(art)
            print()
            return "[ASCII art displayed]"
        except Exception as e:
            print(f"Failed to generate art: {e}")
            return "[Art generation failed]"

    def _handle_tool_result(self, tool_call, result):
        tool_name = tool_call.get("tool", "unknown")
        self.messages.append({
            "role": "user",
            "content": f"[Tool Result] {tool_name} returned: {result}"
        })


if __name__ == '__main__':
    main()
