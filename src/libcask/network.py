import subprocess


class SetupNetworkMixin(object):
    def _setup_hostname(self):
        with self.get_attachment().attach():
            subprocess.check_call(['hostname', self.hostname])

    def _setup_virtual_ethernet(self):
        veth_name = 'veth-{hostname}'.format(hostname=self.hostname)
        veth_host_name = 'hveth-{hostname}'.format(hostname=self.hostname)

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

    def setup_network(self):
        self._setup_hostname()
        self._setup_virtual_ethernet()
