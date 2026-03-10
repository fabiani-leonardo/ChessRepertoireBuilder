import pygame
import sys
import chess
import chess.engine
import json
import os
import random

# --- INIZIALIZZAZIONE ---
pygame.init()
pygame.font.init()

# --- COSTANTI & IMPOSTAZIONI ---
LARGHEZZA_SCACCHIERA = 640
LARGHEZZA_PANNELLO = 300
WIDTH = LARGHEZZA_SCACCHIERA + LARGHEZZA_PANNELLO
HEIGHT = 640
DIM_CASA = LARGHEZZA_SCACCHIERA // 8

COLORE_CHIARO = (240, 217, 181)
COLORE_SCURO = (181, 136, 99)
COLORE_SFONDO = (40, 40, 40)
COLORE_PANNELLO = (30, 30, 30)
COLORE_TESTO = (255, 255, 255)
COLORE_EVIDENZIA = (0, 255, 0)

NOME_FILE_STOCKFISH = "stockfish-windows-x86-64-avx2.exe" 
FILE_REPERTORIO = "repertorio.json"

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Chessbook Clone - Albero Varianti")

font_menu = pygame.font.SysFont("arial", 40, bold=True)
font_testo = pygame.font.SysFont("arial", 20)
font_piccolo = pygame.font.SysFont("arial", 16)

IMAGES = {}
repertori = {"Bianco": {}, "Nero": {}}

# --- FUNZIONI DI BASE ---
def carica_immagini():
    pezzi = {
        'P': 'wP', 'N': 'wN', 'B': 'wB', 'R': 'wR', 'Q': 'wQ', 'K': 'wK',
        'p': 'bP', 'n': 'bN', 'b': 'bB', 'r': 'bR', 'q': 'bQ', 'k': 'bK'
    }
    for simbolo, nome_file in pezzi.items():
        try:
            img = pygame.image.load(f"images/{nome_file}.png")
            IMAGES[simbolo] = pygame.transform.scale(img, (DIM_CASA, DIM_CASA))
        except:
            pass

def carica_repertorio():
    global repertori
    if os.path.exists(FILE_REPERTORIO):
        with open(FILE_REPERTORIO, "r", encoding="utf-8") as f:
            dati_salvati = json.load(f)
            # MIGRAZIONE: Convertiamo le vecchie stringhe in liste
            for colore in dati_salvati:
                for fen, mosse in dati_salvati[colore].items():
                    if isinstance(mosse, str):
                        dati_salvati[colore][fen] = [mosse]
            repertori = dati_salvati

def salva_repertorio():
    with open(FILE_REPERTORIO, "w", encoding="utf-8") as f:
        json.dump(repertori, f, indent=4)

# --- FUNZIONI GRAFICHE ---
def disegna_menu():
    screen.fill(COLORE_SFONDO)
    titolo = font_menu.render("CHESSBOOK CLONE", True, COLORE_TESTO)
    screen.blit(titolo, (WIDTH//2 - titolo.get_width()//2, 50))

    rects = {
        "MOD_B": pygame.Rect(WIDTH//2 - 200, 150, 400, 50),
        "MOD_N": pygame.Rect(WIDTH//2 - 200, 220, 400, 50),
        "ALL_B": pygame.Rect(WIDTH//2 - 200, 320, 400, 50),
        "ALL_N": pygame.Rect(WIDTH//2 - 200, 390, 400, 50)
    }
    
    pygame.draw.rect(screen, (70, 130, 180), rects["MOD_B"], border_radius=10)
    pygame.draw.rect(screen, (50, 100, 150), rects["MOD_N"], border_radius=10)
    pygame.draw.rect(screen, (46, 139, 87), rects["ALL_B"], border_radius=10)
    pygame.draw.rect(screen, (34, 100, 60), rects["ALL_N"], border_radius=10)
    
    testi = {
        "MOD_B": "1. Modifica Repertorio - BIANCO",
        "MOD_N": "2. Modifica Repertorio - NERO",
        "ALL_B": "3. Allenati - BIANCO",
        "ALL_N": "4. Allenati - NERO"
    }
    
    for chiave, rect in rects.items():
        t = font_testo.render(testi[chiave], True, COLORE_TESTO)
        screen.blit(t, (rect.centerx - t.get_width()//2, rect.centery - t.get_height()//2))
        
    return rects

def disegna_scacchiera():
    for riga in range(8):
        for colonna in range(8):
            colore = COLORE_CHIARO if (riga + colonna) % 2 == 0 else COLORE_SCURO
            pygame.draw.rect(screen, colore, pygame.Rect(colonna * DIM_CASA, riga * DIM_CASA, DIM_CASA, DIM_CASA))

def disegna_pezzi(board, orientamento_bianco=True):
    for square in chess.SQUARES:
        pezzo = board.piece_at(square)
        if pezzo:
            colonna = chess.square_file(square)
            riga = chess.square_rank(square)
            x = colonna if orientamento_bianco else 7 - colonna
            y = 7 - riga if orientamento_bianco else riga
            screen.blit(IMAGES[pezzo.symbol()], pygame.Rect(x * DIM_CASA, y * DIM_CASA, DIM_CASA, DIM_CASA))

def disegna_evidenziazione(casa, orientamento_bianco=True):
    if casa is not None:
        colonna = chess.square_file(casa)
        riga = chess.square_rank(casa)
        x = colonna if orientamento_bianco else 7 - colonna
        y = 7 - riga if orientamento_bianco else riga
        s = pygame.Surface((DIM_CASA, DIM_CASA))
        s.set_alpha(100)
        s.fill(COLORE_EVIDENZIA)
        screen.blit(s, (x * DIM_CASA, y * DIM_CASA))

def disegna_pannello(stato, board, colore_scelto, top_mosse_testo, msg_sistema):
    pannello_rect = pygame.Rect(LARGHEZZA_SCACCHIERA, 0, LARGHEZZA_PANNELLO, HEIGHT)
    pygame.draw.rect(screen, COLORE_PANNELLO, pannello_rect)
    
    titolo = font_testo.render(f"Modo: {stato} ({colore_scelto})", True, (255, 215, 0))
    screen.blit(titolo, (LARGHEZZA_SCACCHIERA + 20, 20))
    
    fen = board.fen()
    
    # NOVITÀ: Estraiamo la lista delle mosse e le uniamo con una virgola
    mosse_salvate = repertori[colore_scelto].get(fen, [])
    testo_salvate = ", ".join(mosse_salvate) if mosse_salvate else "Nessuna"
    
    if stato == "MODIFICA":
        rep_testo = font_testo.render(f"Salvate: {testo_salvate}", True, (100, 255, 100) if mosse_salvate else (200, 200, 200))
        screen.blit(rep_testo, (LARGHEZZA_SCACCHIERA + 20, 60))
        
        sf_titolo = font_testo.render("Analisi Stockfish:", True, (150, 200, 255))
        screen.blit(sf_titolo, (LARGHEZZA_SCACCHIERA + 20, 120))
        for i, riga in enumerate(top_mosse_testo):
            testo_mossa = font_piccolo.render(riga, True, COLORE_TESTO)
            screen.blit(testo_mossa, (LARGHEZZA_SCACCHIERA + 20, 160 + (i * 25)))
            
        istruzioni = ["[Click] Muovi", "[S] Salva mossa", "[R] Reset mosse qui", "[Backspace] Indietro", "[Esc] Menu"]
    else:
        info_testo = font_testo.render("Indovina la mossa!", True, (150, 255, 150))
        screen.blit(info_testo, (LARGHEZZA_SCACCHIERA + 20, 120))
        istruzioni = ["[Click] Fai la mossa", "[H] Aiuto (Hint)", "[Esc] Menu"]

    pygame.draw.line(screen, (100, 100, 100), (LARGHEZZA_SCACCHIERA + 20, 450), (WIDTH - 20, 450))
    for i, riga in enumerate(istruzioni):
        testo = font_piccolo.render(riga, True, (180, 180, 180))
        screen.blit(testo, (LARGHEZZA_SCACCHIERA + 20, 470 + (i * 25)))
        
    if msg_sistema:
        msg_render = font_testo.render(msg_sistema, True, (255, 100, 100))
        screen.blit(msg_render, (LARGHEZZA_SCACCHIERA + 20, HEIGHT - 50))

def ottieni_casa(x, y, orientamento_bianco):
    if x >= LARGHEZZA_SCACCHIERA: return None
    colonna = x // DIM_CASA
    riga = y // DIM_CASA
    return chess.square(colonna if orientamento_bianco else 7 - colonna, 7 - riga if orientamento_bianco else riga)

# --- CICLO PRINCIPALE ---
def main():
    carica_immagini()
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
                    board.push(random.choice(mosse_valide))
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
                            
                            # LOGICA MULTIPLA: Aggiungiamo alla lista invece di sovrascrivere
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
                        # Rimuove l'intera lista per questa posizione
                        fen = board.fen()
                        if fen in repertori[colore_scelto]:
                            del repertori[colore_scelto][fen]
                            salva_repertorio()
                            msg_sistema = "Tutte le mosse resettate."
                            
                    elif event.key == pygame.K_h and stato_attuale == "ALLENATI":
                        fen = board.fen()
                        mosse_corr = repertori[colore_scelto].get(fen, [])
                        if mosse_corr:
                            # Prende la prima lettera di ogni mossa salvata
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
                                        if stato_attuale == "MODIFICA":
                                            board.push(mossa)
                                            msg_sistema = ""
                                        elif stato_attuale == "ALLENATI":
                                            fen = board.fen()
                                            
                                            # LOGICA MULTIPLA IN ALLENAMENTO
                                            mosse_corr = repertori[colore_scelto].get(fen, [])
                                            if board.san(mossa) in mosse_corr:
                                                board.push(mossa)
                                                msg_sistema = "Esatto!"
                                            else:
                                                msg_sistema = "Errore, riprova."
                                        casa_selezionata = None
                                    else:
                                        casa_selezionata = None

        if stato_attuale == "MODIFICA" and board.fen() != ultimo_fen_analizzato:
            ultimo_fen_analizzato = board.fen()
            top_mosse_testo = ["Calcolando..."]
            disegna_scacchiera()
            disegna_pannello(stato_attuale, board, colore_scelto, top_mosse_testo, msg_sistema)
            pygame.display.flip()
            
            infos = engine.analyse(board, chess.engine.Limit(time=0.2), multipv=3)
            top_mosse_testo = []
            for i, info in enumerate(infos):
                if "score" in info and "pv" in info:
                    sc = info["score"].white()
                    val = f"M{sc.mate()}" if sc.is_mate() else f"{sc.score()/100.0:+.2f}"
                    top_mosse_testo.append(f"{i+1}. {board.san(info['pv'][0])}  [{val}]")

        if stato_attuale == "MENU":
            disegna_menu()
        else:
            orientamento_bianco = (colore_scelto == "Bianco")
            disegna_scacchiera()
            disegna_evidenziazione(casa_selezionata, orientamento_bianco)
            disegna_pezzi(board, orientamento_bianco)
            disegna_pannello(stato_attuale, board, colore_scelto, top_mosse_testo, msg_sistema)
            
        pygame.display.flip()
        clock.tick(60)

    engine.quit()
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()