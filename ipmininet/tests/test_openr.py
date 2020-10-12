import pytest
import subprocess

from ipmininet.iptopo import IPTopo
from ipmininet.router import OpenrRouter
from ipmininet.node_description import OpenrRouterDescription
from ipmininet.router.config import OpenrRouterConfig

class SimpleOpenrTopo(IPTopo):
    def build(self, *args, **kwargs):
        r1, r2, r3 = \
            self.addRouters('r1', 'r2', 'r3',
                            cls=OpenrRouter,
                            routerDescription=OpenrRouterDescription,
                            config=OpenrRouterConfig)
        self.addLinks((r1, r2), (r1, r3))
        super().build(*args, **kwargs)


@require_root
def test_openr_connectivity():
    try:
        net = IPNet(topo=SimpleBGPTopo())
        net.start()
        assert_connectivity(net, v6=True)
        net.stop()
    finally:
        cleanup()

@require_root
def test_logdir_creation():
    try:
        net = IPNet(topo=SimpleOpenrTopo())
        net.start()
        log_dir_content = os.listdir('/var/tmp/log')
        for i in range(1, 4):
            assert f'r{i}' in log_dir_content
        net.stop()
    finally:
        cleanup()

@require_root
def test_tmp_isolation():
    try:
        net = IPNet(topo=SimpleOpenrTopo())
        net.start()
        tmp_dir_content = os.listdir('/tmp')
        for i in range(1, 4):
            tmp_files = net[f'r{i}'].cmd('ls /tmp')
        net.stop()
    finally:
        cleanup()
