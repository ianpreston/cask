import os
import shutil
import subprocess

import libcask.error


class Image(object):
    def __init__(self, name, path):
        self.name = name
        self.path = path

    def freeze_from(self, container):
        shutil.copytree(container.root_path, self.path, symlinks=True)

    def unfreeze_to(self, container):
        shutil.rmtree(container.root_path)
        shutil.copytree(self.path, container.root_path, symlinks=True)

    def export_to(self, export_filename):
        subprocess.check_call(['tar', '-C', self.path + '/', '-cvzf', export_filename, '.'])

    def import_from(self, import_filename):
        try:
            os.mkdir(self.path)
            subprocess.check_call(['tar', '-C', self.path, '-xvf', import_filename])
        except subprocess.CalledProcessError, e:
            os.rmdir(self.path)
            raise libcask.error.InvalidImage('Extracting image failed. Ensure the file exists and is a valid image archive', e)
