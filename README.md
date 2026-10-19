# Nova-Smistamento (Estensione 3: Richieste dal Portale)

## smista.py
gestisce i duplicati tramite la tupla (tenat,id), pulisce gli oggetti senza alterare il lotto originale, applica le regole di smistamento assegnando la categoria e produce un riepilogo finale con i conteggi.

## smista-dal-portale.py
è la versione con le modifiche per l'estensione numero 3 ovvero quella di leggere dati dal portale online

## lotto.py 
sono i dati in input che vengono importati per lo smistamento in smista.py

## Come avviarlo

bash - uv run python smista.py

## Strada scelta e difesa

Si è optato per l'estensione 3, quindi quella di distinguere rigorosamente tra campi mancanti nel portale (segnalati a Ivan come anomalia tecnica) e valori None (pratiche da far completare al cliente).

Evitando l'uso indiscriminato di .get() sui dati obbligatori per impedire che errori strutturali del portale finissero senza volerlo tra le pratiche ordinarie.

Inseriti 3 controlli preventivi obbligatori (tenant/id, importo, documenti) prima di applicare la logica di categoria.

## Riepilogo (Delta prima e dopo)

Primo report: 
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

## Politica sui duplicati

Teniamo la prima occorrenza e scartiamo la seconda.
Ciò che arriva per primo fa fede cronologicamente; eventuali reinvii successivi senza modifiche strutturali sono considerati duplicati innocui da ignorare per non alterare la sequenza originale di elaborazione.

## Revisione del codice scritto con l'AI
- Evitato l'uso di if importo: per non confondere l'importo a zero con un campo mancante.
- Utilizzato richiesta.copy() per preservare intatto il lotto originale in ingresso.
- Evitato .get() silenzioso sui campi obbligatori per fare emergere i KeyError.
- Gestione sicura delle stringhe nei documenti tramite int() protetto da try/except.


## Prova del collega
Tempo impiegato: 2 minuti.
Nessun blocco eseguendo il comando da terminale pulito.

## Riepilogo da code bluprint:



