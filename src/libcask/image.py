import shutil


class Image(object):
    def __init__(self, name, path):
        self.name = name
        self.path = path

    def freeze_from(self, container):
        shutil.copytree(container.root_path, self.path, symlinks=True)

    def unfreeze_to(self, container):
        shutil.rmtree(container.root_path)
        shutil.copytree(self.path, container.root_path, symlinks=True)
