import os
import os.path
import signal
import subprocess

import libcask.attach


class Container(object):
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
        self.ipaddr_host = ipaddr

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

        proc = subprocess.Popen(args)
        print 'pid:', self.pid()

    def attach(self):
        return libcask.attach.Attachment(self.pid())

    def kill(self, sig=None):
        os.kill(self.pid(), sig or signal.SIGKILL)
