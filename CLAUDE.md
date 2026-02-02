# Claude Instructions for Hangman

## Project Overview

A Hangman word-guessing game with three versions:
- **Single-player web** (`index.html`) - Mobile-friendly, hosted on GitHub Pages
- **Multiplayer web** (`multiplayer.html`) - Turn-based game with WebSocket backend
- **Command-line** (`hangman.py`) - Python terminal game

All versions use the same 59,502-word UK English dictionary.

## Live Site

https://blaidd87.github.io/Hangman/

## Project Structure

```
Hangman/
├── index.html       # Single-player web game (HTML/CSS/JS)
├── multiplayer.html # Multiplayer web game (requires WebSocket server)
├── words.js         # Word list for web version
├── hangman.py       # Python command-line game
├── words.txt        # Word list for Python version
├── README.md        # User documentation
└── CLAUDE.md        # Developer instructions
```

## Key Files

- **words.txt / words.js** - Contains 59,502 UK English words (4-12 chars, lowercase, no apostrophes)
- **index.html** - Self-contained single-player web app, loads words.js separately
- **multiplayer.html** - Multiplayer web app requiring WebSocket server (configure WS_URL constant)
- **hangman.py** - Loads words from words.txt at runtime

## Testing

### Single-player web version
```bash
python3 -m http.server 8000
# Open http://localhost:8000 in browser
```

### Multiplayer web version
```bash
python3 -m http.server 8000
# Open http://localhost:8000/multiplayer.html in browser
# Note: Requires WebSocket server - update WS_URL in multiplayer.html
```

### Python version
```bash
python3 hangman.py
```

### Syntax check
```bash
python3 -m py_compile hangman.py
```

## Word List

Words are filtered from `/usr/share/dict/british-english`:
- Length: 4-12 characters
- Lowercase only (no proper nouns)
- Letters only (no apostrophes or hyphens)

To regenerate:
```bash
grep -E "^[a-z]{4,12}$" /usr/share/dict/british-english > words.txt
```

## Notes

- Keep both word lists in sync (words.txt and words.js)
- Single-player web version must work offline once loaded
- Mobile-friendly design is important (iPhone is primary target)
- Multiplayer requires a WebSocket server - configure the `WS_URL` constant in multiplayer.html
