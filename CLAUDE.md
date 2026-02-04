# Claude Instructions for Hangman

## Project Overview

A single-player Hangman word-guessing game with two implementations:
- **Web version** (`index.html` + `words.js`) - Cyberpunk-themed, mobile-friendly, hosted on GitHub Pages
- **Command-line version** (`hangman.py` + `words.txt`) - Python terminal game

Both versions share the same 59,502-word UK English dictionary and allow 6 wrong guesses.

## Live Site

https://blaidd87.github.io/Hangman/

## Project Structure

```
Hangman/
├── index.html      # Web game (self-contained HTML/CSS/JS, loads words.js)
├── words.js        # Word list as JS array (const WORDS = [...])
├── hangman.py      # Python CLI game (standalone script)
├── words.txt       # Word list as newline-separated text
├── CLAUDE.md       # AI assistant instructions (this file)
├── README.md       # User-facing documentation
└── .gitignore      # Python, IDE, OS excludes
```

No build tools, no package managers, no external dependencies (except Google Fonts for the web version).

## Architecture

### Web Version (`index.html`)

- **Single-file app**: All HTML, CSS, and JS in one file; only `words.js` is external
- **No frameworks**: Pure vanilla HTML5/CSS3/JavaScript
- **Fonts**: Orbitron (headings/buttons) and Share Tech Mono (ASCII art) via Google Fonts
- **Input**: Both mouse clicks on letter buttons and keyboard keypresses (a-z)
- **State**: All game state in JS variables (`word`, `guessedLetters` Set, `wrongGuesses`, `gameOver`); no persistence between sessions
- **Constants**: `HANGMAN_STAGES` (7 ASCII art stages), `MAX_WRONG = 6`
- **Key functions**: `init()`, `createKeyboard()`, `updateDisplay()`, `guess(letter)`, `checkGameEnd()`

### Python Version (`hangman.py`)

- **Standalone script** with `#!/usr/bin/env python3` shebang
- **Standard library only**: `random`, `pathlib`
- **Word loading**: Reads `words.txt` relative to script location via `pathlib`; falls back to a built-in word list if file is missing
- **Constants**: `HANGMAN_STAGES` (7 stages), `MAX_WRONG_GUESSES = 6`
- **Key functions**: `load_words()`, `get_display_word()`, `play_game()`, `main()`
- **Input validation**: Single alphabetic character, duplicate detection, case-insensitive

### Word Lists

- **Source**: Filtered from `/usr/share/dict/british-english`
- **Criteria**: 4-12 characters, lowercase only, letters only (no apostrophes, hyphens, or proper nouns)
- **Count**: 59,502 words
- **Formats**: `words.txt` (newline-separated), `words.js` (JS array: `const WORDS = [...]`)
- **Regenerate**: `grep -E "^[a-z]{4,12}$" /usr/share/dict/british-english > words.txt`

## Visual Design

The web version uses a **cyberpunk/neon aesthetic**:

- **Color palette**: Cyan (#00ffff) primary, magenta (#ff00ff) secondary, lime (#00ff88) accent, dark backgrounds (#0a0a0f, #0d0d15, #1a1a2e)
- **Effects**: Glowing text shadows, animated grid overlay, border glow animation (3s cycle), title flicker (5s cycle)
- **Typography**: Orbitron (headings, buttons) with uppercase transforms and wide letter-spacing; Share Tech Mono for ASCII art
- **Layout**: Max 500px centered container, 7-column grid keyboard, responsive for mobile
- **Win/lose messages**: "System Unlocked" (win) / "Access Denied: [word]" (lose) - themed as hacking a system

## Coding Conventions

### JavaScript (web)
- camelCase for variables and functions: `guessedLetters`, `updateDisplay()`
- UPPER_CASE for constants: `HANGMAN_STAGES`, `MAX_WRONG`
- `Set` for tracking guessed letters
- All code inline in `<script>` tag within `index.html`
- Minimal comments

### Python (CLI)
- snake_case for variables and functions: `load_words()`, `get_display_word()`
- UPPER_CASE for constants: `HANGMAN_STAGES`, `MAX_WRONG_GUESSES`
- Docstrings on all functions
- f-strings for formatting
- `pathlib` for file paths
- Standard `if __name__ == "__main__"` guard

## Testing

### Web version
```bash
python3 -m http.server 8000
# Open http://localhost:8000 in browser
```

### Python version
```bash
python3 hangman.py
```

### Python syntax check
```bash
python3 -m py_compile hangman.py
```

There are no automated tests. Verify changes by playing through a game manually.

## Deployment

- **GitHub Pages**: The web version auto-deploys from the main branch. No build step required.
- **No CI/CD pipelines**: No GitHub Actions or other automation configured.
- **PR-based workflow**: Changes go through pull requests.

## Important Rules

1. **Keep word lists in sync** - `words.txt` and `words.js` must contain the same words
2. **Web version must work offline** once initially loaded (no runtime API calls)
3. **Mobile-first design** - iPhone is the primary target device
4. **No external JS/CSS libraries** - Keep the web version dependency-free
5. **Maintain the cyberpunk theme** - All UI changes should be consistent with the neon/cyberpunk aesthetic
6. **Single-player only** - Multiplayer was previously removed; do not re-add it
7. **Self-contained web app** - All HTML/CSS/JS stays in `index.html`; only `words.js` is separate
