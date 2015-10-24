import json
import os.path

import libcask.image
import libcask.error


class ImageGroup(object):
    def __init__(self, data_path):
        # Path to data file where serialized Images are stored
        self.data_path = data_path

        # Path to directory holding image root directories
        self.images_path = '/data/cask/image'

        self.images = dict(self._deserialize_all())

    def freeze(self, name, container):
        if self.images.get(name):
            raise libcask.error.AlreadyExists('Image already exists', name)

        image = self._create_image(name)
        image.freeze_from(container)

        self.images[image.name] = image
        self._serialize_all()
        return image

    def unfreeze(self, name, container):
        image = self.images.get(name)
        if not image:
            raise libcask.error.NoSuchImage('Image does not exist', name)

        image.unfreeze_to(container)
        return image

    def destroy(self, name):
        if not self.images.get(name):
            raise libcask.error.NoSuchImage('Image does not exist', name)

        del self.images[name]
        self._serialize_all()

    def _create_image(self, name):
        kwargs = {
            'name': name,
            'path': os.path.join(self.images_path, name),
        }
        return libcask.image.Image(**kwargs)

    def _deserialize_all(self):
        try:
            with open(self.data_path, 'r') as f:
                ser = json.loads(f.read())
        except IOError:
            return

        for image_ser in ser['images']:
            image = self._create_image(image_ser['name'])
            yield (image.name, image)

    def _serialize_image(self, image):
        return {
            'name': image.name,
        }

    def _serialize_all(self):
        images_ser = [self._serialize_image(img) for img in self.images.values()]
        images_ser = {'images': images_ser}
        images_ser = json.dumps(images_ser)

        with open(self.data_path, 'w') as f:
            f.write(images_ser)
