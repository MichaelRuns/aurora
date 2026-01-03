import re

CYAN = "\033[96m"
MAGENTA = "\033[95m"
RESET_COLOR = "\033[0m"

class CyaStreamParser:
    def __init__(self):
        self.buffer = ""
        self.current_tag = None
        self.printed_length = 0

    def reset(self):
        """Reset parser state for a new response."""
        self.buffer = ""
        self.current_tag = None
        self.printed_length = 0

    def finalize(self):
        """Called when stream ends. Handle any unclosed tags (e.g., <call> stopped by stop token)."""
        if self.current_tag == "call":
            # Stream ended with unclosed <call> - this means stop token triggered
            return self.handleTagFinish(self.buffer)
        return None

    def process_chunk(self, chunk):
        self.buffer += chunk
        result = None

        # Check for opening tags
        if "<thinking>" in self.buffer and self.current_tag != "thinking":
            self.current_tag = "thinking"
            self.buffer = self.buffer.split("<thinking>")[-1]
            self.printed_length = 0
            print(f"\n{CYAN}", end="", flush=True)
        elif "<call>" in self.buffer and self.current_tag != "call":
            self.current_tag = "call"
            self.buffer = self.buffer.split("<call>")[-1]
            self.printed_length = 0
            print(f"\n{MAGENTA}", end="", flush=True)
        elif "<narrate>" in self.buffer and self.current_tag != "narrate":
            self.current_tag = "narrate"
            self.buffer = self.buffer.split("<narrate>")[-1]
            self.printed_length = 0
            print("\n", end="", flush=True)

        # Check for closing tags
        if self.current_tag and f'</{self.current_tag}>' in self.buffer:
            content = self.buffer.split(f"</{self.current_tag}>")[0]
            result = self.handleTagFinish(content)
        else:
            # Stream output while inside a tag
            self.streamCurrentBuffer()

        return result

    def streamCurrentBuffer(self):
        if self.current_tag is None:
            return

        # Only print characters we haven't printed yet
        # But be careful not to print partial closing tags
        safe_content = self.buffer
        closing_tag = f"</{self.current_tag}>"

        # Check if we might be in the middle of a closing tag
        for i in range(1, len(closing_tag)):
            if self.buffer.endswith(closing_tag[:i]):
                safe_content = self.buffer[:-i]
                break

        # Print only new content
        new_content = safe_content[self.printed_length:]
        if new_content:
            print(new_content, end="", flush=True)
            self.printed_length = len(safe_content)

    def handleTagFinish(self, content):
        # Print any remaining content we haven't streamed yet
        remaining = content[self.printed_length:]
        if remaining:
            print(remaining, end="", flush=True)

        # Reset color and add newline
        if self.current_tag in ["thinking", "call"]:
            print(f"{RESET_COLOR}")
        else:
            print()

        result = None
        if self.current_tag == "call":
            tool_call = self._parse_tool_call(content)
            result = {"tool_call": tool_call}
        # thinking and narrate don't need special handling

        # Reset state for next tag
        remainder = self.buffer.split(f"</{self.current_tag}>", 1)[-1]
        self.current_tag = None
        self.buffer = remainder
        self.printed_length = 0

        return result

    def _parse_tool_call(self, content):
        """Parse tool call like 'rollDice(d20)' or 'ask(what is your name)'"""
        # Match: toolName(args) where args can contain anything except unbalanced parens
        match = re.match(r"(\w+)\((.+)\)$", content.strip(), re.DOTALL)
        if match:
            return {
                "tool": match.group(1),
                "args": match.group(2).strip()
            }
        return {"tool": content.strip(), "args": ""}
