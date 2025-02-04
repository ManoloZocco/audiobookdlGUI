import importlib.resources
from typing import Sequence
import shutil

def levenstein_distance(a: str, b: str) -> int:
    """
    Calcola la distanza di Levenshtein tra due stringhe.
    https://en.wikipedia.org/wiki/Levenshtein_distance
    """
    if len(a) == 0:
        return len(b)
    if len(b) == 0:
        return len(a)
    if a[0] == b[0]:
        return levenstein_distance(a[1:], b[1:])
    return 1 + min(
        levenstein_distance(a, b[1:]),   # Inserimento
        levenstein_distance(a[1:], b),     # Cancellazione
        levenstein_distance(a[1:], b[1:])    # Sostituzione
    )

def nearest_string(input: str, lst: Sequence[str]) -> str:
    """
    Ritorna l'elemento più vicino in `lst` a `input`
    basato sulla distanza di Levenshtein.
    """
    return sorted(lst, key=lambda x: levenstein_distance(input, x))[0]

def read_asset_file(path: str) -> str:
    """
    Legge il file asset specificato nel percorso.
    """
    return importlib.resources.files("audiobookdl").joinpath(path).read_text(encoding="utf8")

def program_in_path(program: str) -> bool:
    """
    Verifica se il programma è presente nel PATH del sistema.
    """
    return shutil.which(program) is not None

# Eliminata la funzione transform_storytel_url per rimuovere il controllo e la trasformazione degli URL.
