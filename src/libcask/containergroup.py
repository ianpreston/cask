import os
import os.path
import json

import libcask.container
import libcask.error


class ContainerGroup(object):
    def __init__(self, data_path):
        # Path to data file where serialized Containers are stored
        self.data_path = data_path

        # Path to directory holding container root directories
        self.parent_root_path = '/data/cask/container'

        # Path to directory holding container pid files
        self.parent_pid_path = '/data/cask/pid'

        # Path to the directory holding container log files
        self.parent_log_path = '/data/cask/log'

        self.containers = dict(self._deserialize_all())

    def create(self, name):
        if self.containers.get(name):
            raise libcask.error.AlreadyExists('Container with that name already exists', name)

        container = self._create_container(name)

        self.containers[name] = container
        self._serialize_all()

        return container

    def destroy(self, name):
        container = self.get(name)
        container.destroy()

        del self.containers[name]
        self._serialize_all()

    def get(self, name):
        try:
            return self.containers[name]
        except KeyError:
            raise libcask.error.NoSuchContainer('Container does not exist', name)

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

    def _find_unused_addr(self, fmt, existing):
        pool = set(fmt.format(x) for x in range(1, 256))
        pool -= set(existing)
        return pool.pop()

    def _serialize(self, container):
        return {
            'name': container.name,
            'root_path': container.root_path,
            'pid_path': container.pid_path,
            'log_path': container.log_path,
            'hostname': container.hostname,
            'ipaddr': container.ipaddr,
            'ipaddr_host': container.ipaddr_host,
            'entry_point': container.entry_point,
        }

    def _serialize_all(self):
        containers_ser = [self._serialize(c) for c in self.containers.values()]
        containers_ser = {'containers': containers_ser}
        containers_ser = json.dumps(containers_ser)

        with open(self.data_path, 'w') as f:
            f.write(containers_ser)

    def _deserialize_all(self):
        try:
            with open(self.data_path, 'r') as f:
                containers_ser = json.loads(f.read())
        except IOError:
            return

        for container_ser in containers_ser['containers']:
            container = libcask.container.Container(**container_ser)
            yield (container.name, container)
