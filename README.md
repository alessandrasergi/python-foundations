# nova-smistamento

Strumento per elaborare i pacchetti di richieste che il sistema di Nova Assicurazioni genera quotidianamente. Il programma assegna a ciascuna pratica un'etichetta ben definita (`da_completare`, `da_rivedere` o `ordinaria`) e chiude con il resoconto numerico complessivo. 

## Requisiti

- [uv](https://docs.astral.sh/uv/) installato. Python 3.12 lo procura uv da sé.

## Come si avvia

Dalla cartella del progetto principale dove trovi il file `pyproject.toml`:

```bash
uv run python -m nova                              # analizza il file predefinito dati/lotto.json
uv run python -m nova dati/lotto_con_errori.json   # si blocca segnalando l'anomalia da corregere
```

Il codice di uscita è `0` se il lotto è stato smistato, `1` se il file non si legge o una richiesta non è valida.

## Controlli

```bash
uv run pytest
uv run ruff check .
uv run ruff format --check .
```

## Com'è fatto

| Modulo | Che cosa fa |
|---|---|
| `nova/modelli.py` | `Richiesta`, il modello Pydantic che valida al confine, e `PraticaSmistata`, la richiesta con la sua categoria |
| `nova/flussi.py` | il lettore JSONL: un generatore che consegna una riga alla volta con il suo numero |
| `nova/regole.py` | contiene le regole di smistamento, conversione degli importi (non legge da file e non stampa) |
| `nova/smistamento.py` | filtra i doppioni, applicare le regole e calcolare i totali (non legge da file e non stampa) |
| `nova/archivio.py` | legge il flusso dal file JSON e converte i formati numerici |
| `nova/__main__.py` | coordina la lettura, esegue lo smistamento, stampa i risultati e restituisce il codice d'uscita appropriato |

## La regola

| condizione, nell'ordine | categoria |
|---|---|
| importo assente (`None`) | `da_completare` |
| importo di almeno 100000 centesimi, oppure meno di 2 documenti | `da_rivedere` |
| altrimenti | `ordinaria` |

Una pratica è identificata dalla coppia `(tenant, id)`. Se arriva due volte, si conserva la prima occorrenza.
Il gestionale esporta l'importo come testo in centesimi e un importo non compilato come stringa vuota; un importo che
non è un intero o è negativo ferma la lettura del lotto.


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