import os
import shutil
import ftplib
from django.conf import settings
#from celery.contrib.methods import task
from celery import current_app
#from celery import chord, chain, group
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
            self.ftp_folder = "%s_FR_%s" % (self.prefix, self.folder)
        else:
            self.ftp_folder = "FR_%s" % (self.folder)

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

            filename = "%s_%s" % (self.prefix, file.name)

            print filename, filepath

            self.file_dict.update({ filename: filepath })

    @current_app.task(filter=task_method)
    def remove_folder(self):

        shutil.rmtree(self.local_path)
        print "removed folder: %s" % self.local_path

    @current_app.task(filter=task_method)
    def close_ftp(self):

        self.ftp.close()
        print "close ftp connection"


    @current_app.task(filter=task_method)
    def ftp_upload_file(self, filename, filepath):
        ftp = ftplib.FTP(settings.FTP_SERVER)
        ftp.login(settings.FTP_USERNAME, settings.FTP_PASSWORD)
        ftp.cwd(self.ftp_folder)
        print "starting transfer"

        with open(filepath,'rb') as f:
            ftp.storbinary("STOR " + filename, f, 1024)

        ftp.close()
        print "finished transfer"
        return True
        #self.file_dict.pop(filename)

    def create_ftp_folder(self):

        ftp = ftplib.FTP(settings.FTP_SERVER)
        ftp.login(settings.FTP_USERNAME, settings.FTP_PASSWORD)

        print "check for %s" % self.ftp_folder

        if self.ftp_folder not in ftp.nlst():
            ftp.mkd(self.ftp_folder)
            print "Had to make folder on ftp server!"

        ftp.close()



    @current_app.task(filter=task_method)
    def ftp_uploader(self):


        print "opened ftp connection"

        self.create_ftp_folder()

        for filename, filepath in self.file_dict.items():
            self.ftp_upload_file(filename, filepath)
            print filename, filepath

        #task_list.append(self.remove_folder().si())
        #task_list.append(self.close_ftp().si())


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
