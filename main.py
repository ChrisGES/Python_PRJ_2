import time
from operator import is_none

from localCommand import *
from backup import *
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


load_dotenv()
FTP_HOST = os.getenv("FTP_HOST")
FTP_PORT = os.getenv("FTP_PORT")
FTP_USER = os.getenv("FTP_USER")
FTP_PASSWORD = os.getenv("FTP_PASSWORD")
LOCAL_DIR = os.getenv("LOCAL_DIR")
REMOTE_DIR = os.getenv("REMOTE_DIR")


print("Lancement du programme")
start_friday_backup_thread(LOCAL_DIR,FTP_HOST,FTP_USER,FTP_PASSWORD,REMOTE_DIR,int(FTP_PORT))
time.sleep(1)
while(1):
    prompt=input(FTP_USER+"=>")
    prompt=prompt.split()

    if prompt.__len__()>0 :
        match prompt[0]:
            case "pwd":
                print(get_current_dir())
            case "cd":
                if prompt.__len__()>1:
                    change_dir(prompt[1])
            case "ls":
                if prompt.__len__()>1:
                    list_dir(prompt[1])
                else:
                    list_dir(".")
            case "tree":
                if prompt.__len__()>1:
                    tree(prompt[1])
                else:
                    tree(".")
            case "mkdir":
                if prompt.__len__()>1:
                    make_dir(prompt[1])
                else:
                    print("Il faut indiquer un nom")
            case "mkfile":
                if prompt.__len__()>1:
                    if prompt.__len__()>2:
                        create_file(prompt[1],prompt[2])
                    else:
                        create_file(prompt[1])
                else:
                    print("Il faut indiquer un nom")

            case "mv"|"rename":
                if prompt.__len__() > 1:
                    if prompt.__len__() > 2:
                        rename(prompt[1], prompt[2])
                    else:
                        print("Indiquer le nouveau nom du fichier")
                else:
                    print("Il faut indiquer un nom")

            case "writefile":
                if prompt.__len__() > 1:
                    if prompt.__len__() > 2:
                        update_file(prompt[1], prompt[2])
                    else:
                        print("Indiquer le nouveau contenu du fichier")
                else:
                    print("Il faut indiquer un fichier à modifier")

            case "appendfile":
                if prompt.__len__() > 1:
                    if prompt.__len__() > 2:
                        append_to_file(prompt[1], prompt[2])
                    else:
                        print("Indiquer le contenu à ajouter au fichier")
                else:
                    print("Il faut indiquer un fichier à modifier")

            case "cat" | "readfile":
                if prompt.__len__() > 1:
                   print(read_file(prompt[1]))
                else:
                    print("Il faut indiquer un fichier à modifier")

            case "copy":
                if prompt.__len__()>1:
                    if prompt.__len__()>2:
                        copy(prompt[1],prompt[2])
                    else:
                        print("Indiquer la destination")
                else:
                    print("Indiquer la source")
            case "delete" | "rm":
                if prompt.__len__()>1:
                    delete(prompt[1])
            case "manualbackup":
                backup_to_ftp(LOCAL_DIR,FTP_HOST,FTP_USER,FTP_PASSWORD,REMOTE_DIR,int(FTP_PORT))

            case "quit"|"q":
                print("Le programme va se fermer...")
                break












