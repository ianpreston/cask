#!/usr/bin/env python
import os
import ctypes
import contextlib


NAMESPACES = [
    'net',
    'uts',
    'ipc',
    'pid',
    'mnt',
]


class Attachment(object):
    def __init__(self, container_pid, namespaces=None):
        self.namespaces = namespaces or NAMESPACES
        self.libc = ctypes.CDLL('libc.so.6', use_errno=True)

        host_pid = os.getpid()
        self.host_namespaces = list(self._open_all(host_pid))
        self.container_namespaces = list(self._open_all(container_pid))

    def _attach_namespace(self, namespace):
        rv = self.libc.setns(namespace.fileno(), 0)
        if rv != 0:
            raise Exception('Unexpected return value from setns()', rv)

    def _attach_all(self, namespaces):
        for ns in namespaces:
            self._attach_namespace(ns)

    def _open_all(self, pid):
        for ns in self.namespaces:
            if ns not in NAMESPACES:
                raise Exception('Invalid namespace', ns)

            ns_path = '/proc/{pid}/ns/{ns}'.format(
                pid=pid,
                ns=ns,
            )
            yield open(ns_path, 'r')

    @contextlib.contextmanager
    def attach(self):
        self._attach_all(self.container_namespaces)
        yield
        self._attach_all(self.host_namespaces)
