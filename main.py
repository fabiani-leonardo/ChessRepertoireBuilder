import chess
import chess.engine
import sys
import random
import json
import os

NOME_FILE_STOCKFISH = "stockfish-windows-x86-64-avx2.exe" 
FILE_REPERTORIO = "repertorio.json"

repertori = {
    "Bianco": {},
    "Nero": {}
}

def carica_repertorio():
    global repertori
    if os.path.exists(FILE_REPERTORIO):
        with open(FILE_REPERTORIO, "r", encoding="utf-8") as f:
            repertori = json.load(f)
        print(">>> Database repertori caricato con successo dal disco.")

def salva_repertorio():
    with open(FILE_REPERTORIO, "w", encoding="utf-8") as f:
        json.dump(repertori, f, indent=4)

def stampa_scacchiera(board, orientamento):
    print("\n" + "-"*30)
    if orientamento == "Bianco":
        print(board)
    else:
        righe = str(board).split('\n')
        righe_invertite = [riga[::-1] for riga in reversed(righe)]
        print('\n'.join(righe_invertite))
    print("-" * 30)

def menu_principale():
    carica_repertorio() 
    while True:
        print("\n" + "="*30)
        print(" CHESSBOOK CLONE - MENU")
        print("="*30)
        print("1. Modifica Repertorio")
        print("2. Allenati")
        print("3. Esci")
        print("="*30)
        
        scelta = input("Seleziona un'opzione (1/2/3): ")
        
        if scelta == '1':
            modifica_repertorio()
        elif scelta == '2':
            allenati()
        elif scelta == '3':
            print("Uscita dal programma. Arrivederci!")
            sys.exit()
        else:
            print("Scelta non valida. Riprova.")

def scegli_colore():
    while True:
        c = input("\nVuoi usare il repertorio del Bianco (B) o del Nero (N)? [B/N]: ").strip().upper()
        if c == 'B':
            return "Bianco"
        elif c == 'N':
            return "Nero"
        else:
            print("Scelta non valida. Inserisci B o N.")

def modifica_repertorio():
    colore_scelto = scegli_colore()
    rep_corrente = repertori[colore_scelto] 
    
    board = chess.Board()
    print(f"\n--- MODIFICA REPERTORIO: {colore_scelto.upper()} ---")
    print("Comandi:")
    print("- <mossa> : Gioca una mossa sulla scacchiera")
    print("- s <mossa> : SALVA la tua mossa (es. 's e4')")
    print("- r <mossa> : RIMUOVI una mossa salvata (es. 'r e4')")
    print("- b : Annulla l'ultima mossa (Back)")
    print("- q : Torna al Menu Principale (Quit)")
    
    with chess.engine.SimpleEngine.popen_uci(NOME_FILE_STOCKFISH) as engine:
        engine.configure({"Threads": 1, "Hash": 16})
        
        while True:
            stampa_scacchiera(board, colore_scelto)
            
            fen_corrente = board.fen()
            turno_attuale = "Bianco" if board.turn == chess.WHITE else "Nero"
            
            if fen_corrente in rep_corrente:
                print(f"[*] HAI GIA' UNA MOSSA IN REPERTORIO QUI: {rep_corrente[fen_corrente]}")
            
            print(f"[{turno_attuale} muove] - Stockfish sta pensando...")
            infos = engine.analyse(board, chess.engine.Limit(time=0.5), multipv=3)
            
            for i, info in enumerate(infos):
                if "score" in info and "pv" in info:
                    mossa_san = board.san(info["pv"][0])
                    score = info["score"].white()
                    val = f"M{score.mate()}" if score.is_mate() else f"{score.score()/100.0:+.2f}"
                    print(f"  {i+1}. {mossa_san} ({val})")
            
            scelta = input(f"\nMossa ({colore_scelto}): ").strip()
            
            if scelta.lower() == 'q':
                break
            elif scelta.lower() == 'b':
                if len(board.move_stack) > 0:
                    board.pop()
                else:
                    print("Sei già alla posizione di partenza!")
                    
            elif scelta.lower().startswith('s '):
                mossa_da_salvare = scelta[2:].strip()
                try:
                    mossa_reale = board.parse_san(mossa_da_salvare)
                    rep_corrente[fen_corrente] = mossa_da_salvare
                    salva_repertorio()
                    print(f">>> Mossa '{mossa_da_salvare}' salvata!")
                    board.push(mossa_reale)
                except ValueError:
                    print("Errore: Mossa illegale o non riconosciuta. Riprova.")
                    
            # NUOVO COMANDO: Rimuovi mossa
            elif scelta.lower().startswith('r '):
                mossa_da_rimuovere = scelta[2:].strip()
                
                # Controlliamo se in questa posizione c'è una mossa salvata e se è proprio quella indicata
                if fen_corrente in rep_corrente:
                    if rep_corrente[fen_corrente] == mossa_da_rimuovere:
                        del rep_corrente[fen_corrente] # La eliminiamo dal dizionario
                        salva_repertorio() # Aggiorniamo il file su disco
                        print(f">>> Mossa '{mossa_da_rimuovere}' rimossa dal repertorio con successo!")
                    else:
                        print(f"Errore: La mossa salvata qui è '{rep_corrente[fen_corrente]}', non '{mossa_da_rimuovere}'.")
                else:
                    print("Errore: Nessuna mossa salvata in questa posizione da rimuovere.")
                    
            else:
                try:
                    board.push_san(scelta)
                except ValueError:
                    print("Comando non riconosciuto o mossa illegale.")

def allenati():
    colore_scelto = scegli_colore()
    rep_corrente = repertori[colore_scelto]
    
    if not rep_corrente:
        print(f"\nIl repertorio del {colore_scelto} è vuoto! Vai prima in 'Modifica Repertorio'.")
        return
        
    board = chess.Board()
    print(f"\n--- ALLENAMENTO: {colore_scelto.upper()} ---")
    print("Comandi: <mossa> per indovinare, '?' per aiuto, 'q' per uscire")
    
    while True:
        stampa_scacchiera(board, colore_scelto)
        turno_attuale = "Bianco" if board.turn == chess.WHITE else "Nero"
        
        if turno_attuale == colore_scelto:
            fen_corrente = board.fen()
            
            if fen_corrente not in rep_corrente:
                print("\n🎉 Hai raggiunto la fine di questa linea del tuo repertorio!")
                if input("Vuoi allenarti di nuovo dall'inizio? (s/n): ").strip().lower() == 's':
                    board = chess.Board()
                    continue
                else:
                    break
                    
            mossa_corretta = rep_corrente[fen_corrente]
            
            while True:
                tentativo = input(f"\nTua mossa ({colore_scelto}): ").strip()
                if tentativo.lower() == 'q':
                    return
                elif tentativo == '?':
                    print(f"💡 Suggerimento: La mossa inizia con '{mossa_corretta[0]}'")
                    continue
                    
                if tentativo == mossa_corretta:
                    print("✅ Corretto!")
                    board.push_san(mossa_corretta)
                    break
                else:
                    print("❌ Mossa errata. Riprova (oppure digita '?' per un aiuto).")
                    
        else:
            print("\nL'avversario sta muovendo...")
            mosse_avversario_valide = []
            
            for mossa in board.legal_moves:
                board.push(mossa)
                if board.fen() in rep_corrente:
                    mosse_avversario_valide.append(mossa)
                board.pop()
                
            if not mosse_avversario_valide:
                print("\nFine della linea: non hai preparato risposte per le possibili mosse dell'avversario qui.")
                if input("Vuoi allenarti di nuovo dall'inizio? (s/n): ").strip().lower() == 's':
                    board = chess.Board()
                    continue
                else:
                    break
                    
            mossa_scelta = random.choice(mosse_avversario_valide)
            print(f"L'avversario gioca: {board.san(mossa_scelta)}")
            board.push(mossa_scelta)

if __name__ == "__main__":
    menu_principale()