# nova-smistamento

Smista le richieste di rimborso di Nova Assicurazioni: ogni pratica esce con una categoria (`da_completare`,
`da_rivedere`, `ordinaria`). Funziona in due modi: come comando che smista un lotto in locale, e come servizio HTTP
che riceve le pratiche una alla volta, con un client che gli invia un lotto intero. I dati sono sintetici e le
categorie sono convenzioni di laboratorio: non autorizzano rimborsi.

## Requisiti

- [uv](https://docs.astral.sh/uv/) installato. Python 3.12 lo procura uv da sé.

## Configurazione

```bash
cp .env.example .env          # su Windows: Copy-Item .env.example .env
uv run python -c "import secrets; print(secrets.token_urlsafe(32))"
```

Incolla il valore generato in `.env`, dopo `NOVA_CHIAVE_SERVIZIO=`. Il file `.env` resta sulla tua macchina: è
escluso da Git. Ogni variabile si può anche impostare nell'ambiente, che prevale sul file.

| Variabile | Che cosa fa | Predefinito |
|---|---|---|
| `NOVA_CHIAVE_SERVIZIO` | la chiave che il client manda e il servizio controlla | nessuno: obbligatoria |
| `NOVA_URL_SERVIZIO` | dove il client trova il servizio | `http://127.0.0.1:8000` |
| `NOVA_CONCORRENZA_MASSIMA` | quante richieste il client manda insieme | `4` |
| `NOVA_TIMEOUT_SECONDI` | quanto il client aspetta ogni operazione di rete | `5` |

## Come si avvia

Dalla cartella del progetto:

```bash
uv run python -m nova                          # smista dati/lotto.jsonl in locale
uv run uvicorn nova.servizio:app               # il servizio, su http://127.0.0.1:8000
uv run python -m nova.invio                    # in un secondo terminale: invia il lotto al servizio
```

La documentazione interattiva del servizio è su `http://127.0.0.1:8000/docs`. `python -m nova` esce con `1` se il
lotto non si legge o una riga è rifiutata. `python -m nova.invio` esce con `1` se l'invio non parte o si interrompe, e con `0` anche
quando qualche pratica è scaduta o rifiutata: gli esiti dicono quali.

## Il servizio

| Metodo e percorso | Che cosa fa | Risposte |
|---|---|---|
| `GET /health` | stato e numero di pratiche registrate | `200` |
| `POST /pratiche` | smista e registra una richiesta | `201`, `401`, `409` se già registrata, `422` se i dati non vanno |
| `GET /pratiche/{tenant}/{id}` | legge una pratica registrata | `200`, `401`, `404` |
| `GET /riepilogo` | conteggi per categoria | `200`, `401` |

Tutto tranne `/health` richiede l'intestazione `X-Chiave-Servizio`. Il registro vive in memoria e si svuota quando
il servizio si ferma.

## Controlli

```bash
uv run pytest
uv run mypy nova
uv run ruff check .
uv run ruff format --check .
```

## La regola

| condizione, nell'ordine | categoria |
|---|---|
| importo assente (`None`) | `da_completare` |
| importo di almeno 100000 centesimi, oppure meno di 2 documenti | `da_rivedere` |
| altrimenti | `ordinaria` |

Una pratica è identificata dalla coppia `(tenant, id)`. Nel lotto si conserva la prima occorrenza; il servizio
rifiuta con `409` una pratica già registrata, quindi rilanciare l'invio non crea doppioni.


# Esercitazione G1: sviluppo estensione 3, lettura dei dati dal portale web

    ## Strada scelta e difesa

        Si è optato per l'estensione 3, quindi quella di distinguere rigorosamente tra campi mancanti nel portale (segnalati a Ivan come anomalia tecnica) e valori None (pratiche da far completare al cliente).

        Evitando l'uso indiscriminato di .get() sui dati obbligatori per impedire che errori strutturali del portale finissero senza volerlo tra le pratiche ordinarie.

        Inseriti 3 controlli preventivi obbligatori (tenant/id, importo, documenti) prima di applicare la logica di categoria.

    ## Riepilogo (Delta prima e dopo)

        Report prima dell'estensione: 
            nova    N-001  ordinaria      Preventivo vetro
            nova    N-002  da_completare  Fattura carrozzeria
            nova    N-003  ordinaria      Ricevuta farmacia
            nova    N-004  ordinaria      Preventivo tetto
            nova    N-005  da_rivedere    Perizia allagamento
            nova    N-006  da_rivedere    Foto danno auto
            aurora  N-001  ordinaria      Cristallo anteriore
            nova    N-007  da_completare  Visita specialistica
            aurora  N-008  da_rivedere    Danno da grandine

            Lette: 11   Smistate: 9   Duplicati scartati: 2
            da_completare  2
            da_rivedere    3
            ordinaria      4

        Report con Estensione Portale:

            === RIEPILOGO SMISTAMENTO PORTALE ===
            nova    W-101  ordinaria      Occhiali da vista
            nova    W-102  da_completare  Fisioterapia
            nova    W-104  ordinaria      Analisi del sangue

            Lette: 5   Smistate con successo: 3   Segnalazioni Ivan: 2
            da_completare  1
            da_rivedere    0
            ordinaria      2

            Dettaglio segnalazioni per Ivan (Bug portale):
            - Bug portale: chiave 'importo_centesimi' assente per ('nova', 'W-103')
            - Bug portale: chiave 'documenti' assente per ('nova', 'W-105')

     ## Revisione del codice scritto con l'AI

        - Evitato l'uso di if importo: per non confondere l'importo a zero con un campo mancante.
        - Utilizzato richiesta.copy() per preservare intatto il lotto originale in ingresso.
        - Evitato .get() silenzioso sui campi obbligatori per fare emergere i KeyError.
        - Gestione sicura delle stringhe nei documenti tramite int() protetto da try/except.

    ## Prova del collega
        Tempo impiegato: 2 minuti.
        Nessun blocco eseguendo il comando da terminale pulito.



# Esercitazione G2: sviluppo estensione 1, gli importi come li scrive una persona

    #Scelta della strada e motivazioni
    Parsing basato su stringhe e calcolo intero in centesimi (euro * 100 + centesimi), senza passare per i numeri in virgola mobile (float).

        - Precisione finanziaria: Evita alla radice i problemi di arrotondamento binario tipici dei tipi float nei calcoli monetari.

        - Rispetto dello standard italiano: Gestisce correttamente il punto come separatore delle migliaia e la virgola come separatore decimale, normalizzando i formati umani (es. ,5 a 50 centesimi).

        - Resilienza e robustezza: Integra validazioni preventive contro importi negativi, stringhe vuote e formati ambigui o scorretti, garantendo coerenza con i tracciati di archivio.

    #Misure prima e dopo
        - Prima (Approccio float/sostituzione): Incapace di gestire correttamente i separatori delle migliaia (es. 1.250,00 errato) e soggetto a imprecisioni sui decimali (es. 0,29 errato).

        - Dopo (Approccio intero su stringhe): 100% di test superati (34/34), lettura accurata di tutti i formati operativi del back-office e zero centesimi persi.

    #Revisione del codice scritto con l'AI
        Il supporto dell'intelligenza artificiale ha permesso di accelerare la stesura della logica di split e dei casi limite con @pytest.mark.parametrize.

    Rilievo deciso di non correggere: 
        Il codice non implementa un controllo formale rigido sul numero esatto di cifre tra un punto e l'altro delle         migliaia (es. accetta formalmente stringhe con formati di spaziatura personalizzati purché senza cifre decimali anomale). Si è scelto di lasciarlo così poiché i dati in ingresso provengono esclusivamente da operatori umani guidati da schermate standardizzate, rendendo superflua una espressione regolare troppo complessa che avrebbe ridotto la leggibilità del codice.

    #Test di usabilità (Prova del collega)
        Tempo impiegato: 6 minuti.

        Primo blocco riscontrato: Esecuzione iniziale di pytest senza passare attraverso il gestore di ambiente (uv run). Risolto seguendo le istruzioni esplicite presenti nel README.


# Esercitazione G3: sviluppo estensione 3, il riepilogo come oggetto

    #Scelta della strada e motivazioni
    Incapsulamento dei conteggi di smistamento in una dataclass congelata (frozen=True) con metodi nativi per il calcolo dei totali e delle quote percentuali.

        - Immutabilità e sicurezza: Protezione dello stato del riepilogo per impedire modifiche accidentali dopo il calcolo, garantendo la coerenza dei dati passati ai log o ai flussi successivi.

        - Incapsulamento della logica: Spostamento dei calcoli statistici (somme, percentuali) dall'interfaccia o dal modulo principale direttamente all'oggetto, migliorando la manutenibilità e la coesione del codice.

        - Resilienza contro i edge cases: Gestione sicura della divisione per zero nel calcolo delle quote in presenza di lotti vuoti, e utilizzo di default_factory per prevenire il rischio di condivisione di dizionari mutabili tra le istanze.

    #Misure prima e dopo
        - Prima (Dizionari sparsi e logica procedurale): Conteggi gestiti tramite semplici dizionari nel main, calcoli percentuali duplicati e logica di stampa dispersa.

        - Dopo (Oggetto riepilogo tipizzato e immutabile): Codice pulito, fortemente tipizzato con mypy, con rappresentazione testuale integrata (__str__) e logica di business centralizzata.

    #Revisione del codice scritto con l'AI
        Il supporto dell'intelligenza artificiale ha permesso di impostare rapidamente la dataclass congelata e di intercettare correttamente la classica trappola della default_factory per i dizionari in Python.

    Rilievo deciso di non correggere: 
        Si è scelto di non inserire un controllo dinamico complesso sulle chiavi delle categorie all'interno del costruttore della dataclass, poiché l'insieme delle categorie è già chiuso, noto e rigorosamente validato a monte dal modulo delle regole.

    #Test di usabilità (Prova del collega)
        Tempo impiegato: 5 minuti.

        Primo blocco riscontrato: Tentativo iniziale di assegnare un dizionario direttamente come valore predefinito nel campo della dataclass, bloccato dall'eccezione nativa di Python sulla mutabilità. Risolto applicando correttamente la `default_factory` con una lambda function.