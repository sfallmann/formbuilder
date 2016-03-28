import os
import shutil
import ftplib
from django.conf import settings
from celery.contrib.methods import task
#from formbuilder.celery import app

#from .tasks import upload_ftp


class FileProcessor(object):

    def __init__(self, folder, prefix=None, ftp=False):


        self.folder = folder
        self.prefix = prefix
        self.ftp = ftp
        self.file_dict = {}
        self.local_path = ""

    def process_files(self, files):

        print "prefix %s" % self.prefix

        if self.prefix:
            self.ftp_folder = "%s_FR_%s" % (self.prefix, self.folder)
        else:
            self.ftp_folder = "FR_%s" % (self.folder)

        self.local_path = os.path.join(settings.UPLOAD_FOLDER, ("%s/" % self.ftp_folder))

        if self.make_folder():
            self.handle_uploaded_files(files)

            if self.ftp:
                self.upload_ftp.delay()


    def make_folder(self):

        if not os.path.exists(self.local_path):
            try:
                os.makedirs(self.local_path)

            except OSError:
                #  TODO:  Add logging
                #  "Error on creating file folder"
                return False

        return True

    def handle_uploaded_files(self, files):

        for file in files:


            filepath = os.path.join(self.local_path, file._name)

            with open(filepath, 'wb+') as destination:
                for chunk in file.chunks():
                    destination.write(chunk)

            filename = "%s_%s" % (self.prefix, file.name)

            print filename, filepath

            self.file_dict.update({ filename: filepath })


    def remove_folder(self):

        shutil.rmtree(self.local_path)


    @task()
    def upload_ftp(self):

        ftp = ftplib.FTP(settings.FTP_SERVER)
        ftp.login(settings.FTP_USERNAME, settings.FTP_PASSWORD)

        print "opened ftp connection"

        if self.ftp_folder not in ftp.nlst():
            ftp.mkd(self.ftp_folder)
            ftp.cwd(self.ftp_folder)

        for k,v in self.file_dict.items():

            filename = k
            filepath = v

            print "starting transfer: %s" % filename

            with open(filepath,'rb') as f:
                ftp.storbinary("STOR " + filename, f, 1024)

            print "finished transfer: %s" % filename

            self.file_dict.pop(k)


        self.remove_folder()

        print "removed folder: %s" % self.local_path

        ftp.close()

        print "close ftp connection"
        if self.file_dict:
            return "The following files were not transfered: %s" % self.file_dict.keys()
        else:
            return "All files transferred successfully"

'''
def process_files(files, folder, prefix, ftp=False):

    print "prefix %s" % prefix

    if prefix:
        ftp_folder = "%s_FR_%s" % (prefix, folder)
    else:
        ftp_folder = "FR_%s" % (folder)

    local_path = os.path.join(settings.UPLOAD_FOLDER, ("%s/" % ftp_folder))

    file_dict = {}

    if make_folder(local_path):
        for file in files:

            new_filepath = handle_uploaded_file(file, local_path)

            if new_filepath:

                filename = "%s_%s" % (prefix, file.name)

                file_dict.update({ filename: saved_filepath })

        if ftp:
            upload_ftp.delay(ftp_folder, file_dict, local_path)


def handle_uploaded_file(f, path):

    filepath = os.path.join(path, f._name)

    try:
        with open(filepath, 'wb+') as destination:
            for chunk in f.chunks():
                destination.write(chunk)

        return filepath
    except:
        #TODO logging and specific exceptions
        return None


def make_folder(folder):

    if not os.path.exists(folder):
        try:
            os.makedirs(folder)

        except OSError:

            #  TODO:  Add logging
            #  "Error on creating file folder"
            return False

    return True
'''
