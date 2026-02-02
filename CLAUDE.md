# Claude Instructions for Hangman

## Project Overview

A Hangman word-guessing game with two versions:
- **Web version** (`index.html`) - Mobile-friendly, hosted on GitHub Pages
- **Command-line version** (`hangman.py`) - Python terminal game

Both use the same 59,502-word UK English dictionary.

## Live Site

https://blaidd87.github.io/Hangman/

## Project Structure

```
Hangman/
├── index.html      # Web game (HTML/CSS/JS)
├── words.js        # Word list for web version
├── hangman.py      # Python command-line game
├── words.txt       # Word list for Python version
└── README.md       # Documentation
```

## Key Files

- **words.txt / words.js** - Contains 59,502 UK English words (4-12 chars, lowercase, no apostrophes)
- **index.html** - Self-contained web app, loads words.js separately
- **hangman.py** - Loads words from words.txt at runtime

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
- Web version must work offline once loaded
- Mobile-friendly design is important (iPhone is primary target)
