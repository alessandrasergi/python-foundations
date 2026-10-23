import asyncio
import time


async def attesa(nome: str, secondi: float, eventi: list[str]) -> str:
    eventi.append(f"{nome}:start")
    await asyncio.sleep(secondi)
    eventi.append(f"{nome}:end")
    return nome


async def principale() -> None:
    eventi: list[str] = []
    valori = await asyncio.gather(attesa("A", 0.04, eventi), attesa("B", 0.02, eventi))
    print(valori, eventi)
    inizio = time.perf_counter()
    await asyncio.gather(*(asyncio.sleep(0.05) for _ in range(10)))
    print(f"dieci attese insieme: {time.perf_counter() - inizio:.2f} s")


asyncio.run(principale())