"""Funzioni per la chiave, smistamento e conteggio delle pratiche, con le regole di categorizzazione e normalizzazione dei dati."""

from collections.abc import Iterable
from typing import Any

from nova.modelli import PraticaSmistata, Richiesta
from nova.regole import categoria

CATEGORIE = ("da_completare", "da_rivedere", "ordinaria")


def chiave_pratica(richiesta: dict[str, Any]) -> tuple[str, str]:
    """La chiave è una tupla di due stringhe: organizzazione e identificativo."""
    return (richiesta["tenant"], richiesta["id"])


def smista(lotto: Iterable[Richiesta | dict[str, Any]]) -> tuple[list[PraticaSmistata], list[tuple[str, str]]]:
    """Restituisce le pratiche smistate, nella loro prima occorrenza, e le chiavi dei duplicati."""
    visti: set[tuple[str, str]] = set()
    smistate: list[PraticaSmistata] = []
    duplicati: list[tuple[str, str]] = []
    for item in lotto:
        richiesta = item if isinstance(item, Richiesta) else Richiesta.model_validate(item)
        chiave = richiesta.chiave()
        if chiave in visti:
            duplicati.append(chiave)
            continue
        visti.add(chiave)
        smistate.append(PraticaSmistata(richiesta, categoria(richiesta.importo_centesimi, richiesta.documenti)))
    return smistate, duplicati


def conteggi(smistate: Iterable[PraticaSmistata]) -> dict[str, int]:
    """Quante pratiche per categoria, con tutte le categorie presenti, anche a zero."""
    risultato = {nome: 0 for nome in CATEGORIE}
    for pratica in smistate:
        risultato[pratica.categoria] += 1
    return risultato