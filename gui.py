import pygame
import sys
import chess
import chess.engine
import chess.pgn
import json
import os
import random
import tkinter as tk
from tkinter import filedialog
import requests # NUOVA LIBRERIA PER INTERNET
import threading # NUOVA LIBRERIA PER NON BLOCCARE LA GRAFICA

# --- INITIALIZATION ---
pygame.init()
pygame.font.init()
pygame.mixer.init()

# --- CONSTANTS & SETTINGS ---
EVAL_BAR_WIDTH = 30
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
LAST_MOVE_COLOR = (255, 255, 0)

STOCKFISH_FILENAME = "stockfish-windows-x86-64-avx2.exe" 
REPERTOIRE_FILE = "repertoire.json"

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Chessbook Clone - Database Umano Integrato")

font_menu = pygame.font.SysFont("arial", 40, bold=True)
font_text = pygame.font.SysFont("arial", 20)
font_small = pygame.font.SysFont("arial", 16)

IMAGES = {}
SOUNDS = {}
repertoires = {"White": {}, "Black": {}}

# --- LICHESS DATABASE CACHE ---
lichess_cache = {}

def leggi_token():
    """Legge il token da file. Se non c'è, restituisce None."""
    try:
        if os.path.exists("token.txt"):
            with open("token.txt", "r") as f:
                return f.read().strip()
    except:
        pass
    return None

def fetch_lichess_async(fen):
    """Scarica le statistiche umane da Lichess in background."""
    mio_token = leggi_token()
    
    # Se l'utente non ha messo il file token.txt, avvisiamolo elegantemente
    if not mio_token:
        lichess_cache[fen] = ["Manca token.txt", "Crea token su Lichess", "e salvalo nel file!"]
        return

    try:
        url = "https://explorer.lichess.ovh/lichess"
        parametri = {
            'fen': fen,
            'speeds': 'blitz,rapid,classical',
            'moves': 4
        }
        
        headers = {
            'User-Agent': 'ChessbookClone/1.0',
            'Authorization': f'Bearer {mio_token}' 
        }
        
        resp = requests.get(url, headers=headers, params=parametri, timeout=5)
        resp.raise_for_status() 
        
        dati = resp.json()
        
        totale_partite = dati.get('white', 0) + dati.get('draws', 0) + dati.get('black', 0)
        mosse_info = []
        
        if totale_partite > 0:
            for m in dati.get('moves', []):
                m_totale = m['white'] + m['draws'] + m['black']
                pct = (m_totale / totale_partite) * 100
                mosse_info.append((m['san'], m_totale, pct))
                
        lichess_cache[fen] = mosse_info if mosse_info else ["Nessun dato qui."]
        
    except Exception as e:
        print(f"Errore Lichess API: {e}")
        lichess_cache[fen] = ["Database offline"]

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
    
    sound_files = {'move': 'move.mp3', 'capture': 'capture.mp3', 'error': 'error.mp3'}
    for name, file in sound_files.items():
        try:
            SOUNDS[name] = pygame.mixer.Sound(f"sounds/{file}")
        except:
            SOUNDS[name] = None

def play_sound(sound_type):
    if SOUNDS.get(sound_type): SOUNDS[sound_type].play()

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
    root = tk.Tk()
    root.withdraw()
    filepath = filedialog.askopenfilename(title=f"Import PGN for {chosen_color}", filetypes=[("PGN Files", "*.pgn")])
    if not filepath: return "Import cancelled."
        
    try:
        count = [0]
        def explore_tree(node, board):
            for child in node.variations:
                move = child.move
                fen = board.fen()
                san_move = board.san(move)
                
                if fen not in repertoires[chosen_color]:
                    repertoires[chosen_color][fen] = []
                if san_move not in repertoires[chosen_color][fen]:
                    repertoires[chosen_color][fen].append(san_move)
                    count[0] += 1
                        
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
        return f"Imported {count[0]} moves!"
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
    score_cp = max(-1000, min(1000, score_cp))
    white_percentage = (score_cp + 1000) / 2000.0 
    if not white_orientation:
        white_percentage = 1.0 - white_percentage 
    white_height = int(HEIGHT * white_percentage)
    black_height = HEIGHT - white_height
    pygame.draw.rect(screen, (50, 50, 50), pygame.Rect(0, 0, EVAL_BAR_WIDTH, black_height))
    pygame.draw.rect(screen, (220, 220, 220), pygame.Rect(0, black_height, EVAL_BAR_WIDTH, white_height))

def draw_board():
    for row in range(8):
        for col in range(8):
            color = LIGHT_COLOR if (row + col) % 2 == 0 else DARK_COLOR
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
        # Impaginazione mosse salvate
        saved_color = (100, 255, 100) if saved_moves else (200, 200, 200)
        full_text = "Saved: " + ", ".join(saved_moves) if saved_moves else "Saved: None"
        words = full_text.split(" ")
        lines, current_line = [], ""
        max_width = PANEL_WIDTH - 40 
        
        for word in words:
            test_line = current_line + word + " "
            if font_text.size(test_line)[0] <= max_width:
                current_line = test_line
            else:
                lines.append(current_line)
                current_line = word + " "
        if current_line: lines.append(current_line)
            
        offset_y = 60
        for line in lines:
            surf = font_text.render(line.strip(), True, saved_color)
            screen.blit(surf, (EVAL_BAR_WIDTH + BOARD_WIDTH + 20, offset_y))
            offset_y += 25
        
        # Disegno Stockfish
        stockfish_offset = max(110, offset_y + 15) 
        sf_title = font_text.render("Stockfish Analysis:", True, (150, 200, 255))
        screen.blit(sf_title, (EVAL_BAR_WIDTH + BOARD_WIDTH + 20, stockfish_offset))
        for i, line in enumerate(top_moves_text):
            move_text = font_small.render(line, True, TEXT_COLOR)
            screen.blit(move_text, (EVAL_BAR_WIDTH + BOARD_WIDTH + 20, stockfish_offset + 30 + (i * 20)))

        # NUOVO: Disegno Lichess Database (sotto Stockfish)
        lichess_offset = stockfish_offset + 105
        db_title = font_text.render("Lichess DB (Humans):", True, (255, 180, 100))
        screen.blit(db_title, (EVAL_BAR_WIDTH + BOARD_WIDTH + 20, lichess_offset))
        
        db_data = lichess_cache.get(fen, ["Caricamento..."])
        for i, item in enumerate(db_data[:4]): # Mostriamo max 4 mosse
            if isinstance(item, tuple): # Se è un dato formattato
                san, count, pct = item
                testo = f"{i+1}. {san}  ({pct:.1f}%)"
            else:
                testo = item # Messaggio d'errore o caricamento
            db_text = font_small.render(testo, True, TEXT_COLOR)
            screen.blit(db_text, (EVAL_BAR_WIDTH + BOARD_WIDTH + 20, lichess_offset + 30 + (i * 20)))

        instructions = ["[Click] Move", "[S] Save", "[R] Reset here", "[Bksp] Undo", "[Esc] Menu"]
    else:
        info_text = font_text.render("Guess the move!", True, (150, 255, 150))
        screen.blit(info_text, (EVAL_BAR_WIDTH + BOARD_WIDTH + 20, 120))
        instructions = ["[Click] Make move", "[H] Hint", "[N] New Line", "[Esc] Menu"]

    pygame.draw.line(screen, (100, 100, 100), (EVAL_BAR_WIDTH + BOARD_WIDTH + 20, 480), (WIDTH - 20, 480))
    for i, line in enumerate(instructions):
        text = font_small.render(line, True, (180, 180, 180))
        screen.blit(text, (EVAL_BAR_WIDTH + BOARD_WIDTH + 20, 495 + (i * 22)))
        
    if system_msg:
        msg_render = font_text.render(system_msg, True, (255, 100, 100))
        screen.blit(msg_render, (EVAL_BAR_WIDTH + BOARD_WIDTH + 20, HEIGHT - 40))

def get_square_from_mouse(x, y, white_orientation):
    board_x = x - EVAL_BAR_WIDTH
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
    eval_cp = 0 
    
    while running:
        fen = board.fen()
        # Richiesta asincrona del DB Lichess per la posizione attuale
        if current_state in ["EDIT", "TRAIN"] and fen not in lichess_cache:
            lichess_cache[fen] = ["Caricamento db..."] # <--- RIGA MAGICA ANTI-SPAM!
            threading.Thread(target=fetch_lichess_async, args=(fen,), daemon=True).start()

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
                    # --- LOGICA DI ALLENAMENTO PONDERATA (Probabilità Lichess) ---
                    db_data = lichess_cache.get(fen, [])
                    weights = []
                    
                    if isinstance(db_data, list) and len(db_data) > 0 and isinstance(db_data[0], tuple):
                        # Costruiamo un dizionario "Mossa: Numero di giocate"
                        counts_dict = {san: count for san, count, pct in db_data}
                        for v_m in valid_moves:
                            san_vm = board.san(v_m)
                            # Se la mossa non è nel top db ma è valida, le diamo peso minimo 1
                            weights.append(counts_dict.get(san_vm, 1)) 
                            
                        # Estraiamo a caso ma tenendo conto dei pesi!
                        chosen_move = random.choices(valid_moves, weights=weights, k=1)[0]
                    else:
                        # Fallback se non c'è internet o il db non è ancora pronto
                        chosen_move = random.choice(valid_moves)
                    # -----------------------------------------------------------

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
                        if fen in repertoires[chosen_color]:
                            del repertoires[chosen_color][fen]
                            save_repertoire()
                            system_msg = "All moves reset."
                            
                    elif event.key == pygame.K_h and current_state == "TRAIN":
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
            
            if infos and "score" in infos[0]:
                sc = infos[0]["score"].white()
                if sc.is_mate():
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