#Esercizio: smistamento di pratiche G1

from lotto import LOTTO

SOGLIA_REVISIONE_CENTESIMI = 100000
DOCUMENTI_MINIMI = 2

visti = set() 
smistate = []
duplicati = []

for richiesta in LOTTO:
    chiave = (richiesta["tenant"], richiesta["id"])
    if chiave in visti:
        duplicati.append(chiave)
        continue # salta al prossimo giro del ciclo for quando trova un duplicato
    visti.add(chiave)

    # 2. Agiamo sulla copia
    pulita = richiesta.copy()
    pulita["oggetto"] = richiesta["oggetto"].strip()

    # 3. regola_prove.py: la categoria dipende dall'importo e dal numero di documenti
    importo = pulita["importo_centesimi"]
    if importo is None:
        categoria = "da_completare"
    elif importo >= SOGLIA_REVISIONE_CENTESIMI or pulita["documenti"] < DOCUMENTI_MINIMI:
        categoria = "da_rivedere"
    else:
        categoria = "ordinaria"

    pulita["categoria"] = categoria
    smistate.append(pulita)

# 4. Le prove sui confini, prima di stampare: se una di queste righe diventa falsa,
#    il programma si ferma qui, e il riepilogo sbagliato non esce.
categoria_di = {}
for pratica in smistate:
    categoria_di[(pratica["tenant"], pratica["id"])] = pratica["categoria"]

assert categoria_di[("nova", "N-002")] == "da_completare"  # importo assente
assert categoria_di[("nova", "N-003")] == "ordinaria"  # zero è un importo presente
assert categoria_di[("nova", "N-004")] == "ordinaria"  # 99999: un centesimo sotto la soglia
assert categoria_di[("nova", "N-005")] == "da_rivedere"  # 100000: sulla soglia
assert categoria_di[("nova", "N-006")] == "da_rivedere"  # un documento solo
assert categoria_di[("aurora", "N-001")] == "ordinaria"  # stesso id, altro tenant: un'altra pratica
assert LOTTO[0]["oggetto"] == "  Preventivo vetro  "  # il lotto originale non è stato toccato

# 5. Il riepilogo che Marta legge.
conteggi = {"da_completare": 0, "da_rivedere": 0, "ordinaria": 0}
for pratica in smistate:
    conteggi[pratica["categoria"]] += 1

for pratica in smistate:
    print(f"{pratica['tenant']:<7} {pratica['id']:<6} {pratica['categoria']:<14} {pratica['oggetto']}")
print()
print(f"Lette: {len(LOTTO)}   Smistate: {len(smistate)}   Duplicati scartati: {len(duplicati)}")
for categoria, numero in conteggi.items():
    print(f"  {categoria:<14} {numero}")
print("\nProve sui confini: tutte superate.")