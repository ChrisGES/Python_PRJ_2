"""
backup_friday.py — Sauvegarde FTP automatique chaque vendredi à 20h00
Dépendances standard : ftplib, os, io, posixpath, time, datetime, logging, threading
"""

import os
import time
import logging
import posixpath
import threading
from asyncio import wait
from datetime import datetime
from ftplib import FTP, error_perm


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  [%(levelname)s]  %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.FileHandler("backup_friday.log", encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
log = logging.getLogger(__name__)


# ─────────────────────────────────────────────
# HELPERS FTP
# ─────────────────────────────────────────────

def connect(host: str, user: str, password: str, port: int = 21) -> FTP:
    """Ouvre et retourne une connexion FTP."""
    ftp = FTP(host,user,password)
    ftp.encoding = "utf-8"
    return ftp


def ftp_make_dir(ftp: FTP, remote_path: str) -> None:
    """Crée un répertoire distant avec tous ses parents (ignore si déjà existant)."""
    parts = remote_path.strip("/").split("/")
    current = "/" if remote_path.startswith("/") else ""
    for part in parts:
        current = posixpath.join(current, part)
        try:
            ftp.mkd(current)
        except error_perm as e:
            if "550" not in str(e):
                raise


def upload_dir(ftp: FTP, local_dir: str, remote_dir: str) -> tuple[int, int]:
    """
    Upload récursif d'un répertoire local vers le serveur FTP.

    Returns:
        (nb_fichiers_uploadés, nb_erreurs)
    """
    ftp_make_dir(ftp, remote_dir)
    uploaded, errors = 0, 0

    for entry in os.scandir(local_dir):
        remote_path = posixpath.join(remote_dir, entry.name)
        if entry.is_dir(follow_symlinks=False):
            u, e = upload_dir(ftp, entry.path, remote_path)
            uploaded += u
            errors += e
        else:
            try:
                with open(entry.path, "rb") as f:
                    ftp.storbinary(f"STOR {remote_path}", f)
                log.debug(f"  Uploadé : {entry.path} → {remote_path}")
                uploaded += 1
            except Exception as exc:
                log.warning(f"  Échec upload '{entry.path}' : {exc}")
                errors += 1

    return uploaded, errors

def backup_to_ftp(
        local_dir: str,
        ftp_host: str,
        ftp_user: str,
        ftp_password: str,
        remote_base_dir: str,
        ftp_port: int,
) -> None:
    """Copie le répertoire local vers le serveur FTP avec un dossier horodaté."""
    if not os.path.isdir(local_dir):
        log.error(f"Répertoire source introuvable : {local_dir}")
        return

    folder_name = os.path.basename(os.path.abspath(local_dir))
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    remote_dir = posixpath.join(remote_base_dir, f"{folder_name}_{stamp}")

    log.info("═══ Début de la sauvegarde ═══")
    log.info(f"  Source      : {os.path.abspath(local_dir)}")
    log.info(f"  Destination : {ftp_host}:{remote_dir}")

    try:
        ftp = connect(ftp_host, ftp_user, ftp_password)
        uploaded, errors = upload_dir(ftp, local_dir, remote_dir)
        ftp.quit()

        if errors == 0:
            log.info(f"  Résultat    : {uploaded} fichier(s) uploadé(s) — aucune erreur ✓")
        else:
            log.warning(f"  Résultat    : {uploaded} uploadé(s), {errors} erreur(s)")

    except Exception as exc:
        log.error(f"Erreur de connexion/upload : {exc}")

    log.info("═══ Sauvegarde terminée ═══")


# ─────────────────────────────────────────────
# PLANIFICATEUR
# ─────────────────────────────────────────────




def scheduler_loop(
        local_dir: str,
        ftp_host: str,
        ftp_user: str,
        ftp_password: str,
        remote_base_dir: str,
        ftp_port: int
) -> None:
    """Boucle interne du thread : attend chaque vendredi 20h puis déclenche la sauvegarde."""
    log.info("Planificateur démarré — sauvegarde chaque vendredi à 20h00")

    while True:
        date = datetime.now()
        log.info(f"Datetime: {date.strftime('%d%m%Y - %HH%Mm%Ss')}")
        if date.weekday() == 4 :
            if date.hour==20:
                backup_to_ftp(local_dir, ftp_host, ftp_user, ftp_password,
                              remote_base_dir, ftp_port)
                time.sleep(3601)  # évite un double déclenchement dans la même minute

            else:
                time.sleep(3601)
        else:
            time.sleep(3600*24)



def start_friday_backup_thread(
        local_dir: str,
        ftp_host: str,
        ftp_user: str,
        ftp_password: str,
        remote_base_dir: str = "/backup",
        ftp_port: int = 21,
) -> threading.Thread:
    """
    Lance en arrière-plan un thread qui copie `local_dir` vers le serveur FTP
    chaque vendredi à 20h00.

    Args:
        local_dir       : Répertoire local à sauvegarder.
        ftp_host        : Adresse du serveur FTP.
        ftp_user        : Nom d'utilisateur FTP.
        ftp_password    : Mot de passe FTP.
        remote_base_dir : Répertoire racine de destination sur le serveur FTP.
        ftp_port        : Port FTP (défaut 21).

    Returns:
        Le thread daemon lancé.
    """
    thread = threading.Thread(
        target=scheduler_loop,  # <- On passe la fonction, pas le résultat
        args=(local_dir, ftp_host, ftp_user, ftp_password, remote_base_dir, ftp_port),
        daemon=True,
        name="FridayBackup",
    )
    thread.start()
    log.info(f"Thread '{thread.name}' démarré (id={thread.ident})")
    return thread


