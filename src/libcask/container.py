import os
import os.path
import time
import signal
import shlex
import shutil
import subprocess

import libcask.attach
import libcask.error


class Container(object):
    def __init__(
        self,
        name,
        root_path,
        pid_path,
        log_path,
        hostname,
        ipaddr,
        ipaddr_host,
        entry_point,
    ):
        # Human-readable name for this container
        self.name = name

        # Path to the filesystem root directory of the container
        self.root_path = root_path

        # Path to the pidfile of the container
        self.pid_path = pid_path

        # Path to the logfile of the container
        self.log_path = log_path

        # Hostname of the container
        self.hostname = hostname

        # IP Address of the container's virtual ethernet interface
        self.ipaddr = ipaddr

        # IP Address of the host's end of the virtual ethernet pair
        self.ipaddr_host = ipaddr_host

        # Command to run in the new container
        self.entry_point = entry_point

    def pid(self):
        try:
            with open(self.pid_path, 'r') as f:
                return int(f.read())
        except IOError:
            return None

    def create(self):
        os.makedirs(self.root_path)

    def destroy(self):
        if self.status():
            raise libcask.error.AlreadyRunning('Cannot destroy a running container')

        shutil.rmtree(self.root_path)

    def status(self):
        pid = self.pid()
        status_path = '/proc/{pid}/status'.format(pid=pid)

        try:
            with open(status_path, 'r'):
                return True
        except IOError:
            return False

    def start(self):
        if self.status():
            raise libcask.error.AlreadyRunning('Container is already running')

        entry = shlex.split(self.entry_point)
        args = ['cask-clone', self.root_path, self.pid_path] + entry

        with open('/dev/null', 'rwb') as devnull:
            with open(self.log_path, 'wb') as logf:
                subprocess.Popen(args, stdin=devnull, stdout=logf, stderr=logf)

        # TODO - Properly await existence of pidfile. This /sucks/.
        time.sleep(1)

        self.setup_network()

    def copy_file(self, host_path, container_path):
        # HACK - Ensure `container_path` is relative, i.e. transform
        # "/etc/hosts" -> "etc/hosts"
        dest = container_path.strip('/')
        dest = os.path.join(self.root_path, dest)

        shutil.copyfile(host_path, dest)
        shutil.copystat(host_path, dest)

    def get_attachment(self, namespaces=None):
        if not self.status():
            raise libcask.error.NotRunning('Cannot attach to down container')
        return libcask.attach.Attachment(self.pid(), namespaces)

    def kill(self, sig=None):
        if not self.status():
            raise libcask.error.NotRunning('Container is already down')

        os.kill(self.pid(), sig or signal.SIGKILL)
        os.unlink(self.pid_path)

    def setup_network(self):
        self._setup_hostname()
        self._setup_virtual_ethernet()

    def _setup_hostname(self):
        with self.get_attachment(['uts']).attach():
            subprocess.check_call(['hostname', self.hostname])

    def _setup_virtual_ethernet(self):
        veth_name = 'veth-{name}'.format(name=self.name)
        veth_host_name = 'hveth-{name}'.format(name=self.name)

        # Create virtual ethernet pair
        subprocess.check_call([
            'ip', 'link', 'add',
            'name', veth_host_name, 'type', 'veth',
            'peer', 'name', veth_name, 'netns', str(self.pid())
        ])

        # Add the container's host IP address and bring the interface up
        subprocess.check_call(['ip', 'addr', 'add', self.ipaddr_host, 'dev', veth_host_name])
        subprocess.check_call(['ip', 'link', 'set', veth_host_name, 'up'])

        # Add the host interface to the bridge
        # Assuming here that `cask0` bridge interface exists. It should
        # be created and initialized by the Makefile.
        subprocess.check_call(['ip', 'link', 'set', veth_host_name, 'master', 'cask0'])

        # Set up virtual ethernet interface inside the container
        with self.get_attachment(['net', 'uts']).attach():
            subprocess.check_call([
                'ifconfig', veth_name, self.ipaddr, 'up',
            ])
