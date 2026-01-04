# Aurora

A terminal-based D&D-style text adventure game powered by a local LLM. Aurora demonstrates advanced LLM patterns including chain-of-thought reasoning, structured output parsing, and real-time streaming interactions.

## Overview

Aurora is an interactive RPG where a local LLM acts as the dungeon master, creating dynamic stories, managing game mechanics, and responding to player choices in real-time. The game features streaming narrative output with colored terminal display and intelligent tool calling for dice rolls, player input, and ASCII art generation.

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

## Features

- **Real-time streaming**: Character-by-character streaming output with proper tag handling
- **Structured output parsing**: Handles `<thinking>`, `<narrate>`, and `<call>` tags in streaming mode
- **Chain-of-thought reasoning**: LLM uses `<thinking>` tags for internal planning and decision-making
- **Comprehensive tool system**:
  - `rollDice()`: Roll dice for skill checks and story events
  - `ask()`: Get open-ended player input
  - `choice()`: Present multiple-choice decisions
  - `art()`: Generate ASCII art for dramatic moments
- **Colored terminal output**: Cyan for thoughts, magenta for tool calls, default for narration
- **Full game loop**: Complete turn-based interaction with automatic history management
- **Conversation history**: Maintains context across the entire session

## Requirements

- Python 3.11+
- [Ollama](https://ollama.ai/) running locally on port 11434
- Model: `llama3.2:3b` (configurable in `choose_your_adventure.py`)
- Required Python packages: `requests`

## Installation & Usage

```bash
# Clone the repository
git clone https://github.com/yourusername/aurora.git
cd aurora

# Create and activate virtual environment (optional but recommended)
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install requests

# Start Ollama (if not already running)
ollama serve

# Pull the model (first time only)
ollama pull llama3.2:3b

# Run the game
python choose_your_adventure.py
```

## Gameplay

The game starts with the LLM choosing a unique setting and may ask what kind of story you prefer. From there:

1. The DM narrates the story using colored, streaming text
2. You'll be prompted to make decisions via:
   - **Open-ended questions**: Type your character's actions
   - **Multiple choice**: Select from numbered options or type custom responses
   - **Dice rolls**: Automatic rolls for skill checks and random events
3. The game maintains full context of your adventure throughout the session
4. Press `Ctrl+C` to exit at any time

## How It Works

### Structured LLM Output

The system prompt instructs the LLM to structure responses using XML-like tags:

```xml
<thinking>
  [Internal reasoning: NPC motivations, DC calculations, plot planning]
</thinking>
<narrate>
  [Story narration visible to the player]
</narrate>
<call>toolName(arguments)</call>
```

### Streaming Parser

The `CyaStreamParser` class handles real-time parsing of streaming LLM output:
- Detects opening tags and switches display modes (colors)
- Streams content character-by-character as it arrives
- Handles partial tag detection to avoid printing incomplete closing tags
- Parses tool calls when `</call>` tag completes
- Supports stop tokens (stream can end mid-tag)

### Game Loop

1. Game sends conversation history to Ollama API
2. Stream parser processes chunks in real-time, displaying colored output
3. When a tool call is detected, the parser returns it to the game
4. Game executes the tool (dice roll, player input, etc.)
5. Tool result is appended to conversation history
6. Loop continues with updated context

## Technical Highlights

- **Stop token handling**: Uses `</call>` as a stop token to terminate generation immediately after tool calls, improving response time
- **Streaming with tags**: Custom parser handles interleaved tags in streaming mode without buffering entire response
- **Color management**: Proper ANSI color code handling with reset to avoid terminal corruption
- **Conversation context**: Full message history maintained with proper role assignments (system/user/assistant)

## File Structure

```
aurora/
├── choose_your_adventure.py  # Main game class, game loop, and tool execution
├── CYA_PROMPTS.py            # System prompts for DM and ASCII art generation
├── stream_parser.py          # Real-time streaming output parser with tag detection
├── README.md                 # This file
└── LICENSE                   # MIT License
```

## Configuration

You can customize the game by editing variables in `choose_your_adventure.py`:

```python
BASE_URL = "http://localhost:11434"  # Ollama server URL
MODEL = "llama3.2:3b"                # LLM model to use
```

Ollama options can be adjusted in the `_ask_ollama()` method:
- `temperature`: Controls randomness (default: 0.7)
- `num_predict`: Max tokens per response (default: 1024)
- `num_ctx`: Context window size (default: 8192)

## Future Enhancements

Potential additions to explore:
- Character sheet tracking (stats, inventory, health)
- Save/load game state
- Combat system with turn-based mechanics
- Multi-model support (Claude, GPT, etc.)
- Image generation integration for key scenes
- Sound effects or background music
- Configurable difficulty settings

## License

MIT License - See LICENSE file for details
