import os
import urllib.request
import time

if not os.path.exists("images"):
    os.makedirs("images")

urls = {
    'P': 'https://upload.wikimedia.org/wikipedia/commons/thumb/4/45/Chess_plt45.svg/150px-Chess_plt45.svg.png',
    'N': 'https://upload.wikimedia.org/wikipedia/commons/thumb/7/70/Chess_nlt45.svg/150px-Chess_nlt45.svg.png',
    'B': 'https://upload.wikimedia.org/wikipedia/commons/thumb/b/b1/Chess_blt45.svg/150px-Chess_blt45.svg.png',
    'R': 'https://upload.wikimedia.org/wikipedia/commons/thumb/7/72/Chess_rlt45.svg/150px-Chess_rlt45.svg.png',
    'Q': 'https://upload.wikimedia.org/wikipedia/commons/thumb/1/15/Chess_qlt45.svg/150px-Chess_qlt45.svg.png',
    'K': 'https://upload.wikimedia.org/wikipedia/commons/thumb/4/42/Chess_klt45.svg/150px-Chess_klt45.svg.png',
    'p': 'https://upload.wikimedia.org/wikipedia/commons/thumb/c/c7/Chess_pdt45.svg/150px-Chess_pdt45.svg.png',
    'n': 'https://upload.wikimedia.org/wikipedia/commons/thumb/e/ed/Chess_ndt45.svg/150px-Chess_ndt45.svg.png',
    'b': 'https://upload.wikimedia.org/wikipedia/commons/thumb/9/98/Chess_bdt45.svg/150px-Chess_bdt45.svg.png',
    'r': 'https://upload.wikimedia.org/wikipedia/commons/thumb/f/ff/Chess_rdt45.svg/150px-Chess_rdt45.svg.png',
    'q': 'https://upload.wikimedia.org/wikipedia/commons/thumb/4/47/Chess_qdt45.svg/150px-Chess_qdt45.svg.png',
    'k': 'https://upload.wikimedia.org/wikipedia/commons/thumb/f/f0/Chess_kdt45.svg/150px-Chess_kdt45.svg.png'
}

print("Scaricamento delle immagini (modalità lenta anti-blocco)...")

# User-Agent conforme alle policy di Wikimedia
headers = {'User-Agent': 'ChessRepertoireBuilder/1.0 (studente.ingegneria@example.com) Python'}

for pezzo, url in urls.items():
    file_path = f"images/{pezzo}.png"
    if not os.path.exists(file_path):
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req) as response, open(file_path, 'wb') as out_file:
                out_file.write(response.read())
            print(f"Scaricato con successo: {pezzo}.png")
            
            # Rate limiting: aspettiamo 1 secondo per non far arrabbiare il server
            time.sleep(1) 
            
        except Exception as e:
            print(f"Errore nello scaricare {pezzo}: {e}")
    else:
        print(f"File {pezzo}.png già presente.")

print("Download completato! Ora hai la cartella 'images' pronta all'uso.")