#!/usr/bin/env python
import sys
import ctypes
import subprocess


NAMESPACES = [
    'net',
    'uts',
    'ipc',
    'pid',
    'mnt',
]


class Attach(object):
    def __init__(self, pid):
        self.libc = ctypes.CDLL('libc.so.6', use_errno=True)
        self.pid = int(pid)

    def _attach_namespace(self, ns_path):
        with open(ns_path, 'r') as f:
            print 'Attach to namespace:', ns_path
            rv = self.libc.setns(f.fileno(), 0)
            if rv != 0:
                raise Exception('Unexpected return value from setns()', rv)

    def attach_all(self):
        for ns in NAMESPACES:
            ns_path = '/proc/{pid}/ns/{ns}'.format(
                pid=self.pid,
                ns=ns,
            )
            self._attach_namespace(ns_path)

    def run(self, cmd):
        print 'Run:', cmd
        rv = subprocess.check_call(cmd, shell=True)
        print 'Return code:', rv


def main():
    if len(sys.argv) < 3:
        print 'usage: {cmd} <pid> <command>'.format(cmd=sys.argv[0])
        return

    att = Attach(int(sys.argv[1]))
    att.attach_all()
    att.run(' '.join(sys.argv[2:]))


if __name__ == '__main__':
    main()
