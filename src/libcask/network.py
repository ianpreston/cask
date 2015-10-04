import subprocess


class SetupNetworkMixin(object):
    def _setup_hostname(self):
        with self.get_attachment().attach():
            subprocess.check_call(['hostname', self.hostname])

    def _setup_virtual_ethernet(self):
        # Setup virtual ethernet interface on the host
        # TODO - Need to allocate virtual interface names to containers!
        subprocess.check_call([
            'ip', 'link', 'add',
            'name', 'veth0', 'type', 'veth',
            'peer', 'name', 'veth1', 'netns', str(self.pid())
        ])
        subprocess.check_call([
            'ifconfig', 'veth0', self.ipaddr_host, 'up',
        ])

        # Set up virtual ethernet interface inside the container
        # TODO - Only attach CLONE_NEWNET and use the host's ifconfig, so we're
        # not relying on the container having ifconfig.
        with self.get_attachment().attach():
            subprocess.check_call([
                'ifconfig', 'veth1', self.ipaddr, 'up',
            ])

    def setup_network(self):
        self._setup_hostname()
        self._setup_virtual_ethernet()
