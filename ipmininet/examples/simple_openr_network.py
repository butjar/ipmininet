"""This file contains a simple OpenR topology"""

from ipmininet.iptopo import IPTopo
from ipmininet.router.config import RouterConfig

HOSTS_PER_ROUTER = 2


class OpenrConfig(RouterConfig):
    """A simple config with only a BGP daemon"""
    def __init__(self, node, *args, **kwargs):
        defaults = {}
        super(OpenrConfig, self).__init__(node,
                                        daemons=((OpenrDaemon, defaults),),
                                        *args, **kwargs)


class SimpleOpenrNet(IPTopo):
    """"""

    def build(self, *args, **kwargs):
        r1 = self.addRouter_openr('r1')
        r2 = self.addRouter_openr('r2')
        r3 = self.addRouter_openr('r3')
        self.addLink(r1, r2)
        self.addLink(r1, r3)
        self.addLink(r3, r2)
        for r in (r1, r2, r3):
            for i in xrange(HOSTS_PER_ROUTER):
                self.addLink(r, self.addHost('h%s%s' % (i, r)),
                             params2={'v4_width': 5})


        super(SimpleOpenRNet, self).build(*args, **kwargs)

    def addRouter_openr(self, name):
        return self.addRouter(name, config=OpenrConfig)
