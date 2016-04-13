import os
import shutil
import ftplib
from django.conf import settings
#from celery.contrib.methods import task
from celery import current_app
from celery.contrib.methods import task_method

#from formbuilder.celery import app

#from .tasks import upload_ftp


class FileProcessor(object):

    def __init__(self, folder, prefix=None, ftp_transfer=False):

        self.folder = folder
        self.prefix = prefix
        self.ftp_transfer = ftp_transfer
        self.file_dict = {}
        self.local_path = ""


    def process_files(self, files):

        print "prefix %s" % self.prefix

        if self.prefix:
            self.ftp_folder = "%s_PBMFR_%s" % (self.prefix, self.folder)
        else:
            self.ftp_folder = "PBMFR_%s" % (self.folder)

        self.local_path = os.path.join(settings.UPLOAD_FOLDER, ("%s/" % self.ftp_folder))

        if self.make_folder():
            self.save_files(files)

            if self.ftp_transfer:
                self.ftp_uploader.delay()

    def make_folder(self):

        if not os.path.exists(self.local_path):
            try:
                os.makedirs(self.local_path)

            except OSError:
                #  TODO:  Add logging
                #  "Error on creating file folder"
                return False

        return True

    def save_files(self, files):

        for file in files:


            filepath = os.path.join(self.local_path, file._name)

            with open(filepath, 'wb+') as destination:
                for chunk in file.chunks():
                    destination.write(chunk)

            if self.prefix:
                filename = "%s_%s" % (self.prefix, file.name)
            else:
                filename = file.name

            print filename, filepath

            self.file_dict.update({ filename: filepath })

    def remove_folder(self):

        shutil.rmtree(self.local_path)
        print "removed folder: %s" % self.local_path


    @current_app.task(
        filter=task_method,
        time_limit=900,
        max_retries=3,
        default_retry_delay=900,
    )
    def ftp_uploader(self):

        try:
            print "open ftp connection"

            ftp = ftplib.FTP(settings.FTP_SERVER)
            ftp.login(settings.FTP_USERNAME, settings.FTP_PASSWORD)

            print "check for %s" % self.ftp_folder

            if self.ftp_folder not in ftp.nlst():
                ftp.mkd(self.ftp_folder)
                print "Created %s on ftp server" % self.ftp_folder

            print "Changing working directory to %s" % self.ftp_folder

            ftp.cwd(self.ftp_folder)

            for filename, filepath in self.file_dict.items():

                print "Starting transfer of %s/%s" % (filename, filepath)

                with open(filepath,'rb') as f:
                    ftp.storbinary("STOR " + filename, f, 1024)

                print "Completed transfer of %s/%s" % (filename, filepath)
                self.file_dict.pop(filename)

            ftp.close()

            self.remove_folder()

        except (socket.error, IOError, ftplib.error_reply, ftplib.error_temp) as exc:
            raise self.retry(exc=exc)




