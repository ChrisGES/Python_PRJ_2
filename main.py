from ftplib import FTP

def connexion_ftp(user, passwd, timeout=10):
    try:
        ftp = FTP()
        ftp.connect("127.0.0.1", port=21, timeout=timeout)
        ftp.login(user, passwd)
        print("Connexion réussie")
        return ftp

    except Exception as e:
        print(f"Erreur : {e}")
        return None

print("Lancement du programme")
input("=>")
connexion_ftp("FTP1","wxcvbn,;:!")




