import pygame
import sys
import chess
import chess.engine
import chess.pgn # Library to read PGN files
import json
import os
import random
import tkinter as tk
from tkinter import filedialog

# --- INITIALIZATION ---
pygame.init()
pygame.font.init()
pygame.mixer.init() # Initialize audio

# --- CONSTANTS & SETTINGS ---
EVAL_BAR_WIDTH = 30 # Space for the evaluation bar
BOARD_WIDTH = 640
PANEL_WIDTH = 300
WIDTH = EVAL_BAR_WIDTH + BOARD_WIDTH + PANEL_WIDTH
HEIGHT = 640
SQUARE_SIZE = BOARD_WIDTH // 8

LIGHT_COLOR = (240, 217, 181)
DARK_COLOR = (181, 136, 99)
BG_COLOR = (40, 40, 40)
PANEL_COLOR = (30, 30, 30)
TEXT_COLOR = (255, 255, 255)
HIGHLIGHT_COLOR = (0, 255, 0)
LAST_MOVE_COLOR = (255, 255, 0) # Yellow

STOCKFISH_FILENAME = "stockfish-windows-x86-64-avx2.exe" 
REPERTOIRE_FILE = "repertoire.json"

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Chessbook Clone - Ultimate Edition")

font_menu = pygame.font.SysFont("arial", 40, bold=True)
font_text = pygame.font.SysFont("arial", 20)
font_small = pygame.font.SysFont("arial", 16)

IMAGES = {}
SOUNDS = {}
repertoires = {"White": {}, "Black": {}}

# --- LOADING FUNCTIONS ---
def load_assets():
    pieces = {
        'P': 'wP', 'N': 'wN', 'B': 'wB', 'R': 'wR', 'Q': 'wQ', 'K': 'wK',
        'p': 'bP', 'n': 'bN', 'b': 'bB', 'r': 'bR', 'q': 'bQ', 'k': 'bK'
    }
    for symbol, file_name in pieces.items():
        try:
            img = pygame.image.load(f"images/{file_name}.png")
            IMAGES[symbol] = pygame.transform.scale(img, (SQUARE_SIZE, SQUARE_SIZE))
        except: pass
    
    # Safe sound loading
    sound_files = {'move': 'move.wav', 'capture': 'capture.mp3', 'error': 'error.mp3'}
    for name, file in sound_files.items():
        try:
            SOUNDS[name] = pygame.mixer.Sound(f"sounds/{file}")
        except:
            SOUNDS[name] = None # Fallback if files are missing

def play_sound(sound_type):
    if SOUNDS.get(sound_type):
        SOUNDS[sound_type].play()

def load_repertoire():
    global repertoires
    if os.path.exists(REPERTOIRE_FILE):
        with open(REPERTOIRE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            for color in data:
                for fen, moves in data[color].items():
                    if isinstance(moves, str): data[color][fen] = [moves]
            repertoires = data

def save_repertoire():
    with open(REPERTOIRE_FILE, "w", encoding="utf-8") as f:
        json.dump(repertoires, f, indent=4)

def import_pgn(chosen_color):
    """Opens a Windows dialog and converts a PGN into our JSON, exploring ALL variations."""
    root = tk.Tk()
    root.withdraw()
    filepath = filedialog.askopenfilename(title=f"Import PGN for {chosen_color}", filetypes=[("PGN Files", "*.pgn")])
    
    if not filepath:
        return "Import cancelled."
        
    try:
        count = [0]
        
        def explore_tree(node, board):
            for child in node.variations:
                move = child.move
                fen = board.fen()
                san_move = board.san(move)
                
                # TURN CHECK REMOVED!
                # We save every single branch of the PGN tree to maintain continuity
                if fen not in repertoires[chosen_color]:
                    repertoires[chosen_color][fen] = []
                if san_move not in repertoires[chosen_color][fen]:
                    repertoires[chosen_color][fen].append(san_move)
                    count[0] += 1
                        
                # Navigate deep
                board.push(move)
                explore_tree(child, board)
                board.pop()

        with open(filepath, "r", encoding="utf-8") as pgn_file:
            while True:
                game = chess.pgn.read_game(pgn_file)
                if game is None: break
                
                board = game.board()
                explore_tree(game, board)
                
        save_repertoire()
        return f"Imported {count[0]} moves (including opponents)!"
    except Exception as e:
        return f"Error reading PGN: {e}"

# --- GRAPHICAL FUNCTIONS ---
def draw_menu():
    screen.fill(BG_COLOR)
    title = font_menu.render("CHESSBOOK CLONE", True, TEXT_COLOR)
    screen.blit(title, (WIDTH//2 - title.get_width()//2, 30))

    rects = {
        "MOD_W": pygame.Rect(WIDTH//2 - 200, 100, 400, 50),
        "MOD_B": pygame.Rect(WIDTH//2 - 200, 170, 400, 50),
        "TRAIN_W": pygame.Rect(WIDTH//2 - 200, 250, 400, 50),
        "TRAIN_B": pygame.Rect(WIDTH//2 - 200, 320, 400, 50),
        "PGN_W": pygame.Rect(WIDTH//2 - 200, 420, 190, 40),
        "PGN_B": pygame.Rect(WIDTH//2 + 10, 420, 190, 40)
    }
    
    pygame.draw.rect(screen, (70, 130, 180), rects["MOD_W"], border_radius=10)
    pygame.draw.rect(screen, (50, 100, 150), rects["MOD_B"], border_radius=10)
    pygame.draw.rect(screen, (46, 139, 87), rects["TRAIN_W"], border_radius=10)
    pygame.draw.rect(screen, (34, 100, 60), rects["TRAIN_B"], border_radius=10)
    pygame.draw.rect(screen, (100, 100, 100), rects["PGN_W"], border_radius=5)
    pygame.draw.rect(screen, (80, 80, 80), rects["PGN_B"], border_radius=5)
    
    texts = {
        "MOD_W": "1. Edit Repertoire - WHITE", "MOD_B": "2. Edit Repertoire - BLACK",
        "TRAIN_W": "3. Train - WHITE", "TRAIN_B": "4. Train - BLACK",
        "PGN_W": "Import PGN (White)", "PGN_B": "Import PGN (Black)"
    }
    
    for key, rect in rects.items():
        font_to_use = font_small if "PGN" in key else font_text
        t = font_to_use.render(texts[key], True, TEXT_COLOR)
        screen.blit(t, (rect.centerx - t.get_width()//2, rect.centery - t.get_height()//2))
        
    return rects

def draw_eval_bar(score_cp, white_orientation):
    # score_cp is in centipawns from WHITE's perspective.
    # Cap at +1000 and -1000 centipawns (10 pawns advantage) to prevent overflowing
    score_cp = max(-1000, min(1000, score_cp))
    
    # 0 = equal (mid screen). +1000 = all white (y=0). -1000 = all black (y=HEIGHT)
    white_percentage = (score_cp + 1000) / 2000.0 
    
    if not white_orientation:
        white_percentage = 1.0 - white_percentage # Flip bar if playing black!
        
    white_height = int(HEIGHT * white_percentage)
    black_height = HEIGHT - white_height
    
    # Draw black part at the top and white at the bottom (or vice versa based on orientation)
    pygame.draw.rect(screen, (50, 50, 50), pygame.Rect(0, 0, EVAL_BAR_WIDTH, black_height))
    pygame.draw.rect(screen, (220, 220, 220), pygame.Rect(0, black_height, EVAL_BAR_WIDTH, white_height))

def draw_board():
    for row in range(8):
        for col in range(8):
            color = LIGHT_COLOR if (row + col) % 2 == 0 else DARK_COLOR
            # Add EVAL_BAR_WIDTH to the X coordinate
            pygame.draw.rect(screen, color, pygame.Rect(EVAL_BAR_WIDTH + col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

def draw_pieces(board, white_orientation=True):
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece:
            col = chess.square_file(square)
            row = chess.square_rank(square)
            x = col if white_orientation else 7 - col
            y = 7 - row if white_orientation else row
            screen.blit(IMAGES[piece.symbol()], pygame.Rect(EVAL_BAR_WIDTH + x * SQUARE_SIZE, y * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

def draw_highlights(board, selected_square, white_orientation=True):
    # 1. Highlight the last played move (Transparent yellow)
    if len(board.move_stack) > 0:
        last_move = board.peek()
        for square in [last_move.from_square, last_move.to_square]:
            col = chess.square_file(square)
            row = chess.square_rank(square)
            x = col if white_orientation else 7 - col
            y = 7 - row if white_orientation else row
            s = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE))
            s.set_alpha(80)
            s.fill(LAST_MOVE_COLOR)
            screen.blit(s, (EVAL_BAR_WIDTH + x * SQUARE_SIZE, y * SQUARE_SIZE))
            
    # 2. Highlight the mouse-selected square (Green)
    if selected_square is not None:
        col = chess.square_file(selected_square)
        row = chess.square_rank(selected_square)
        x = col if white_orientation else 7 - col
        y = 7 - row if white_orientation else row
        s = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE))
        s.set_alpha(100)
        s.fill(HIGHLIGHT_COLOR)
        screen.blit(s, (EVAL_BAR_WIDTH + x * SQUARE_SIZE, y * SQUARE_SIZE))

def draw_panel(state, board, chosen_color, top_moves_text, system_msg):
    panel_rect = pygame.Rect(EVAL_BAR_WIDTH + BOARD_WIDTH, 0, PANEL_WIDTH, HEIGHT)
    pygame.draw.rect(screen, PANEL_COLOR, panel_rect)
    
    title = font_text.render(f"Mode: {state} ({chosen_color})", True, (255, 215, 0))
    screen.blit(title, (EVAL_BAR_WIDTH + BOARD_WIDTH + 20, 20))
    
    fen = board.fen()
    saved_moves = repertoires[chosen_color].get(fen, [])
    
    if state == "EDIT":
        # --- MULTILINE LOGIC FOR WORD WRAPPING ---
        saved_color = (100, 255, 100) if saved_moves else (200, 200, 200)
        full_text = "Saved: " + ", ".join(saved_moves) if saved_moves else "Saved: None"
            
        words = full_text.split(" ")
        lines = []
        current_line = ""
        max_width = PANEL_WIDTH - 40 # 20px margin per side
        
        for word in words:
            test_line = current_line + word + " "
            # If the test line fits the space, keep it
            if font_text.size(test_line)[0] <= max_width:
                current_line = test_line
            else:
                # Otherwise save the line and break to next line
                lines.append(current_line)
                current_line = word + " "
        if current_line:
            lines.append(current_line)
            
        offset_y = 60 # Starting Y coordinate
        for line in lines:
            surf = font_text.render(line.strip(), True, saved_color)
            screen.blit(surf, (EVAL_BAR_WIDTH + BOARD_WIDTH + 20, offset_y))
            offset_y += 25 # Drop 25 pixels for the next line
        
        # --- END MULTILINE LOGIC ---

        # Move Stockfish down based on the space occupied by saved moves
        stockfish_offset = max(120, offset_y + 20) 
        
        sf_title = font_text.render("Stockfish Analysis:", True, (150, 200, 255))
        screen.blit(sf_title, (EVAL_BAR_WIDTH + BOARD_WIDTH + 20, stockfish_offset))
        for i, line in enumerate(top_moves_text):
            move_text = font_small.render(line, True, TEXT_COLOR)
            screen.blit(move_text, (EVAL_BAR_WIDTH + BOARD_WIDTH + 20, stockfish_offset + 35 + (i * 25)))
            
        instructions = ["[Click] Move", "[S] Save move", "[R] Reset moves here", "[Backspace] Undo", "[Esc] Menu"]
    else:
        info_text = font_text.render("Guess the move!", True, (150, 255, 150))
        screen.blit(info_text, (EVAL_BAR_WIDTH + BOARD_WIDTH + 20, 120))
        instructions = ["[Click] Make move", "[H] Hint", "[N] New Line", "[Esc] Menu"]
    

    pygame.draw.line(screen, (100, 100, 100), (EVAL_BAR_WIDTH + BOARD_WIDTH + 20, 450), (WIDTH - 20, 450))
    for i, line in enumerate(instructions):
        text = font_small.render(line, True, (180, 180, 180))
        screen.blit(text, (EVAL_BAR_WIDTH + BOARD_WIDTH + 20, 470 + (i * 25)))
        
    if system_msg:
        msg_render = font_text.render(system_msg, True, (255, 100, 100))
        screen.blit(msg_render, (EVAL_BAR_WIDTH + BOARD_WIDTH + 20, HEIGHT - 50))

def get_square_from_mouse(x, y, white_orientation):
    board_x = x - EVAL_BAR_WIDTH # Subtract bar offset
    if board_x < 0 or board_x >= BOARD_WIDTH: return None
    col = board_x // SQUARE_SIZE
    row = y // SQUARE_SIZE
    return chess.square(col if white_orientation else 7 - col, 7 - row if white_orientation else row)

# --- MAIN LOOP ---
def main():
    load_assets()
    load_repertoire()
    board = chess.Board()
    
    try:
        engine = chess.engine.SimpleEngine.popen_uci(STOCKFISH_FILENAME)
        engine.configure({"Threads": 1, "Hash": 16})
    except Exception as e:
        print(f"Stockfish Error: {e}")
        sys.exit()
    
    clock = pygame.time.Clock()
    running = True
    
    current_state = "MENU"
    chosen_color = "White"
    selected_square = None
    last_analyzed_fen = ""
    top_moves_text = ["Calculating..."]
    system_msg = ""
    eval_cp = 0 # Global variable for bar height
    
    while running:
        if current_state == "TRAIN":
            current_turn = "White" if board.turn == chess.WHITE else "Black"
            if current_turn != chosen_color:
                pygame.time.wait(400)
                valid_moves = []
                for move in board.legal_moves:
                    board.push(move)
                    if board.fen() in repertoires[chosen_color]:
                        valid_moves.append(move)
                    board.pop()
                
                if valid_moves:
                    chosen_move = random.choice(valid_moves)
                    is_capture = board.is_capture(chosen_move)
                    board.push(chosen_move)
                    play_sound("capture" if is_capture else "move")
                    system_msg = "Your turn!"
                else:
                    system_msg = "End of line reached!"

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                
            elif event.type == pygame.KEYDOWN:
                if current_state in ["EDIT", "TRAIN"]:
                    if event.key == pygame.K_ESCAPE:
                        current_state = "MENU"
                        system_msg = ""
                        
                    elif event.key in [pygame.K_LEFT, pygame.K_BACKSPACE] and current_state == "EDIT":
                        if len(board.move_stack) > 0:
                            board.pop()
                            system_msg = "Move undone."
                            selected_square = None
                            
                    elif event.key == pygame.K_s and current_state == "EDIT":
                        if len(board.move_stack) > 0:
                            last_move = board.pop()
                            previous_fen = board.fen()
                            san_move = board.san(last_move)
                            
                            if previous_fen not in repertoires[chosen_color]:
                                repertoires[chosen_color][previous_fen] = []
                            if san_move not in repertoires[chosen_color][previous_fen]:
                                repertoires[chosen_color][previous_fen].append(san_move)
                                system_msg = f"Added: {san_move}!"
                            else:
                                system_msg = f"{san_move} already saved!"
                                
                            save_repertoire()
                            board.push(last_move)
                            
                    elif event.key == pygame.K_r and current_state == "EDIT":
                        fen = board.fen()
                        if fen in repertoires[chosen_color]:
                            del repertoires[chosen_color][fen]
                            save_repertoire()
                            system_msg = "All moves reset."
                            
                    elif event.key == pygame.K_h and current_state == "TRAIN":
                        fen = board.fen()
                        current_moves = repertoires[chosen_color].get(fen, [])
                        if current_moves:
                            initials = ", ".join(list(set(m[0] for m in current_moves)))
                            system_msg = f"Starts with: {initials}"
                        else:
                            system_msg = "No moves saved here."
                    elif event.key == pygame.K_n and current_state == "TRAIN":
                        board.reset()
                        selected_square = None
                        system_msg = "New line started!"
                            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    x, y = event.pos
                    
                    if current_state == "MENU":
                        rects = draw_menu()
                        if rects["MOD_W"].collidepoint(x, y):
                            chosen_color, current_state, board, system_msg = "White", "EDIT", chess.Board(), ""
                        elif rects["MOD_B"].collidepoint(x, y):
                            chosen_color, current_state, board, system_msg = "Black", "EDIT", chess.Board(), ""
                        elif rects["TRAIN_W"].collidepoint(x, y):
                            chosen_color, current_state, board, system_msg = "White", "TRAIN", chess.Board(), ""
                        elif rects["TRAIN_B"].collidepoint(x, y):
                            chosen_color, current_state, board, system_msg = "Black", "TRAIN", chess.Board(), ""
                        elif rects["PGN_W"].collidepoint(x, y):
                            system_msg = import_pgn("White")
                        elif rects["PGN_B"].collidepoint(x, y):
                            system_msg = import_pgn("Black")
                            
                    elif current_state in ["EDIT", "TRAIN"]:
                        current_turn = "White" if board.turn == chess.WHITE else "Black"
                        if current_state == "TRAIN" and current_turn != chosen_color:
                            continue

                        white_orientation = (chosen_color == "White")
                        clicked_square = get_square_from_mouse(x, y, white_orientation)
                        
                        if clicked_square is not None:
                            clicked_piece = board.piece_at(clicked_square)
                            
                            if selected_square is None:
                                if clicked_piece and clicked_piece.color == board.turn:
                                    selected_square = clicked_square
                            else:
                                if clicked_piece and clicked_piece.color == board.turn:
                                    selected_square = clicked_square
                                else:
                                    move = chess.Move(selected_square, clicked_square)
                                    piece_to_move = board.piece_at(selected_square)
                                    if piece_to_move and piece_to_move.piece_type == chess.PAWN:
                                        if chess.square_rank(clicked_square) in [0, 7]:
                                            move = chess.Move(selected_square, clicked_square, promotion=chess.QUEEN)
                                    
                                    if move in board.legal_moves:
                                        is_capture = board.is_capture(move)
                                        if current_state == "EDIT":
                                            board.push(move)
                                            play_sound("capture" if is_capture else "move")
                                            system_msg = ""
                                        elif current_state == "TRAIN":
                                            fen = board.fen()
                                            current_moves = repertoires[chosen_color].get(fen, [])
                                            if board.san(move) in current_moves:
                                                board.push(move)
                                                play_sound("capture" if is_capture else "move")
                                                system_msg = "Correct!"
                                            else:
                                                play_sound("error")
                                                system_msg = "Incorrect, try again."
                                        selected_square = None
                                    else:
                                        selected_square = None

        if current_state in ["EDIT", "TRAIN"] and board.fen() != last_analyzed_fen:
            last_analyzed_fen = board.fen()
            top_moves_text = ["Calculating..."]
            
            infos = engine.analyse(board, chess.engine.Limit(time=0.2), multipv=3)
            top_moves_text = []
            
            # Extract evaluation for the bar drawing
            if infos and "score" in infos[0]:
                sc = infos[0]["score"].white()
                if sc.is_mate():
                    # If it's a mate, give the bar a very high value
                    eval_cp = 10000 if sc.mate() > 0 else -10000
                else:
                    eval_cp = sc.score()
            
            for i, info in enumerate(infos):
                if "score" in info and "pv" in info:
                    sc = info["score"].white()
                    val = f"M{sc.mate()}" if sc.is_mate() else f"{sc.score()/100.0:+.2f}"
                    top_moves_text.append(f"{i+1}. {board.san(info['pv'][0])}  [{val}]")

        if current_state == "MENU":
            draw_menu()
            if system_msg:
                # Show in the menu how many PGNs were imported
                msg_render = font_text.render(system_msg, True, (255, 255, 100))
                screen.blit(msg_render, (WIDTH//2 - msg_render.get_width()//2, HEIGHT - 50))
        else:
            white_orientation = (chosen_color == "White")
            draw_eval_bar(eval_cp, white_orientation)
            draw_board()
            draw_highlights(board, selected_square, white_orientation)
            draw_pieces(board, white_orientation)
            draw_panel(current_state, board, chosen_color, top_moves_text, system_msg)
            
        pygame.display.flip()
        clock.tick(60)

    engine.quit()
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()