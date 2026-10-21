# Legge i dati, smistandoli e stampando un riepilogo, con il numero di pratiche per categoria

import sys
from pathlib import Path

from nova.archivio import leggi_lotto
from nova.smistamento import conteggi, smista

PERCORSO_PREDEFINITO = Path("dati") / "lotto.json"


def main(argomenti: list[str]) -> int:
    # legge il lotto di pratiche da un file JSON, lo smista e stampa un riepilogo
    percorso = Path(argomenti[0]) if argomenti else PERCORSO_PREDEFINITO
    try:
        lotto = leggi_lotto(percorso)
    except (FileNotFoundError, ValueError) as errore:
        print(f"Lotto non leggibile. {errore}", file=sys.stderr)
        return 1

    smistate, duplicati = smista(lotto)
    for pratica in smistate:
        print(f"{pratica['tenant']:<7} {pratica['id']:<6} {pratica['categoria']:<14} {pratica['oggetto']}")
    print()
    print(f"Lette: {len(lotto)}   Smistate: {len(smistate)}   Duplicati scartati: {len(duplicati)}")
    for nome, numero in conteggi(smistate).items():
        print(f"  {nome:<14} {numero}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))