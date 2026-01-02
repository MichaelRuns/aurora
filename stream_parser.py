CYAN = "\033[96m"
MAGENTA = "\033[95m"
RESET = "\033[0m"

class CyaStreamParser:
    def __init__(self):
        self.buffer = ""
        self.current_tag = None
    def process_chunk(self, chunk):
        # print(f"[DEBUG] chunk:{chunk} buffer:{self.buffer}, current_tag:{self.current_tag}")
        self.buffer += chunk
        if "<thinking>" in self.buffer and self.current_tag != "thinking":
                self.current_tag = "thinking"
                self.buffer = self.buffer.split("<thinking>")[-1]
        elif "<call>" in self.buffer and self.current_tag != "call":
                self.current_tag = "call"
                self.buffer = self.buffer.split("<call>")[-1]
        elif "<narrate>" in self.buffer and self.current_tag != "narrate":
              print("\nNarrator: ", end="", flush=True)
              self.current_tag = "narrate"
              self.buffer=self.buffer.split("<narrate>")[-1]
        if self.current_tag and f'</{self.current_tag}>' in self.buffer:
              content = self.buffer.split(f"</{self.current_tag}>")[0]
              self.handleTagFinish(content)
        self.handleStreamBuffer()
    
    def handleStreamBuffer(self):
         if self.current_tag not in ["narrate", "thinking"]:
              return
         return
         print(self.buffer, end="", flush=True)
    
    def printThought(self, content):
       print(f"{CYAN}{content}{RESET}")
       pass
    
    def printNarration(self, content):
        print(content)
        pass
    
    def handleTagFinish(self,content):
        if self.current_tag == "call":
            self.handleCall(content)
        elif self.current_tag == "thinking":
             self.printThought(content)
             return {"role: ASSISTANT", f"<thinking>{content}</content>"}
        elif self.current_tag == "narrate":
            self.printNarration(content)
            return {"role: ASSISTANT", f"<narrate>{content}</narrate>"}
        self.current_tag = None
        self.buffer = ""
        

    
    def handleCall(self, content):
          return {"role: ASSISTANT", f"<call>{content}</call>"}
          print(f"\n{MAGENTA}{content}{RESET}")
