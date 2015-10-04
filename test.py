#!/usr/bin/env python
import sys; sys.path.insert(0, './src/')
import libcask.container

cont = libcask.container.Container(
    name='Example',
    root_path='/home/dev/cask/containers/example/',
    pid_path='/home/dev/cask/pid/example',
    hostname='exampl',
    ipaddr='10.1.1.1',
    ipaddr_host='10.1.1.2',
    entry_point='/busybox sh',
)

if sys.argv[1] == 'start':
    cont.start()
elif sys.argv[1] == 'shell':
    cont.attach().run('/busybox sh')
elif sys.argv[1] == 'kill':
    cont.kill()
elif sys.argv[1] == 'status':
    print 'Running' if cont.status() else 'Not running'
elif sys.argv[1] == 'pid':
    print 'Container running with PID:', cont.pid()
else:
    print 'usage: {} <command>'.format(sys.argv[0])
