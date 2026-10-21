#Funzioni presa da smista.py per la chiave, smistamento e conteggio delle pratiche, con le regole di categorizzazione e normalizzazione dei dati.

from nova.regole import categoria, normalizza_oggetto

CATEGORIE = ("da_completare", "da_rivedere", "ordinaria")


def chiave_pratica(richiesta: dict) -> tuple[str, str]:
    # La chiave è una tupla di due stringhe: organizzazione e identificativo
    return (richiesta["tenant"], richiesta["id"])


def smista(lotto: list[dict]) -> tuple[list[dict], list[tuple[str, str]]]:
    # Smista un lotto di richieste, restituendo due liste: le richieste smistate e le chiavi delle richieste duplicate
    
    visti = set()
    smistate = []
    duplicati = []
    for richiesta in lotto:
        chiave = chiave_pratica(richiesta)
        if chiave in visti:
            duplicati.append(chiave)
            continue
        visti.add(chiave)
        pulita = richiesta.copy()
        pulita["oggetto"] = normalizza_oggetto(richiesta["oggetto"])
        pulita["categoria"] = categoria(pulita["importo_centesimi"], pulita["documenti"])
        smistate.append(pulita)
    return smistate, duplicati


def conteggi(smistate: list[dict]) -> dict[str, int]:
    # Conteggio delle pratiche per categoria

    risultato = {}
    for nome in CATEGORIE:
        risultato[nome] = 0
    for pratica in smistate:
        risultato[pratica["categoria"]] += 1
    return risultato


