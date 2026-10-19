#Esercizi: copia superficiale e copia profonda di un dizionario con lista

# Prima parte: copia superficiale
originale = {"id": "N-001", "documenti": ["preventivo"]}
copia = originale.copy()
copia["documenti"].append("foto")
print("Esercizio 1 - superficiale ORIGINALE:", originale)
print("Esercizio 1 - superficiale COPIA:", copia)

# Seconda parte: copia profonda
originale = {"id": "N-001", "documenti": ["preventivo"]}
copia = originale.copy()
copia["documenti"] = originale["documenti"].copy()
copia["documenti"].append("foto")
print("Esercizio 2 - profonda ORIGINALE:", originale)
print("Esercizio 2 - profonda COPIA:", copia)

# Terza parte: verifica
altro_nome = originale
print("Esercizio 3 - stesso oggetto?", altro_nome is originale)
print("Esercizio 3 - stessa lista?", copia["documenti"] is originale["documenti"])

