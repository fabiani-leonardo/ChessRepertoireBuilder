# ChessRepertoireBuilder ♟️

A Python/Pygame application to build and train your personal chess repertoire.

## Installation
1. Clone this repository.
2. Create a virtual environment and install the required dependencies: `pip install pygame-ce chess`
3. **PLEASE NOTE:** This program requires the Stockfish engine to work.
   - Download Stockfish (AVX2 version recommended for modern Windows) from [stockfishchess.org](https://stockfishchess.org/download/)
   - Extract the `.exe` file and place it in the root folder of the project.
   - Make sure the name of the extracted file matches the `STOCKFISH_FILENAME` variable inside `gui.py` (default is `stockfish-windows-x86-64-avx2.exe`).
4. Ensure you have the `images/` and `sounds/` folders populated with the required piece images and audio files in the project root.
5. Run the program with `python gui.py`

## ✨ Features
* **Dual Repertoire Management:** Build and manage separate opening repertoires for White and Black.
* **Live Stockfish Analysis:** Integrated Stockfish engine provides real-time evaluations, top 3 engine lines, and a dynamic evaluation bar to help you find the best moves.
* **Interactive Training Mode:** Test your memory by playing against your saved lines. The computer will automatically play the opponent's responses based on your repertoire.
* **Bulk PGN Import:** Easily import existing PGN files. The app parses the entire PGN tree (including all sub-variations) and merges them into your JSON repertoire file.
* **Visual & Audio Feedback:** Features highlighted squares for previous moves, move/capture sound effects, and error buzzers to keep you focused during training.
* **Auto-Saving:** All your moves are continuously saved to a local `repertoire.json` file so you never lose your prep.

## 🎮 How to Use

When you launch the app, you will be greeted by the Main Menu where you can choose to Edit, Train, or Import PGNs for either color.

### Edit Mode (Building your Repertoire)
In this mode, you can explore lines with Stockfish and save the moves you want to learn.
* **[Click]** on pieces to make moves on the board.
* **[S]** - **Save Move:** Adds the last played move to your repertoire for the current position.
* **[R]** - **Reset Position:** Deletes all saved moves for the exact position currently on the board.
* **[Backspace]** or **[Left Arrow]** - **Undo:** Takes back the last move.
* **[Esc]** - Return to the main menu.

### Train Mode (Testing your Memory)
In this mode, the board will flip to your chosen color's perspective. Make your planned moves, and the app will randomly play one of the saved opponent responses.
* **[Click]** to make your move.
* **[H]** - **Hint:** Shows the starting square of the correct move(s) if you get stuck.
* **[Esc]** - Return to the main menu.
* *Note:* If you play a move that isn't in your repertoire, the app will play an error sound and prompt you to try again.

### Importing PGNs
Clicking the "Import PGN" buttons on the main menu will open a file dialog. Select any `.pgn` file, and the program will automatically extract every branch and variation, converting them into your repertoire format.