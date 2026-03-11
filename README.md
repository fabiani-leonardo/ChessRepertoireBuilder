# ChessRepertoireBuilder ♟️

A Python/Pygame application to build and train your personal chess repertoire, featuring live Stockfish analysis and Lichess human database integration.

## ✨ Features
* **Dual Repertoire Management:** Build and manage separate opening repertoires for White and Black.
* **Lichess Database API (New!):** Shows the most played moves by human players in real-time, helping you prepare for practical play.
* **Weighted Training (New!):** During training, the computer plays opponent responses based on their actual frequency in the Lichess database!
* **Visual Match Feedback (New!):** A green dot indicator appears next to Stockfish/Lichess moves if they are already saved in your repertoire.
* **Live Stockfish Analysis:** Integrated Stockfish engine provides real-time evaluations, top 3 engine lines, and a dynamic evaluation bar.
* **Bulk PGN Import:** Easily import existing PGN files. The app parses the entire PGN tree (including all sub-variations) and merges them into your JSON.
* **Visual & Audio Feedback:** Features highlighted squares for previous moves, move/capture sound effects, and error buzzers.
* **Auto-Saving:** All your moves are continuously saved to a local `repertoire.json` file.

## 🚀 Installation and Setup

1. Clone this repository.
2. Create a virtual environment and install the required dependencies: `pip install pygame-ce chess requests`
3. **Stockfish Engine:**
   * Download Stockfish (AVX2 version recommended) from [stockfishchess.org](https://stockfishchess.org/download/).
   * Extract the `.exe` file and place it in the root folder of the project.
   * Make sure the name matches the `STOCKFISH_FILENAME` variable inside `gui.py`.
4. **Lichess API Token (Required for Human DB):**
   * Go to Lichess.org -> Preferences -> Personal Access Tokens.
   * Generate a new token (no special permissions needed).
   * Create a file named `token.txt` in the project root and paste ONLY the token string inside.
5. **Assets:** Ensure you have the `images/` and `sounds/` folders populated with the required files.
6. Run the program: `python gui.py` (or use your `avvia.bat` script).

## 🎮 How to Use

When you launch the app, you will be greeted by the Main Menu where you can choose to Edit, Train, or Import PGNs.

### Edit Mode (Building your Repertoire)
In this mode, you can explore lines with Stockfish/Lichess and save the moves you want to learn.
* **[Click]** on pieces to make moves on the board.
* **[S]** - **Save Move:** Adds the last played move to your repertoire for the current position.
* **[R]** - **Reset Position:** Deletes all saved moves for the exact position currently on the board.
* **[Backspace]** or **[Left Arrow]** - **Undo:** Takes back the last move.
* **[Esc]** - Return to the main menu.

### Train Mode (Testing your Memory)
The board will flip to your chosen color's perspective. Make your planned moves, and the app will randomly play one of the saved opponent responses (weighted by human probability).
* **[Click]** to make your move.
* **[H]** - **Hint:** Shows the starting letter(s) of the correct move(s) if you get stuck.
* **[N]** - **New Line:** Resets the board to the starting position to practice another line.
* **[Esc]** - Return to the main menu.
* *Note:* If you play a move that isn't in your repertoire, the app will play an error sound and prompt you to try again.

### Importing PGNs
Clicking the "Import PGN" buttons on the main menu will open a file dialog. Select any `.pgn` file, and the program will automatically extract every branch and variation.