import lotto

# ESTENSIONE 3 Selezioniamo il lotto specifico proveniente dal portale web
from lotto import lotto_dal_portale

SOGLIA_REVISIONE_CENTESIMI = 100000
DOCUMENTI_MINIMI = 2

visti = set() 
smistate = []
duplicati = []
# ESTENSIONE 3 Tracciamento dei difetti del portale per Ivan
segnalazioni_ivan = []

for richiesta in lotto_dal_portale:
    # ESTENSIONE 3 Controllo preventivo: se mancano chiavi di sistema (tenant/id),senza far schiantare il programma con KeyError
    if "tenant" not in richiesta or "id" not in richiesta:
        segnalazioni_ivan.append(f"Manca tenant o id in {richiesta}")
        continue

    chiave = (richiesta["tenant"], richiesta["id"])
    if chiave in visti:
        duplicati.append(chiave)
        continue
    visti.add(chiave)

    pulita = richiesta.copy()
    
    # ESTENSIONE 3 Normalizzazione sicura dell'oggetto gestendo eventuali valori None/vuoti 
    if "oggetto" in pulita and pulita["oggetto"] is not None:
        pulita["oggetto"] = str(pulita["oggetto"]).strip()
    else:
        pulita["oggetto"] = ""

    # ESTENSIONE 3 Controllo esplicito 'in': verifichiamo che la chiave esista.
    # Usare .get() nasconderebbe l'assenza del campo trasformandola in un None silenzioso.
    if "importo_centesimi" not in richiesta:
        segnalazioni_ivan.append(f"Bug portale: chiave 'importo_centesimi' assente per {chiave}")
        continue
    
    importo = pulita["importo_centesimi"]

    # ESTENSIONE 3 Verifichiamo la presenza della chiave 'documenti'
    if "documenti" not in richiesta:
        segnalazioni_ivan.append(f"Bug portale: chiave 'documenti' assente per {chiave}")
        continue
        
    # ESTENSIONE 3 Conversione sicura: il portale a volte manda i documenti come testo.
    # Usiamo int() in un blocco try/except per evitare l'errore TypeError ("2" < 2).
    doc_raw = pulita["documenti"]
    try:
        documenti = int(doc_raw) if doc_raw is not None else 0
    except (ValueError, TypeError):
        segnalazioni_ivan.append(f"Bug portale: documenti non validi '{doc_raw}' per {chiave}")
        continue

    # Regola di smistamento (distingue importo None da importo >= SOGLIA o documenti insufficienti)
    if importo is None:
        categoria = "da_completare"
    elif importo >= SOGLIA_REVISIONE_CENTESIMI or documenti < DOCUMENTI_MINIMI:
        categoria = "da_rivedere"
    else:
        categoria = "ordinaria"

    pulita["categoria"] = categoria
    smistate.append(pulita)

# Conteggi finali
conteggi = {"da_completare": 0, "da_rivedere": 0, "ordinaria": 0}
for pratica in smistate:
    conteggi[pratica["categoria"]] += 1

# Stampa del riepilogo
print("=== RIEPILOGO SMISTAMENTO PORTALE ===")
for pratica in smistate:
    print(f"{pratica.get('tenant', 'N/A'):<7} {pratica.get('id', 'N/A'):<6} {pratica['categoria']:<14} {pratica.get('oggetto', '')}")

print()
print(f"Lette: {len(lotto_dal_portale)}   Smistate con successo: {len(smistate)}   Segnalazioni Ivan: {len(segnalazioni_ivan)}")
for categoria, numero in conteggi.items():
    print(f"  {categoria:<14} {numero}") #formatting allineato per leggibilità

# ESTENSIONE 3 Stampa dell'elenco delle anomalie rilevate dal portale
if segnalazioni_ivan:
    print("\nDettaglio segnalazioni per Ivan (Bug portale):")
    for s in segnalazioni_ivan:
        print(f" - {s}")