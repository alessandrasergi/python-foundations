"""Le forme dei dati: la richiesta validata al confine e la pratica smistata."""

from dataclasses import dataclass, field
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class Richiesta(BaseModel):
    """Una richiesta come il programma la accetta: ogni campo dichiarato, nessuna conversione permissiva."""

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    id: str = Field(min_length=1)
    tenant: str = Field(min_length=1)
    oggetto: str = Field(min_length=1)
    importo_centesimi: int | None = Field(ge=0)
    documenti: int = Field(ge=0)

    def chiave(self) -> tuple[str, str]:
        """L'identità della pratica: l'organizzazione e l'identificativo, insieme."""
        return (self.tenant, self.id)

    def __getitem__(self, key: str) -> Any:
        """Permette l'accesso ai campi tramite parentesi quadre per compatibilità con i test."""
        return getattr(self, key)


@dataclass(frozen=True)
class PraticaSmistata:
    """Una richiesta con la categoria che la regola le ha assegnato."""

    richiesta: Richiesta
    categoria: str

    def __getitem__(self, key: str) -> Any:
        """Permette l'accesso ai campi della richiesta tramite parentesi quadre nei test."""
        return getattr(self.richiesta, key)

#estensione 3 G3
@dataclass(frozen=True)
class Riepilogo:
    """Il riepilogo delle pratiche smistate, con conteggi, totali e quote percentuali."""

    conteggi: dict[str, int] = field(
        default_factory=lambda: {"da_completare": 0, "da_rivedere": 0, "ordinaria": 0}
    )

    @property
    def totale(self) -> int:
        """Il numero totale delle pratiche elaborate."""
        return sum(self.conteggi.values())

    def quota(self, categoria: str) -> float:
        """La quota di una categoria sul totale, gestendo in sicurezza la divisione per zero."""
        tot = self.totale
        if tot == 0:
            return 0.0
        return self.conteggi.get(categoria, 0) / tot

    def __str__(self) -> str:
        """Rappresentazione testuale pulita e pronta per la stampa."""
        dettagli = [
            f"  - {cat}: {num} ({self.quota(cat) * 100:.1f}%)"
            for cat, num in self.conteggi.items()
        ]
        return f"Totale pratiche: {self.totale}\n" + "\n".join(dettagli)