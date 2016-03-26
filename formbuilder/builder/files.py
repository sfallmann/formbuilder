import os, ftplib
from django.conf import settings
from .tasks import upload_ftp


UPLOAD_FOLDER = os.path.join(os.getcwd(), "uploads")


def process_files(files, folder, prefix, ftp=False):

    print "prefix %s" % prefix

    if prefix:
        ftp_folder = "%s_FR_%s" % (prefix, folder)
    else:
        ftp_folder = "FR_%s" % (folder)

    local_path = os.path.join(UPLOAD_FOLDER, ("%s/" % ftp_folder))

    file_dict = {}

    if make_folder(local_path):
        for file in files:

            saved_filepath = handle_uploaded_file(file, local_path)

            if saved_filepath:

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
