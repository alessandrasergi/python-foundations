# i confini stabiliti inizialmente sono diventati dei test

import pytest

from nova.regole import categoria, leggi_centesimi, normalizza_oggetto


@pytest.mark.parametrize(
    ("importo", "documenti", "attesa"),
    [
        (None, 2, "da_completare"),
        (0, 2, "ordinaria"),
        (99999, 2, "ordinaria"),
        (100000, 2, "da_rivedere"),
        (4500, 1, "da_rivedere"),
        (None, 0, "da_completare"),
    ],
)
def test_categoria_sui_confini(importo, documenti, attesa):
    assert categoria(importo, documenti) == attesa

@pytest.mark.parametrize(
    "testo, atteso",
    [
        ("", None),
        ("   ", None),
        ("0,29", 29),
        ("125,50", 12550),
        ("1.250,00", 125000),
        ("45,00", 4500),  # Con la virgola per indicare gli euro
        ("12500", 12500), # Test del formato grezzo in centesimi del JSON
        ("0,00", 0),
        ("0,5", 50),
    ],
)
def test_leggi_centesimi_validi(testo, atteso):
    assert leggi_centesimi(testo) == atteso

@pytest.mark.parametrize(
    "testo_errato",
    [
        "-5",
        "-0,29",
        "abc",
        "12,34,56",
        "12a,5%  0",
        "1.250.000.00", # Errore: troppi punti separatori
    ],
)
def test_leggi_centesimi_errati(testo_errato):
    with pytest.raises(ValueError):
        leggi_centesimi(testo_errato)

def test_leggi_centesimi_vuoto_assente_zero():
    assert leggi_centesimi("") is None
    assert leggi_centesimi("0") == 0
    assert leggi_centesimi("12500") == 12500


@pytest.mark.parametrize("testo", ["dodici", "-1"])
def test_un_importo_illeggibile_o_negativo_si_rifiuta(testo):
    with pytest.raises(ValueError):
        leggi_centesimi(testo)


def test_normalizzare_due_volte_non_cambia_niente():
    una_volta = normalizza_oggetto("  Preventivo vetro  ")
    assert una_volta == "Preventivo vetro"
    assert normalizza_oggetto(una_volta) == una_volta
