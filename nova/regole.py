# Regole di smistamento, categorizazzione e normalizzazione dei dati

SOGLIA_REVISIONE_CENTESIMI = 100000
DOCUMENTI_MINIMI = 2


def categoria(importo_centesimi: int | None, documenti: int) -> str:
     # Determina la categoria della richiesta in base alle regole di smistamento

    if importo_centesimi is None:
        return "da_completare"
    if importo_centesimi >= SOGLIA_REVISIONE_CENTESIMI or documenti < DOCUMENTI_MINIMI:
        return "da_rivedere"
    return "ordinaria"


def leggi_centesimi(testo: str) -> int | None:
    # Legge un importo in centesimi interi da una stringa. Restituisce None se la stringa è vuota
    # In caso di importo negativo o non valido, solleva un ValueError
    
    if testo == "":
        return None
    valore = int(testo)
    if valore < 0:
        raise ValueError(f"l'importo non può essere negativo: {testo!r}")
    return valore


def normalizza_oggetto(testo: str) -> str:
    # Toglie gli spazi in testa e in coda: la forma con cui l'oggetto si conserva

    return testo.strip()