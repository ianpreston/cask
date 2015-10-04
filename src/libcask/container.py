import os
import os.path
import time
import signal
import subprocess

import libcask.attach
import libcask.network


class Container(libcask.network.SetupNetworkMixin):
    def __init__(
        self,
        name,
        root_path,
        pid_path,
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
        os.makedirs(os.path.dirname(self.pid_path))

    def status(self):
        pid = self.pid()
        status_path = '/proc/{pid}/status'.format(pid=pid)

        try:
            with open(status_path, 'r') as f:
                return True
        except IOError:
            return False

    def start(self):
        entry = self.entry_point.split(' ')
        args = ['./cask-clone', self.root_path, self.pid_path] + entry

        with open('/dev/null', 'rwb') as devnull:
            subprocess.Popen(args, stdin=devnull, stdout=devnull, stderr=devnull)

        # TODO - Properly await existence of pidfile. This /sucks/.
        time.sleep(1)

        print 'pid:', self.pid()

        self.setup_network()

    def attach(self):
        return libcask.attach.Attachment(self.pid())

    def kill(self, sig=None):
        os.kill(self.pid(), sig or signal.SIGKILL)
        os.unlink(self.pid_path)
