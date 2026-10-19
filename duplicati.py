visti = set()
smistate = []
for richiesta in LOTTO:
    chiave = (richiesta["tenant"], richiesta["id"])
    if chiave in visti:
        continue
    visti.add(chiave)
    smistate.append(richiesta.copy())