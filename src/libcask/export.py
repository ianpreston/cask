import os
import os.path
import json
import shutil
import tempfile
import subprocess


class ContainerExport(object):
    EXPORTED_ATTRIBUTES = ['hostname', 'entry_point']

    def __init__(self, container, filename):
        # Path to the the archive directory that the export .tar.gz will either
        # be created from, or extracted to.
        self.archive_path = tempfile.mkdtemp()

        # Container that will be imported to/exported from
        self.container = container

        # Filename of the .tar.gz archive that will be created/extracted
        self.filename = filename

    def export_to_file(self):
        self._export_attributes()
        self._export_root()
        self._create_archive()

    def import_from_file(self):
        self._extract_archive()
        self._import_attributes()
        self._import_root()

    def cleanup(self):
        shutil.rmtree(self.archive_path)

    def __del__(self):
        self.cleanup()

    @property
    def attributes_path(self):
        return os.path.join(self.archive_path, 'attributes.json')

    @property
    def root_path(self):
        return os.path.join(self.archive_path, 'root')

    def _create_archive(self):
        subprocess.check_call(['tar', '-C', self.archive_path + '/', '-cvzf', self.filename, '.'])

    def _extract_archive(self):
        subprocess.check_call(['tar', '-C', self.archive_path, '-xvf', self.filename])

    def _export_attributes(self):
        with open(self.attributes_path, 'w') as f:
            f.write(json.dumps({
                attr: self.container.__dict__[attr]
                for attr in self.EXPORTED_ATTRIBUTES
            }))

    def _import_attributes(self):
        with open(self.attributes_path, 'r') as f:
            attributes = json.loads(f.read())

        for attr in self.EXPORTED_ATTRIBUTES:
            self.container.__dict__[attr] = attributes[attr]

    def _export_root(self):
        shutil.copytree(self.container.root_path, self.root_path, symlinks=True)

    def _import_root(self):
        os.rmdir(self.container.root_path)
        shutil.copytree(self.root_path, self.container.root_path, symlinks=True)
