import requests

def testa_connessione():
    # La posizione di partenza degli scacchi
    fen_di_prova = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
    url = "https://explorer.lichess.ovh/lichess"
    
    parametri = {
        'fen': fen_di_prova,
        'speeds': 'blitz,rapid,classical',
        'moves': 4
    }
    
    headers = {
        # Sostituisci questo con un indirizzo email vero o molto realistico
        'User-Agent': 'ChessbookCloneTest/1.0 (info.tuonome@gmail.com)'
    }

    print(f"--- INIZIO TEST LICHESS API ---")
    print(f"URL: {url}")
    print(f"Parametri inviati: {parametri}")
    
    try:
        print("Inviando la richiesta...")
        risposta = requests.get(url, headers=headers, params=parametri, timeout=10)
        
        print(f"Codice di Stato HTTP: {risposta.status_code}")
        
        if risposta.status_code == 200:
            print("SUCCESSO! Ecco i primi dati ricevuti:")
            dati = risposta.json()
            print(f"Partite col Bianco: {dati.get('white')}")
            if 'moves' in dati and len(dati['moves']) > 0:
                print(f"Mossa più giocata: {dati['moves'][0]['san']}")
        else:
            print(f"IL SERVER HA RIFIUTATO LA RICHIESTA.")
            print(f"Messaggio del server: {risposta.text}")
            
    except Exception as e:
        print(f"ERRORE DI SISTEMA (Python non riesce a uscire su internet):")
        print(e)

if __name__ == "__main__":
    testa_connessione()