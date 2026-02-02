# Hangman

A classic Hangman word-guessing game with 59,502 words from the UK English dictionary.

## Play Online

**[Play Single Player](https://blaidd87.github.io/Hangman/)** - Classic solo hangman game

**[Play Multiplayer](https://blaidd87.github.io/Hangman/multiplayer.html)** - Turn-based game with friends (requires WebSocket server)

Works on any device - desktop, tablet, or mobile.

## Command-Line Version

You can also play in the terminal:

```bash
python3 hangman.py
```

## How to Play

1. A random word is selected and displayed as underscores
2. Guess one letter at a time
3. Correct guesses reveal the letter in the word
4. Wrong guesses add a part to the hangman drawing
5. Win by guessing the word before the hangman is complete (6 wrong guesses allowed)

## Features

- 59,502 words from the UK English dictionary
- Words filtered to 4-12 characters for balanced gameplay
- ASCII art hangman visualization
- Tracks guessed letters
- Play again option
- Multiplayer mode with turn-based gameplay

## Files

- `index.html` - Single-player web version
- `multiplayer.html` - Multiplayer web version (requires WebSocket server)
- `words.js` - Word list for web version
- `hangman.py` - Command-line Python version
- `words.txt` - Word list for Python version
- `backend/` - AWS Lambda backend for multiplayer (see `backend/DEPLOY.md`)

## Requirements

- Web version: Any modern browser
- Command-line version: Python 3.x
