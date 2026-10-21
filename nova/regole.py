# Regole di smistamento, categorizazzione e normalizzazione dei dati

SOGLIA_REVISIONE_CENTESIMI = 100000
DOCUMENTI_MINIMI = 2


def categoria(importo_centesimi: int | None, documenti: int) -> str:
     # Determina la categoria della richiesta in base alle regole di smistamento

    if documenti < 0:
        raise ValueError(f"il numero di documenti non può essere negativo: {documenti!r}")
    if importo_centesimi is None:
        return "da_completare"
    if importo_centesimi >= SOGLIA_REVISIONE_CENTESIMI or documenti < DOCUMENTI_MINIMI:
        return "da_rivedere"
    return "ordinaria"


def leggi_centesimi(testo: str) -> int | None:
    """Legge un importo in centesimi interi da una stringa formattata all'italiana.
    Rifiuta formati ambigui o errati (es. punti usati al posto della virgola).
    """
    # Se la stringa  è vuota o none e controlla se contiene il simbolo dell'euro, lo rimuove e pulisce gli spazi
    if not testo or not (testo := testo.replace("€", "").strip()):
        return None
        
    if testo.startswith("-"):
        raise ValueError(f"L'importo non può essere negativo: {testo!r}")
        
    parti = testo.split(",")
    if len(parti) > 2:
        raise ValueError(f"Formato non valido (troppe virgole): {testo!r}")
        
    # CASO 1: Nessuna virgola (es. "12500" oppure "1.250.000.00")
    if len(parti) == 1:
        # Verifica se ci sono punti e se sono usati correttamente come separatori delle migliaia
        if "." in testo:
            sottoparti = testo.split(".")
            # formattazione errata: usato il punto come separatore dei decimali invece della virgola
            if len(sottoparti[-1]) == 2:
                raise ValueError(f"Formato importo non valido (uso errato del punto): {testo!r}")

        #rimuove i punti e verifica che la parte intera sia composta solo da cifre        
        parte_intera = parti[0].replace(".", "")
        if not parte_intera.isdigit():
            raise ValueError(f"Importo non valido: {testo!r}")
        return int(parte_intera)

    # CASO 2: C'è la virgola (formato italiano con euro e centesimi, es. "125,50")
    parte_intera = parti[0].replace(".", "")
    decimale = parti[1]

    #verifica che entrambe le parti siano numeriche
    if not parte_intera.isdigit() or not decimale.isdigit():
        raise ValueError(f"Importo non valido: {testo!r}")
        
    euro = int(parte_intera)
    centesimi = int(decimale.ljust(2, '0')[:2])
    
    return euro * 100 + centesimi


def normalizza_oggetto(testo: str) -> str:
    # Toglie gli spazi in testa e in coda: la forma con cui l'oggetto si conserva
    if not isinstance(testo, str):
        raise TypeError(f"l'oggetto da normalizzare deve essere una stringa: {testo!r}")
    return testo.strip()