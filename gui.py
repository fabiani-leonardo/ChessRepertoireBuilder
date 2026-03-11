import pygame
import sys
import chess
import chess.engine
import chess.pgn # Nuova libreria per leggere i file PGN
import json
import os
import random
import tkinter as tk
from tkinter import filedialog

# --- INIZIALIZZAZIONE ---
pygame.init()
pygame.font.init()
pygame.mixer.init() # Inizializziamo l'audio

# --- COSTANTI & IMPOSTAZIONI ---
LARGHEZZA_BARRA = 30 # Spazio per la barra di valutazione
LARGHEZZA_SCACCHIERA = 640
LARGHEZZA_PANNELLO = 300
WIDTH = LARGHEZZA_BARRA + LARGHEZZA_SCACCHIERA + LARGHEZZA_PANNELLO
HEIGHT = 640
DIM_CASA = LARGHEZZA_SCACCHIERA // 8

COLORE_CHIARO = (240, 217, 181)
COLORE_SCURO = (181, 136, 99)
COLORE_SFONDO = (40, 40, 40)
COLORE_PANNELLO = (30, 30, 30)
COLORE_TESTO = (255, 255, 255)
COLORE_EVIDENZIA = (0, 255, 0)
COLORE_ULTIMA_MOSSA = (255, 255, 0) # Giallo

NOME_FILE_STOCKFISH = "stockfish-windows-x86-64-avx2.exe" 
FILE_REPERTORIO = "repertorio.json"

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Chessbook Clone - Ultimate Edition")

font_menu = pygame.font.SysFont("arial", 40, bold=True)
font_testo = pygame.font.SysFont("arial", 20)
font_piccolo = pygame.font.SysFont("arial", 16)

IMAGES = {}
SUONI = {}
repertori = {"Bianco": {}, "Nero": {}}

# --- FUNZIONI DI CARICAMENTO ---
def carica_asset():
    pezzi = {
        'P': 'wP', 'N': 'wN', 'B': 'wB', 'R': 'wR', 'Q': 'wQ', 'K': 'wK',
        'p': 'bP', 'n': 'bN', 'b': 'bB', 'r': 'bR', 'q': 'bQ', 'k': 'bK'
    }
    for simbolo, nome_file in pezzi.items():
        try:
            img = pygame.image.load(f"images/{nome_file}.png")
            IMAGES[simbolo] = pygame.transform.scale(img, (DIM_CASA, DIM_CASA))
        except: pass
    
    # Caricamento suoni sicuri
    file_suoni = {'muovi': 'move.wav', 'cattura': 'capture.mp3', 'errore': 'error.mp3'}
    for nome, file in file_suoni.items():
        try:
            SUONI[nome] = pygame.mixer.Sound(f"sounds/{file}")
        except:
            SUONI[nome] = None # Fallback se non ci sono i file

def riproduci_suono(tipo):
    if SUONI.get(tipo):
        SUONI[tipo].play()

def carica_repertorio():
    global repertori
    if os.path.exists(FILE_REPERTORIO):
        with open(FILE_REPERTORIO, "r", encoding="utf-8") as f:
            dati = json.load(f)
            for colore in dati:
                for fen, mosse in dati[colore].items():
                    if isinstance(mosse, str): dati[colore][fen] = [mosse]
            repertori = dati

def salva_repertorio():
    with open(FILE_REPERTORIO, "w", encoding="utf-8") as f:
        json.dump(repertori, f, indent=4)

def importa_pgn(colore_scelto):
    """Apre una finestra Windows e converte un PGN nel nostro JSON, esplorando TUTTE le varianti."""
    root = tk.Tk()
    root.withdraw()
    filepath = filedialog.askopenfilename(title=f"Importa PGN per {colore_scelto}", filetypes=[("File PGN", "*.pgn")])
    
    if not filepath:
        return "Importazione annullata."
        
    try:
        conteggio = [0]
        
        def esplora_albero(nodo, board):
            for figlio in nodo.variations:
                mossa = figlio.move
                fen = board.fen()
                mossa_san = board.san(mossa)
                
                # RIMOSSO IL CONTROLLO SUL TURNO! 
                # Salviamo ogni singolo ramo dell'albero PGN per avere continuità
                if fen not in repertori[colore_scelto]:
                    repertori[colore_scelto][fen] = []
                if mossa_san not in repertori[colore_scelto][fen]:
                    repertori[colore_scelto][fen].append(mossa_san)
                    conteggio[0] += 1
                        
                # Navighiamo in profondità
                board.push(mossa)
                esplora_albero(figlio, board)
                board.pop()

        with open(filepath, "r", encoding="utf-8") as pgn_file:
            while True:
                game = chess.pgn.read_game(pgn_file)
                if game is None: break
                
                board = game.board()
                esplora_albero(game, board)
                
        salva_repertorio()
        return f"Importate {conteggio[0]} mosse (inclusi gli avversari)!"
    except Exception as e:
        return f"Errore lettura PGN: {e}"

# --- FUNZIONI GRAFICHE ---
def disegna_menu():
    screen.fill(COLORE_SFONDO)
    titolo = font_menu.render("CHESSBOOK CLONE", True, COLORE_TESTO)
    screen.blit(titolo, (WIDTH//2 - titolo.get_width()//2, 30))

    rects = {
        "MOD_B": pygame.Rect(WIDTH//2 - 200, 100, 400, 50),
        "MOD_N": pygame.Rect(WIDTH//2 - 200, 170, 400, 50),
        "ALL_B": pygame.Rect(WIDTH//2 - 200, 250, 400, 50),
        "ALL_N": pygame.Rect(WIDTH//2 - 200, 320, 400, 50),
        "PGN_B": pygame.Rect(WIDTH//2 - 200, 420, 190, 40),
        "PGN_N": pygame.Rect(WIDTH//2 + 10, 420, 190, 40)
    }
    
    pygame.draw.rect(screen, (70, 130, 180), rects["MOD_B"], border_radius=10)
    pygame.draw.rect(screen, (50, 100, 150), rects["MOD_N"], border_radius=10)
    pygame.draw.rect(screen, (46, 139, 87), rects["ALL_B"], border_radius=10)
    pygame.draw.rect(screen, (34, 100, 60), rects["ALL_N"], border_radius=10)
    pygame.draw.rect(screen, (100, 100, 100), rects["PGN_B"], border_radius=5)
    pygame.draw.rect(screen, (80, 80, 80), rects["PGN_N"], border_radius=5)
    
    testi = {
        "MOD_B": "1. Modifica Repertorio - BIANCO", "MOD_N": "2. Modifica Repertorio - NERO",
        "ALL_B": "3. Allenati - BIANCO", "ALL_N": "4. Allenati - NERO",
        "PGN_B": "Importa PGN (Bianco)", "PGN_N": "Importa PGN (Nero)"
    }
    
    for chiave, rect in rects.items():
        font_da_usare = font_piccolo if "PGN" in chiave else font_testo
        t = font_da_usare.render(testi[chiave], True, COLORE_TESTO)
        screen.blit(t, (rect.centerx - t.get_width()//2, rect.centery - t.get_height()//2))
        
    return rects

def disegna_barra_valutazione(score_cp, orientamento_bianco):
    # score_cp è in centipawns dal punto di vista del BIANCO.
    # Cap a +1000 e -1000 centipawns (10 pedoni di vantaggio) per evitare che schizzi fuori
    score_cp = max(-1000, min(1000, score_cp))
    
    # 0 = pari (metà schermo). +1000 = tutto bianco (y=0). -1000 = tutto nero (y=HEIGHT)
    percentuale_bianco = (score_cp + 1000) / 2000.0 
    
    if not orientamento_bianco:
        percentuale_bianco = 1.0 - percentuale_bianco # Ribaltiamo la barra se giochiamo col nero!
        
    altezza_bianco = int(HEIGHT * percentuale_bianco)
    altezza_nero = HEIGHT - altezza_bianco
    
    # Disegniamo la parte nera in alto e bianca in basso (o viceversa in base all'orientamento)
    pygame.draw.rect(screen, (50, 50, 50), pygame.Rect(0, 0, LARGHEZZA_BARRA, altezza_nero))
    pygame.draw.rect(screen, (220, 220, 220), pygame.Rect(0, altezza_nero, LARGHEZZA_BARRA, altezza_bianco))

def disegna_scacchiera():
    for riga in range(8):
        for colonna in range(8):
            colore = COLORE_CHIARO if (riga + colonna) % 2 == 0 else COLORE_SCURO
            # Aggiungiamo LARGHEZZA_BARRA alla coordinata X
            pygame.draw.rect(screen, colore, pygame.Rect(LARGHEZZA_BARRA + colonna * DIM_CASA, riga * DIM_CASA, DIM_CASA, DIM_CASA))

def disegna_pezzi(board, orientamento_bianco=True):
    for square in chess.SQUARES:
        pezzo = board.piece_at(square)
        if pezzo:
            colonna = chess.square_file(square)
            riga = chess.square_rank(square)
            x = colonna if orientamento_bianco else 7 - colonna
            y = 7 - riga if orientamento_bianco else riga
            screen.blit(IMAGES[pezzo.symbol()], pygame.Rect(LARGHEZZA_BARRA + x * DIM_CASA, y * DIM_CASA, DIM_CASA, DIM_CASA))

def disegna_evidenziazioni(board, casa_selezionata, orientamento_bianco=True):
    # 1. Evidenzia l'ultima mossa giocata (Giallo trasparente)
    if len(board.move_stack) > 0:
        ultima_mossa = board.peek()
        for casa in [ultima_mossa.from_square, ultima_mossa.to_square]:
            colonna = chess.square_file(casa)
            riga = chess.square_rank(casa)
            x = colonna if orientamento_bianco else 7 - colonna
            y = 7 - riga if orientamento_bianco else riga
            s = pygame.Surface((DIM_CASA, DIM_CASA))
            s.set_alpha(80)
            s.fill(COLORE_ULTIMA_MOSSA)
            screen.blit(s, (LARGHEZZA_BARRA + x * DIM_CASA, y * DIM_CASA))
            
    # 2. Evidenzia la casa selezionata dal mouse (Verde)
    if casa_selezionata is not None:
        colonna = chess.square_file(casa_selezionata)
        riga = chess.square_rank(casa_selezionata)
        x = colonna if orientamento_bianco else 7 - colonna
        y = 7 - riga if orientamento_bianco else riga
        s = pygame.Surface((DIM_CASA, DIM_CASA))
        s.set_alpha(100)
        s.fill(COLORE_EVIDENZIA)
        screen.blit(s, (LARGHEZZA_BARRA + x * DIM_CASA, y * DIM_CASA))

def disegna_pannello(stato, board, colore_scelto, top_mosse_testo, msg_sistema):
    pannello_rect = pygame.Rect(LARGHEZZA_BARRA + LARGHEZZA_SCACCHIERA, 0, LARGHEZZA_PANNELLO, HEIGHT)
    pygame.draw.rect(screen, COLORE_PANNELLO, pannello_rect)
    
    titolo = font_testo.render(f"Modo: {stato} ({colore_scelto})", True, (255, 215, 0))
    screen.blit(titolo, (LARGHEZZA_BARRA + LARGHEZZA_SCACCHIERA + 20, 20))
    
    fen = board.fen()
    mosse_salvate = repertori[colore_scelto].get(fen, [])
    
    if stato == "MODIFICA":
        # --- LOGICA MULTILINEA PER L'ANDATA A CAPO ---
        colore_salvate = (100, 255, 100) if mosse_salvate else (200, 200, 200)
        testo_completo = "Salvate: " + ", ".join(mosse_salvate) if mosse_salvate else "Salvate: Nessuna"
            
        parole = testo_completo.split(" ")
        linee = []
        linea_corrente = ""
        max_larghezza = LARGHEZZA_PANNELLO - 40 # Margine di 20px per lato
        
        for parola in parole:
            prova = linea_corrente + parola + " "
            # Se la linea di prova ci sta nello spazio, la teniamo
            if font_testo.size(prova)[0] <= max_larghezza:
                linea_corrente = prova
            else:
                # Altrimenti salviamo la linea e andiamo a capo
                linee.append(linea_corrente)
                linea_corrente = parola + " "
        if linea_corrente:
            linee.append(linea_corrente)
            
        offset_y = 60 # Coordinata Y di partenza
        for linea in linee:
            surf = font_testo.render(linea.strip(), True, colore_salvate)
            screen.blit(surf, (LARGHEZZA_BARRA + LARGHEZZA_SCACCHIERA + 20, offset_y))
            offset_y += 25 # Scendiamo di 25 pixel per la riga successiva
        
        # --- FINE LOGICA MULTILINEA ---

        # Spostiamo Stockfish in basso in base allo spazio occupato dalle mosse salvate
        offset_stockfish = max(120, offset_y + 20) 
        
        sf_titolo = font_testo.render("Analisi Stockfish:", True, (150, 200, 255))
        screen.blit(sf_titolo, (LARGHEZZA_BARRA + LARGHEZZA_SCACCHIERA + 20, offset_stockfish))
        for i, riga in enumerate(top_mosse_testo):
            testo_mossa = font_piccolo.render(riga, True, COLORE_TESTO)
            screen.blit(testo_mossa, (LARGHEZZA_BARRA + LARGHEZZA_SCACCHIERA + 20, offset_stockfish + 35 + (i * 25)))
            
        istruzioni = ["[Click] Muovi", "[S] Salva mossa", "[R] Reset mosse qui", "[Backspace] Indietro", "[Esc] Menu"]
    else:
        info_testo = font_testo.render("Indovina la mossa!", True, (150, 255, 150))
        screen.blit(info_testo, (LARGHEZZA_BARRA + LARGHEZZA_SCACCHIERA + 20, 120))
        istruzioni = ["[Click] Fai la mossa", "[H] Aiuto (Hint)", "[Esc] Menu"]

    pygame.draw.line(screen, (100, 100, 100), (LARGHEZZA_BARRA + LARGHEZZA_SCACCHIERA + 20, 450), (WIDTH - 20, 450))
    for i, riga in enumerate(istruzioni):
        testo = font_piccolo.render(riga, True, (180, 180, 180))
        screen.blit(testo, (LARGHEZZA_BARRA + LARGHEZZA_SCACCHIERA + 20, 470 + (i * 25)))
        
    if msg_sistema:
        msg_render = font_testo.render(msg_sistema, True, (255, 100, 100))
        screen.blit(msg_render, (LARGHEZZA_BARRA + LARGHEZZA_SCACCHIERA + 20, HEIGHT - 50))

def ottieni_casa(x, y, orientamento_bianco):
    x_scacchiera = x - LARGHEZZA_BARRA # Sottraiamo l'offset della barra
    if x_scacchiera < 0 or x_scacchiera >= LARGHEZZA_SCACCHIERA: return None
    colonna = x_scacchiera // DIM_CASA
    riga = y // DIM_CASA
    return chess.square(colonna if orientamento_bianco else 7 - colonna, 7 - riga if orientamento_bianco else riga)

# --- CICLO PRINCIPALE ---
def main():
    carica_asset()
    carica_repertorio()
    board = chess.Board()
    
    try:
        engine = chess.engine.SimpleEngine.popen_uci(NOME_FILE_STOCKFISH)
        engine.configure({"Threads": 1, "Hash": 16})
    except Exception as e:
        print(f"Errore Stockfish: {e}")
        sys.exit()
    
    clock = pygame.time.Clock()
    running = True
    
    stato_attuale = "MENU"
    colore_scelto = "Bianco"
    casa_selezionata = None
    ultimo_fen_analizzato = ""
    top_mosse_testo = ["Calcolando..."]
    msg_sistema = ""
    valutazione_cp = 0 # Variabile globale per l'altezza della barra
    
    while running:
        if stato_attuale == "ALLENATI":
            turno_attuale = "Bianco" if board.turn == chess.WHITE else "Nero"
            if turno_attuale != colore_scelto:
                pygame.time.wait(400)
                mosse_valide = []
                for mossa in board.legal_moves:
                    board.push(mossa)
                    if board.fen() in repertori[colore_scelto]:
                        mosse_valide.append(mossa)
                    board.pop()
                
                if mosse_valide:
                    mossa_scelta = random.choice(mosse_valide)
                    is_cattura = board.is_capture(mossa_scelta)
                    board.push(mossa_scelta)
                    riproduci_suono("cattura" if is_cattura else "muovi")
                    msg_sistema = "Tocca a te!"
                else:
                    msg_sistema = "Fine linea raggiunta!"

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                
            elif event.type == pygame.KEYDOWN:
                if stato_attuale in ["MODIFICA", "ALLENATI"]:
                    if event.key == pygame.K_ESCAPE:
                        stato_attuale = "MENU"
                        msg_sistema = ""
                        
                    elif event.key in [pygame.K_LEFT, pygame.K_BACKSPACE] and stato_attuale == "MODIFICA":
                        if len(board.move_stack) > 0:
                            board.pop()
                            msg_sistema = "Mossa annullata."
                            casa_selezionata = None
                            
                    elif event.key == pygame.K_s and stato_attuale == "MODIFICA":
                        if len(board.move_stack) > 0:
                            ultima_mossa = board.pop()
                            fen_precedente = board.fen()
                            mossa_san = board.san(ultima_mossa)
                            
                            if fen_precedente not in repertori[colore_scelto]:
                                repertori[colore_scelto][fen_precedente] = []
                            if mossa_san not in repertori[colore_scelto][fen_precedente]:
                                repertori[colore_scelto][fen_precedente].append(mossa_san)
                                msg_sistema = f"Aggiunta: {mossa_san}!"
                            else:
                                msg_sistema = f"{mossa_san} già salvata!"
                                
                            salva_repertorio()
                            board.push(ultima_mossa)
                            
                    elif event.key == pygame.K_r and stato_attuale == "MODIFICA":
                        fen = board.fen()
                        if fen in repertori[colore_scelto]:
                            del repertori[colore_scelto][fen]
                            salva_repertorio()
                            msg_sistema = "Tutte le mosse resettate."
                            
                    elif event.key == pygame.K_h and stato_attuale == "ALLENATI":
                        fen = board.fen()
                        mosse_corr = repertori[colore_scelto].get(fen, [])
                        if mosse_corr:
                            iniziali = ", ".join(list(set(m[0] for m in mosse_corr)))
                            msg_sistema = f"Inizia con: {iniziali}"
                        else:
                            msg_sistema = "Nessuna mossa salvata qui."
                            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    x, y = event.pos
                    
                    if stato_attuale == "MENU":
                        rects = disegna_menu()
                        if rects["MOD_B"].collidepoint(x, y):
                            colore_scelto, stato_attuale, board, msg_sistema = "Bianco", "MODIFICA", chess.Board(), ""
                        elif rects["MOD_N"].collidepoint(x, y):
                            colore_scelto, stato_attuale, board, msg_sistema = "Nero", "MODIFICA", chess.Board(), ""
                        elif rects["ALL_B"].collidepoint(x, y):
                            colore_scelto, stato_attuale, board, msg_sistema = "Bianco", "ALLENATI", chess.Board(), ""
                        elif rects["ALL_N"].collidepoint(x, y):
                            colore_scelto, stato_attuale, board, msg_sistema = "Nero", "ALLENATI", chess.Board(), ""
                        elif rects["PGN_B"].collidepoint(x, y):
                            msg_sistema = importa_pgn("Bianco")
                        elif rects["PGN_N"].collidepoint(x, y):
                            msg_sistema = importa_pgn("Nero")
                            
                    elif stato_attuale in ["MODIFICA", "ALLENATI"]:
                        turno_attuale = "Bianco" if board.turn == chess.WHITE else "Nero"
                        if stato_attuale == "ALLENATI" and turno_attuale != colore_scelto:
                            continue

                        orientamento_bianco = (colore_scelto == "Bianco")
                        casa_cliccata = ottieni_casa(x, y, orientamento_bianco)
                        
                        if casa_cliccata is not None:
                            pezzo_cliccato = board.piece_at(casa_cliccata)
                            
                            if casa_selezionata is None:
                                if pezzo_cliccato and pezzo_cliccato.color == board.turn:
                                    casa_selezionata = casa_cliccata
                            else:
                                if pezzo_cliccato and pezzo_cliccato.color == board.turn:
                                    casa_selezionata = casa_cliccata
                                else:
                                    mossa = chess.Move(casa_selezionata, casa_cliccata)
                                    pezzo_da_muovere = board.piece_at(casa_selezionata)
                                    if pezzo_da_muovere and pezzo_da_muovere.piece_type == chess.PAWN:
                                        if chess.square_rank(casa_cliccata) in [0, 7]:
                                            mossa = chess.Move(casa_selezionata, casa_cliccata, promotion=chess.QUEEN)
                                    
                                    if mossa in board.legal_moves:
                                        is_cattura = board.is_capture(mossa)
                                        if stato_attuale == "MODIFICA":
                                            board.push(mossa)
                                            riproduci_suono("cattura" if is_cattura else "muovi")
                                            msg_sistema = ""
                                        elif stato_attuale == "ALLENATI":
                                            fen = board.fen()
                                            mosse_corr = repertori[colore_scelto].get(fen, [])
                                            if board.san(mossa) in mosse_corr:
                                                board.push(mossa)
                                                riproduci_suono("cattura" if is_cattura else "muovi")
                                                msg_sistema = "Esatto!"
                                            else:
                                                riproduci_suono("errore")
                                                msg_sistema = "Errore, riprova."
                                        casa_selezionata = None
                                    else:
                                        casa_selezionata = None

        if stato_attuale == "MODIFICA" and board.fen() != ultimo_fen_analizzato:
            ultimo_fen_analizzato = board.fen()
            top_mosse_testo = ["Calcolando..."]
            
            infos = engine.analyse(board, chess.engine.Limit(time=0.2), multipv=3)
            top_mosse_testo = []
            
            # Estraiamo anche la valutazione per disegnare la barra
            if infos and "score" in infos[0]:
                sc = infos[0]["score"].white()
                if sc.is_mate():
                    # Se è matto, diamo un valore altissimo alla barra
                    valutazione_cp = 10000 if sc.mate() > 0 else -10000
                else:
                    valutazione_cp = sc.score()
            
            for i, info in enumerate(infos):
                if "score" in info and "pv" in info:
                    sc = info["score"].white()
                    val = f"M{sc.mate()}" if sc.is_mate() else f"{sc.score()/100.0:+.2f}"
                    top_mosse_testo.append(f"{i+1}. {board.san(info['pv'][0])}  [{val}]")

        if stato_attuale == "MENU":
            disegna_menu()
            if msg_sistema:
                # Mostra nel menu quanti PGN sono stati importati
                msg_render = font_testo.render(msg_sistema, True, (255, 255, 100))
                screen.blit(msg_render, (WIDTH//2 - msg_render.get_width()//2, HEIGHT - 50))
        else:
            orientamento_bianco = (colore_scelto == "Bianco")
            disegna_barra_valutazione(valutazione_cp, orientamento_bianco)
            disegna_scacchiera()
            disegna_evidenziazioni(board, casa_selezionata, orientamento_bianco)
            disegna_pezzi(board, orientamento_bianco)
            disegna_pannello(stato_attuale, board, colore_scelto, top_mosse_testo, msg_sistema)
            
        pygame.display.flip()
        clock.tick(60)

    engine.quit()
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()