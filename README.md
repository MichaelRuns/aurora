# Aurora

A terminal-based D&D-style text adventure game powered by a local LLM. This project serves as a case study for implementing chain-of-thought reasoning and tool calling with language models.

## Overview

Aurora is a "choose your own adventure" game where a local LLM acts as the dungeon master, narrating the story, managing game mechanics, and responding to player choices in real-time via streaming output.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     choose_your_adventure.py                │
│  - Main game loop                                           │
│  - Ollama API integration (streaming)                       │
│  - Conversation history management                          │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      stream_parser.py                       │
│  - Parses streaming LLM output                              │
│  - Handles tagged sections: <thinking>, <narrate>, <call>   │
│  - Colored terminal output                                  │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                       CYA_PROMPTS.py                        │
│  - System prompt defining DM behavior                       │
│  - Tool definitions (rollDice, ask)                         │
│  - Output format rules                                      │
└─────────────────────────────────────────────────────────────┘
```

## Current Features

- **Streaming responses**: Real-time text output from the LLM
- **Structured output parsing**: Handles `<thinking>`, `<narrate>`, and `<call>` tags
- **Chain-of-thought reasoning**: LLM uses `<thinking>` tags for internal logic
- **Tool system**: Support for `rollDice()` and `ask()` tool calls
- **Colored terminal output**: Cyan for thoughts, magenta for tool calls

## Requirements

- Python 3.11+
- [Ollama](https://ollama.ai/) running locally on port 11434
- Model: `llama3.2:3b` (configurable in `choose_your_adventure.py`)

## Usage

```bash
# Start Ollama (if not already running)
ollama serve

# Pull the model (first time only)
ollama pull llama3.2:3b

# Run the game
python choose_your_adventure.py
```

## Project Status

### Working
- Basic Ollama API integration
- Streaming response handling
- Tag detection in stream parser

### Known Issues / Next Steps
- **Streaming output not displaying correctly**: The `handleStreamBuffer()` method has a premature `return` statement that prevents real-time character-by-character output
- Tool call execution not implemented (calls are parsed but not executed)
- Player input loop not implemented
- Conversation history not being appended correctly after responses

## File Structure

```
aurora/
├── choose_your_adventure.py  # Main game class and entry point
├── CYA_PROMPTS.py            # System prompt and tool definitions
├── stream_parser.py          # Streaming output parser
├── README.md                 # This file
└── LICENSE                   # MIT License
```

## LLM Output Format

The system prompt instructs the LLM to output in this structure:

```xml
<thinking> [Private DM reasoning - DC calculations, NPC motivations, plot planning] </thinking>
<narrate> [Story text shown to the player] </narrate>
<call>toolName(params)</call>
```
