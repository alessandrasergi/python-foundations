"""Il confine: dal file JSONL del gestionale alle richieste validate."""

import json
from contextlib import closing
from pathlib import Path
from typing import Any

from pydantic import ValidationError

from nova.flussi import leggi_jsonl
from nova.modelli import Richiesta
from nova.regole import leggi_centesimi, normalizza_oggetto


def adatta(riga: Any) -> Any:
    """Porta una riga del gestionale nella forma del modello, con due conversioni dichiarate.

    Il gestionale esporta l'importo come testo in centesimi, e l'oggetto così come è stato digitato:
    qui l'importo diventa un intero o None, e l'oggetto perde gli spazi esterni. Tutto il resto passa
    com'è, e lo giudica il modello.
    """
    if not isinstance(riga, dict):
        return riga
    adattata = dict(riga)
    if isinstance(riga.get("importo_centesimi"), str):
        adattata["importo_centesimi"] = leggi_centesimi(riga["importo_centesimi"])
    if isinstance(riga.get("oggetto"), str):
        adattata["oggetto"] = normalizza_oggetto(riga["oggetto"])
    return adattata


def descrivi(errore: ValidationError) -> str:
    """Il primo problema di una validazione, in una riga: il campo e che cosa non va."""
    primo = errore.errors()[0]
    campo = ".".join(str(parte) for parte in primo["loc"]) or "richiesta"
    return f"{campo}: {primo['msg']}"


def leggi_lotto(percorso: Path) -> list[Richiesta]:
    """Legge il lotto riga per riga, adatta e valida ogni richiesta.

    Si ferma alla prima riga che non è JSON valido, che ha un importo illeggibile o che il modello
    rifiuta, con un ValueError che dice quale riga e perché. Il lotto si valida tutto prima di
    essere smistato.
    """
    lotto = []
    testo = percorso.read_text(encoding="utf-8").strip()

    # Se il file è un JSON standard racchiuso tra parentesi quadre
    if testo.startswith("["):
        try:
            dati_json = json.loads(testo)
        except json.JSONDecodeError as errore:
            # Calcoliamo la riga approssimativa o usiamo l'errore standard atteso dai test
            riga_err = errore.lineno if hasattr(errore, 'lineno') else 1
            raise ValueError(f"{percorso}, riga {riga_err}: JSON non valido") from errore

        for indice, item in enumerate(dati_json, start=1):
            dove = f"{percorso}, riga {indice}"
            try:
                richiesta = Richiesta.model_validate(adatta(item))
            except ValidationError as errore:
                raise ValueError(f"{dove}: {descrivi(errore)}") from errore
            except ValueError as errore:
                importo_val = item.get('importo_centesimi') if isinstance(item, dict) else None
                raise ValueError(f"{dove}: importo non valido {importo_val!r}") from errore
            lotto.append(richiesta)
        return lotto

    # Altrimenti gestione JSONL standard tramite generatore
    with closing(leggi_jsonl(percorso)) as righe:
        for numero, riga in righe:
            dove = f"{percorso}, riga {numero}"
            try:
                richiesta = Richiesta.model_validate(adatta(riga))
            except ValidationError as errore:
                raise ValueError(f"{dove}: {descrivi(errore)}") from errore
            except ValueError as errore:
                importo_val = riga.get('importo_centesimi') if isinstance(riga, dict) else None
                raise ValueError(f"{dove}: importo non valido {importo_val!r}") from errore
            lotto.append(richiesta)
    return lotto