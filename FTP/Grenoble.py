import os
import shutil

# 1) login FTP
# 2) Navigate in Grenoble folder 
# 3) Download X file/folder
# 4) Logout

def pwd():
    print(os.getcwd())

pwd()
os.chdir("grenoble_folder")
pwd()
os.chdir("..")

# simulation de téléchargement
src = "grenoble_folder/test.txt"
dst = "home_test/test.txt"

shutil.copyfile(src, dst)

# fin du scenario - Admin Grenoble

