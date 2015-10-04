#!/usr/bin/env python
import ctypes
import subprocess


NAMESPACES = [
    'net',
    'uts',
    'ipc',
    'pid',
    'mnt',
]


class Attachment(object):
    def __init__(self, pid):
        self.libc = ctypes.CDLL('libc.so.6', use_errno=True)
        self.pid = int(pid)

        self._attach_all()

    def _attach_namespace(self, ns_path):
        with open(ns_path, 'r') as f:
            rv = self.libc.setns(f.fileno(), 0)
            if rv != 0:
                raise Exception('Unexpected return value from setns()', rv)

    def _attach_all(self):
        for ns in NAMESPACES:
            ns_path = '/proc/{pid}/ns/{ns}'.format(
                pid=self.pid,
                ns=ns,
            )
            self._attach_namespace(ns_path)

    def run(self, cmd):
        subprocess.check_call(cmd, shell=True)
