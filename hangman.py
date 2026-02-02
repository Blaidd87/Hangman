#!/usr/bin/env python3
"""A simple command-line Hangman game."""

import random

WORDS = [
    "python", "hangman", "programming", "computer", "keyboard",
    "developer", "algorithm", "function", "variable", "software",
    "terminal", "debugging", "interface", "database", "network"
]

HANGMAN_STAGES = [
    """
       ------
       |    |
       |
       |
       |
       |
    --------
    """,
    """
       ------
       |    |
       |    O
       |
       |
       |
    --------
    """,
    """
       ------
       |    |
       |    O
       |    |
       |
       |
    --------
    """,
    """
       ------
       |    |
       |    O
       |   /|
       |
       |
    --------
    """,
    """
       ------
       |    |
       |    O
       |   /|\\
       |
       |
    --------
    """,
    """
       ------
       |    |
       |    O
       |   /|\\
       |   /
       |
    --------
    """,
    """
       ------
       |    |
       |    O
       |   /|\\
       |   / \\
       |
    --------
    """
]

MAX_WRONG_GUESSES = len(HANGMAN_STAGES) - 1


def get_display_word(word, guessed_letters):
    """Return the word with unguessed letters as underscores."""
    return " ".join(letter if letter in guessed_letters else "_" for letter in word)


def play_game():
    """Play a single game of Hangman."""
    word = random.choice(WORDS).lower()
    guessed_letters = set()
    wrong_guesses = 0

    print("\n" + "=" * 40)
    print("     WELCOME TO HANGMAN!")
    print("=" * 40)

    while wrong_guesses < MAX_WRONG_GUESSES:
        print(HANGMAN_STAGES[wrong_guesses])
        print(f"Word: {get_display_word(word, guessed_letters)}")
        print(f"Guessed letters: {', '.join(sorted(guessed_letters)) if guessed_letters else 'None'}")
        print(f"Wrong guesses remaining: {MAX_WRONG_GUESSES - wrong_guesses}")

        # Check for win
        if all(letter in guessed_letters for letter in word):
            print(f"\nCongratulations! You won! The word was: {word}")
            return True

        # Get player's guess
        guess = input("\nGuess a letter: ").lower().strip()

        # Validate input
        if len(guess) != 1 or not guess.isalpha():
            print("Please enter a single letter.")
            continue

        if guess in guessed_letters:
            print(f"You already guessed '{guess}'. Try again.")
            continue

        guessed_letters.add(guess)

        if guess in word:
            print(f"Good guess! '{guess}' is in the word.")
        else:
            wrong_guesses += 1
            print(f"Sorry, '{guess}' is not in the word.")

    # Game over - player lost
    print(HANGMAN_STAGES[wrong_guesses])
    print(f"\nGame Over! The word was: {word}")
    return False


def main():
    """Main function to run the Hangman game."""
    while True:
        play_game()
        play_again = input("\nPlay again? (y/n): ").lower().strip()
        if play_again != 'y':
            print("Thanks for playing Hangman! Goodbye!")
            break


if __name__ == "__main__":
    main()
