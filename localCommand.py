import os
import shutil
from pathlib import Path

# ─────────────────────────────────────────────
# 1. NAVIGATION
# ─────────────────────────────────────────────

def get_current_dir() -> str:
    """Retourne le répertoire de travail courant."""
    return os.getcwd()


def change_dir(path: str) -> str:
    """
    Change le répertoire de travail courant.

    Args:
        path : Chemin absolu ou relatif.

    Returns:
        Nouveau répertoire courant.
    """
    os.chdir(path)
    current = os.getcwd()
    print(f"[OK] Répertoire courant : {current}")
    return current


def list_dir(path: str = ".") -> list[str]:
    """
    Liste le contenu d'un répertoire.

    Args:
        path : Répertoire à lister (défaut : courant).

    Returns:
        Liste des noms de fichiers/dossiers.
    """
    entries = os.listdir(path)
    print(f"[OK] Contenu de '{path}' ({len(entries)} entrées) :")
    for name in sorted(entries):
        full = os.path.join(path, name)
        tag = "DIR " if os.path.isdir(full) else "FILE"
        size = os.path.getsize(full) if os.path.isfile(full) else "-"
        print(f"  [{tag}] {name}  ({size} octets)" if tag == "FILE" else f"  [{tag}] {name}/")
    return entries


def tree(path: str = ".", _prefix: str = "") -> None:
    """
    Affiche récursivement l'arborescence à partir de `path`.

    Args:
        path : Racine de l'arborescence.
    """
    if _prefix == "":
        print(os.path.abspath(path))

    entries = sorted(os.scandir(path), key=lambda e: (not e.is_dir(), e.name))
    for i, entry in enumerate(entries):
        connector = "└── " if i == len(entries) - 1 else "├── "
        print(f"{_prefix}{connector}{entry.name}{'/' if entry.is_dir() else ''}")
        if entry.is_dir():
            extension = "    " if i == len(entries) - 1 else "│   "
            tree(entry.path, _prefix + extension)


# ─────────────────────────────────────────────
# 2. CRÉER
# ─────────────────────────────────────────────

def make_dir(path: str) -> None:
    """
    Crée un répertoire (y compris tous les parents manquants).

    Args:
        path : Chemin du répertoire à créer.
    """
    Path(path).mkdir(parents=True, exist_ok=True)
    print(f"[OK] Répertoire créé : {path}")


def create_file(path: str, content: str | bytes = "") -> None:
    """
    Crée un fichier avec un contenu donné.
    Crée les répertoires parents si nécessaires.

    Args:
        path    : Chemin du fichier à créer.
        content : Contenu initial (str ou bytes, vide par défaut).
    """
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    mode = "wb" if isinstance(content, bytes) else "w"
    encoding = None if isinstance(content, bytes) else "utf-8"
    with open(path, mode, encoding=encoding) as f:
        f.write(content)
    print(f"[OK] Fichier créé : {path}")


# ─────────────────────────────────────────────
# 3. MODIFIER
# ─────────────────────────────────────────────

def rename(src: str, dst: str) -> None:
    """
    Renomme un fichier ou répertoire.

    Args:
        src : Chemin source.
        dst : Nouveau nom/chemin.
    """
    Path(src).rename(dst)
    print(f"[OK] Renommé : {src} → {dst}")


def update_file(path: str, content: str | bytes) -> None:
    """
    Remplace intégralement le contenu d'un fichier existant.

    Args:
        path    : Chemin du fichier.
        content : Nouveau contenu (str ou bytes).
    """
    mode = "w"
    encoding = "utf-8"
    with open(path, mode, encoding=encoding) as f:
        f.write(content)
    print(f"[OK] Fichier mis à jour : {path}")


def append_to_file(path: str, content: str | bytes) -> None:
    """
    Ajoute du contenu à la fin d'un fichier existant.

    Args:
        path    : Chemin du fichier.
        content : Contenu à ajouter (str ou bytes).
    """
    mode = "ab" if isinstance(content, bytes) else "a"
    encoding = None if isinstance(content, bytes) else "utf-8"
    with open(path, mode, encoding=encoding) as f:
        f.write(content)
    print(f"[OK] Contenu ajouté à : {path}")


def read_file(path: str, binary: bool = False) -> str | bytes:
    """
    Lit et retourne le contenu d'un fichier.

    Args:
        path   : Chemin du fichier.
        binary : Si True, lecture en mode binaire.

    Returns:
        Contenu du fichier (str ou bytes).
    """
    mode = "rb" if binary else "r"
    encoding = None if binary else "utf-8"
    with open(path, mode, encoding=encoding) as f:
        return f.read()


# ─────────────────────────────────────────────
# 4. COPIER
# ─────────────────────────────────────────────

def copy_file(src: str, dst: str) -> None:
    """
    Copie un fichier vers une destination.
    Crée les répertoires parents de la destination si nécessaires.

    Args:
        src : Fichier source.
        dst : Fichier ou répertoire destination.
    """
    Path(dst).parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)  # copy2 préserve les métadonnées
    print(f"[OK] Fichier copié : {src} → {dst}")


def copy_dir(src: str, dst: str) -> None:
    """
    Copie récursivement un répertoire entier vers une destination.
    La destination ne doit pas déjà exister.

    Args:
        src : Répertoire source.
        dst : Répertoire destination.
    """
    shutil.copytree(src, dst, dirs_exist_ok=True)
    print(f"[OK] Répertoire copié : {src} → {dst}")


def copy(src: str, dst: str) -> None:
    """
    Copie un fichier ou un répertoire (détection automatique).

    Args:
        src : Source (fichier ou dossier).
        dst : Destination.
    """
    if os.path.isdir(src):
        copy_dir(src, dst)
    else:
        copy_file(src, dst)


# ─────────────────────────────────────────────
# 5. DÉPLACER
# ─────────────────────────────────────────────

def move(src: str, dst: str) -> None:
    """
    Déplace un fichier ou un répertoire (fonctionne entre partitions).
    Crée les répertoires parents de la destination si nécessaires.

    Args:
        src : Source (fichier ou dossier).
        dst : Destination.
    """
    Path(dst).parent.mkdir(parents=True, exist_ok=True)
    shutil.move(src, dst)
    print(f"[OK] Déplacé : {src} → {dst}")


# ─────────────────────────────────────────────
# 6. SUPPRIMER
# ─────────────────────────────────────────────

def delete_file(path: str) -> None:
    """
    Supprime un fichier.

    Args:
        path : Chemin du fichier à supprimer.
    """
    os.remove(path)
    print(f"[OK] Fichier supprimé : {path}")


def delete_dir(path: str) -> None:
    """
    Supprime récursivement un répertoire et tout son contenu.

    Args:
        path : Répertoire à supprimer.
    """
    shutil.rmtree(path)
    print(f"[OK] Répertoire supprimé : {path}")


def delete(path: str) -> None:
    """
    Supprime un fichier ou un répertoire (détection automatique).

    Args:
        path : Chemin du fichier ou répertoire à supprimer.
    """
    if os.path.isdir(path):
        delete_dir(path)
    else:
        delete_file(path)