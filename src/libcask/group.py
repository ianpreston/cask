import json
import os
import os.path

import libcask.container
import libcask.error


class ContainerGroup(object):
    def __init__(self, data_path):
        # Directory where serialized Containers are stored
        self.data_path = data_path

        # Path to directory holding container root directories
        self.parent_root_path = '/data/cask/container'

        # Path to directory holding container pid files
        self.parent_pid_path = '/data/cask/pid'

        self.containers = self._deserialize_all()

    def _container_data_path(self, name):
        return os.path.join(self.data_path, name + '.json')

    def _serialize(self, container):
        container_dict = {
            'name': container.name,
            'hostname': container.hostname,
            'ipaddr': container.ipaddr,
            'entry_point': container.entry_point,
        }
        container_json = json.dumps(container_dict)

        with open(self._container_data_path(container.name), 'w') as f:
            f.write(container_json)

    def _deserialize(self, name):
        with open(self._container_data_path(name), 'r') as f:
            container_json = f.read()

        kwargs = json.loads(container_json)
        kwargs.update({
            'root_path': os.path.join(self.parent_root_path, name),
            'pid_path': os.path.join(self.parent_pid_path, name),
            'ipaddr_host': '10.1.1.2',
        })

        return libcask.container.Container(**kwargs)

    def _deserialize_all(self):
        # Get names of all containers
        container_names = os.listdir(self.data_path)
        container_names = [n.replace('.json', '') for n in container_names]

        all_containers = {}
        for n in container_names:
            container = self._deserialize(n)
            all_containers[n] = container
        return all_containers

    def create(self, name):
        if self.containers.get(name):
            raise libcask.error.AlreadyExists('Container with that name already exists', name)

        container = libcask.container.Container(
            name=name,
            root_path=os.path.join(self.parent_root_path, name),
            pid_path=os.path.join(self.parent_pid_path, name),
            hostname=name,
            ipaddr='10.1.1.1',
            ipaddr_host='10.1.1.2',
            entry_point='/busybox sh /entry.sh',
        )

        container.create()

        self.containers[name] = container
        self._serialize(container)

    def get(self, name):
        try:
            return self.containers[name]
        except KeyError:
            raise libcask.error.NoSuchContainer('Container does not exist', name)
