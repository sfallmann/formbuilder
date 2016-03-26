import os
import shutil
import ftplib
from django.conf import settings
from celery.decorators import task


@task(name="remove_folder")
def remove_folder(folder_path):

    try:
        shutil.rmtree(folder_path)
        return True
    except:
        return False


@task(name="upload_ftp")
def upload_ftp(ftp_folder, file_dict, local_path):


    ftp = ftplib.FTP(settings.FTP_SERVER)
    ftp.login(settings.FTP_USERNAME, settings.FTP_PASSWORD)

    if ftp_folder not in ftp.nlst():
        ftp.mkd(ftp_folder)
        ftp.cwd(ftp_folder)

    for k,v in file_dict.items():

        filename = k
        filepath = v


        with open(filepath,'rb') as f:
            ftp.storbinary("STOR " + filename, f, 1024)

    remove_folder.delay(local_path)
    ftp.close()

    return True

