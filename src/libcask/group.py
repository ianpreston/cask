import os
import os.path
import json

import libcask.container
import libcask.export
import libcask.error


class ContainerGroup(object):
    def __init__(self, data_path):
        # Directory where serialized Containers are stored
        self.data_path = data_path

        # Path to directory holding container root directories
        self.parent_root_path = '/data/cask/container'

        # Path to directory holding container pid files
        self.parent_pid_path = '/data/cask/pid'

        # Path to the directory holding container log files
        self.parent_log_path = '/data/cask/log'

        self.containers = self._deserialize_all()

    def _container_data_path(self, name):
        return os.path.join(self.data_path, name + '.json')

    def _serialize(self, container):
        container_dict = {
            'name': container.name,
            'root_path': container.root_path,
            'pid_path': container.pid_path,
            'log_path': container.log_path,
            'hostname': container.hostname,
            'ipaddr': container.ipaddr,
            'ipaddr_host': container.ipaddr_host,
            'entry_point': container.entry_point,
        }
        container_json = json.dumps(container_dict)

        with open(self._container_data_path(container.name), 'w') as f:
            f.write(container_json)

    def _deserialize(self, name):
        with open(self._container_data_path(name), 'r') as f:
            container_json = f.read()

        kwargs = json.loads(container_json)

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

    def _find_unused_addr(self, fmt, existing):
        pool = set(fmt.format(x) for x in range(1, 256))
        pool -= set(existing)
        return pool.pop()

    def _create_container(self, name):
        # Find new free IP addresses
        ipaddr = self._find_unused_addr('10.18.66.{}', [c.ipaddr for c in self.containers.values()])
        ipaddr_host = self._find_unused_addr('10.18.67.{}', [c.ipaddr_host for c in self.containers.values()])

        container = libcask.container.Container(
            name=name,
            root_path=os.path.join(self.parent_root_path, name),
            pid_path=os.path.join(self.parent_pid_path, name),
            log_path=os.path.join(self.parent_log_path, name),
            hostname=name,
            ipaddr=ipaddr,
            ipaddr_host=ipaddr_host,
            entry_point='/busybox-i686 yes',
        )

        container.create()
        return container

    def create(self, name):
        if self.containers.get(name):
            raise libcask.error.AlreadyExists('Container with that name already exists', name)

        container = self._create_container(name)

        self.containers[name] = container
        self._serialize(container)

        return container

    def export(self, name, export_filename):
        container = self.get(name)

        exp = libcask.export.ContainerExport(container, export_filename)
        exp.export_to_file()

    def importc(self, name, export_filename):
        if self.containers.get(name):
            raise libcask.error.AlreadyExists('Container with that name already exists', name)

        container = self._create_container(name)

        imp = libcask.export.ContainerExport(container, export_filename)
        imp.import_from_file()

        self.containers[container.name] = container
        self._serialize(container)

        return container

    def destroy(self, name):
        container = self.get(name)
        container.destroy()

        del self.containers[name]

        os.unlink(self._container_data_path(name))

    def get(self, name):
        try:
            return self.containers[name]
        except KeyError:
            raise libcask.error.NoSuchContainer('Container does not exist', name)
