from ftplib import FTP
import hashlib
import os
from dotenv import load_dotenv




def connexion_ftp(timeout=10):
    try:
        ftp = FTP()
        ftp.connect(FTP_HOST, port=21, timeout=timeout)
        ftp.login(FTP_USER, FTP_PASSWORD)
        print("Connexion réussie")
        return ftp

    except Exception as e:
        print(f"Erreur : {e}")
        return None


# ─────────────────────────────────────────────
# 1. NAVIGATION
# ─────────────────────────────────────────────

def get_current_dir(ftp: FTP) -> str:
    """Retourne le répertoire de travail courant."""
    return ftp.pwd()


def change_dir(ftp: FTP, path: str) -> str:
    """
    Change le répertoire courant.

    Args:
        path : Chemin absolu ou relatif.

    Returns:
        Nouveau répertoire courant.
    """
    ftp.cwd(path)
    current = ftp.pwd()
    print(f"[OK] Répertoire courant : {current}")
    return current


def list_dir(ftp: FTP, path: str = ".") -> list[str]:
    """
    Liste le contenu d'un répertoire.

    Args:
        path : Répertoire à lister (défaut : courant).

    Returns:
        Liste des noms de fichiers/dossiers.
    """
    entries = []
    ftp.retrlines(f"LIST {path}", entries.append)
    print(f"[OK] Contenu de '{path}' ({len(entries)} entrées) :")
    for e in entries:
        print(f"  {e}")
    return entries


def list_dir_names(ftp: FTP, path: str = ".") -> list[str]:
    """
    Retourne uniquement les noms (sans métadonnées) d'un répertoire.

    Returns:
        Liste de noms de fichiers/dossiers.
    """
    return ftp.nlst(path)


def tree(ftp: FTP, path: str = ".", _prefix: str = "") -> None:
    """
    Affiche récursivement l'arborescence à partir de `path`.

    Args:
        path : Racine de l'arborescence.
    """
    names = ftp.nlst(path)
    for name in names:
        basename = posixpath.basename(name)
        print(f"{_prefix}├── {basename}")
        try:
            # Tenter d'entrer dans le sous-répertoire
            ftp.cwd(name)
            tree(ftp, name, _prefix + "│   ")
            ftp.cwd("..")
        except error_perm:
            pass  # C'est un fichier, pas un dossier


# ─────────────────────────────────────────────
# 2. CRÉER
# ─────────────────────────────────────────────

def make_dir(ftp: FTP, path: str) -> None:
    """
    Crée un répertoire distant (y compris les parents manquants).

    Args:
        path : Chemin du répertoire à créer.
    """
    parts = path.strip("/").split("/")
    current = "/" if path.startswith("/") else ""
    for part in parts:
        current = posixpath.join(current, part)
        try:
            ftp.mkd(current)
            print(f"[OK] Répertoire créé : {current}")
        except error_perm as e:
            if "550" not in str(e):  # 550 = déjà existant
                raise


def upload_file(ftp: FTP, local_path: str, remote_path: str) -> None:
    """
    Envoie un fichier local vers le serveur FTP.

    Args:
        local_path  : Chemin du fichier local.
        remote_path : Chemin de destination sur le serveur.
    """
    with open(local_path, "rb") as f:
        ftp.storbinary(f"STOR {remote_path}", f)
    print(f"[OK] Fichier uploadé : {local_path} → {remote_path}")


def create_file_from_content(ftp: FTP, remote_path: str, content: str | bytes) -> None:
    """
    Crée un fichier distant à partir d'un contenu en mémoire.

    Args:
        remote_path : Chemin du fichier distant à créer.
        content     : Contenu du fichier (str ou bytes).
    """
    if isinstance(content, str):
        content = content.encode("utf-8")
    buf = io.BytesIO(content)
    ftp.storbinary(f"STOR {remote_path}", buf)
    print(f"[OK] Fichier créé : {remote_path}")


# ─────────────────────────────────────────────
# 3. MODIFIER
# ─────────────────────────────────────────────

def rename(ftp: FTP, old_path: str, new_path: str) -> None:
    """
    Renomme (ou déplace) un fichier ou répertoire.

    Args:
        old_path : Chemin source.
        new_path : Nouveau chemin.
    """
    ftp.rename(old_path, new_path)
    print(f"[OK] Renommé : {old_path} → {new_path}")


def update_file(ftp: FTP, remote_path: str, new_content: str | bytes) -> None:
    """
    Remplace le contenu d'un fichier distant existant.

    Args:
        remote_path : Chemin du fichier sur le serveur.
        new_content : Nouveau contenu (str ou bytes).
    """
    create_file_from_content(ftp, remote_path, new_content)
    print(f"[OK] Fichier mis à jour : {remote_path}")


def append_to_file(ftp: FTP, remote_path: str, content: str | bytes) -> None:
    """
    Ajoute du contenu à la fin d'un fichier distant existant.

    Args:
        remote_path : Chemin du fichier distant.
        content     : Contenu à ajouter.
    """
    if isinstance(content, str):
        content = content.encode("utf-8")
    buf = io.BytesIO(content)
    ftp.storbinary(f"APPE {remote_path}", buf)
    print(f"[OK] Contenu ajouté à : {remote_path}")


# ─────────────────────────────────────────────
# 4. COPIER
# ─────────────────────────────────────────────

def _is_dir(ftp: FTP, path: str) -> bool:
    """Détermine si `path` est un répertoire distant."""
    original = ftp.pwd()
    try:
        ftp.cwd(path)
        ftp.cwd(original)
        return True
    except error_perm:
        return False


def _download_to_memory(ftp: FTP, remote_path: str) -> bytes:
    """Télécharge un fichier distant en mémoire."""
    buf = io.BytesIO()
    ftp.retrbinary(f"RETR {remote_path}", buf.write)
    return buf.getvalue()


def copy_file(ftp: FTP, src: str, dst: str) -> None:
    """
    Copie un fichier distant vers un autre emplacement distant.

    Args:
        src : Chemin source.
        dst : Chemin destination.
    """
    data = _download_to_memory(ftp, src)
    create_file_from_content(ftp, dst, data)
    print(f"[OK] Fichier copié : {src} → {dst}")


def copy_dir(ftp: FTP, src: str, dst: str) -> None:
    """
    Copie récursivement un répertoire distant vers une autre destination.

    Args:
        src : Répertoire source.
        dst : Répertoire destination (sera créé si nécessaire).
    """
    make_dir(ftp, dst)
    for name in ftp.nlst(src):
        basename = posixpath.basename(name)
        src_path = posixpath.join(src, basename)
        dst_path = posixpath.join(dst, basename)
        if _is_dir(ftp, src_path):
            copy_dir(ftp, src_path, dst_path)
        else:
            copy_file(ftp, src_path, dst_path)
    print(f"[OK] Répertoire copié : {src} → {dst}")


# ─────────────────────────────────────────────
# 5. DÉPLACER
# ─────────────────────────────────────────────

def move_file(ftp: FTP, src: str, dst: str) -> None:
    """
    Déplace un fichier distant (rename FTP).

    Args:
        src : Chemin source.
        dst : Chemin destination.
    """
    rename(ftp, src, dst)
    print(f"[OK] Fichier déplacé : {src} → {dst}")


def move_dir(ftp: FTP, src: str, dst: str) -> None:
    """
    Déplace un répertoire distant.
    Utilise rename si possible, sinon effectue une copie + suppression.

    Args:
        src : Répertoire source.
        dst : Répertoire destination.
    """
    try:
        rename(ftp, src, dst)
        print(f"[OK] Répertoire déplacé (rename) : {src} → {dst}")
    except error_perm:
        # Cross-device ou non supporté : copie puis suppression
        copy_dir(ftp, src, dst)
        delete_dir(ftp, src)
        print(f"[OK] Répertoire déplacé (copy+delete) : {src} → {dst}")


# ─────────────────────────────────────────────
# 6. SUPPRIMER
# ─────────────────────────────────────────────

def delete_file(ftp: FTP, remote_path: str) -> None:
    """
    Supprime un fichier distant.

    Args:
        remote_path : Chemin du fichier à supprimer.
    """
    ftp.delete(remote_path)
    print(f"[OK] Fichier supprimé : {remote_path}")


def delete_dir(ftp: FTP, path: str) -> None:
    """
    Supprime récursivement un répertoire et tout son contenu.

    Args:
        path : Répertoire à supprimer.
    """
    for name in ftp.nlst(path):
        basename = posixpath.basename(name)
        entry = posixpath.join(path, basename)
        if _is_dir(ftp, entry):
            delete_dir(ftp, entry)
        else:
            delete_file(ftp, entry)
    ftp.rmd(path)
    print(f"[OK] Répertoire supprimé : {path}")


def delete(ftp: FTP, path: str) -> None:
    """
    Supprime un fichier ou un répertoire (avec tout son contenu).

    Args:
        path : Chemin du fichier ou répertoire à supprimer.
    """
    if _is_dir(ftp, path):
        delete_dir(ftp, path)
    else:
        delete_file(ftp, path)


load_dotenv()
FTP_HOST = os.getenv("FTP_HOST")
FTP_USER = os.getenv("FTP_USER")
FTP_PASSWORD = os.getenv("FTP_PASSWORD")
print("Lancement du programme")
ftp=connexion_ftp()
prompt=input("=>")
match prompt:
    case "pwd":
        print(get_current_dir(ftp))







