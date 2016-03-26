import ftplib
from django.conf import settings

def process_files(files):



    ftp = ftplib.FTP(settings.FTP_SERVER)
    ftp.login(settings.FTP_USERNAME, settings.FTP_PASSWORD)

    for file in files:

        upload_ftp(ftp, file)


def upload_ftp(ftp, file):

    ftp.storbinary("STOR " + file.name, file, 1024)
    file.close()
