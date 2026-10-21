#Necessario per la lettura dei lotti di pratiche esportati dal gestionale

import json
from pathlib import Path

from nova.regole import leggi_centesimi


def leggi_lotto(percorso: Path) -> list[dict]:
    # Legge il lotto e converte ogni importo in centesimi interi.
    # Funzionamento:esporta l'importo come testo, e un importo non compilato come "".
    # In caso di file JSON non valido o di una richiesta con un importo non leggibile, la
    # lettura si ferma con un ValueError dicendo dove guardare
   
    testo = percorso.read_text(encoding="utf-8")
    try:
        righe = json.loads(testo)
    except json.JSONDecodeError as errore:
        raise ValueError(f"{percorso}: JSON non valido alla riga {errore.lineno}, colonna {errore.colno}") from errore

    lotto = []
    for posizione, riga in enumerate(righe, start=1):
        richiesta = riga.copy()
        try:
            richiesta["importo_centesimi"] = leggi_centesimi(riga["importo_centesimi"])
        except ValueError as errore:
            raise ValueError(
                f"{percorso}: richiesta n. {posizione} ({riga['id']}), importo non valido {riga['importo_centesimi']!r}"
            ) from errore
        lotto.append(richiesta)
    return lotto


