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

        # Path to the directory holding container log files
        self.parent_log_path = '/data/cask/log'

        self.containers = self._deserialize_all()

    def _container_data_path(self, name):
        return os.path.join(self.data_path, name + '.json')

    def _serialize(self, container):
        container_dict = {
            'name': container.name,
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
        kwargs.update({
            'root_path': os.path.join(self.parent_root_path, name),
            'pid_path': os.path.join(self.parent_pid_path, name),
            'log_path': os.path.join(self.parent_log_path, name),
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

    def _find_unused_addr(self, fmt, existing):
        pool = set(fmt.format(x) for x in range(1, 256))
        pool -= set(existing)
        return pool.pop()

    def create(self, name):
        if self.containers.get(name):
            raise libcask.error.AlreadyExists('Container with that name already exists', name)

        # Find new free IP addresses
        ipaddr = self._find_unused_addr('10.18.66.{}', [c.ipaddr for c in self.containers.values()])
        ipaddr_host = self._find_unused_addr('10.18.67.{}', [c.ipaddr_host for c in self.containers.values()])

        container = libcask.container.Container(
            name=name,
            root_path=os.path.join(self.parent_root_path, name),
            pid_path=os.path.join(self.parent_pid_path, name),
            hostname=name,
            ipaddr=ipaddr,
            ipaddr_host=ipaddr_host,
            entry_point='/busybox sh /entry.sh',
        )

        container.create()

        self.containers[name] = container
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
