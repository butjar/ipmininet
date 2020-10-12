import pytest
import os
import tempfile

from ipmininet.clean import cleanup
from ipmininet.iptopo import IPTopo
from ipmininet.router import OpenrRouter
from ipmininet.node_description import OpenrRouterDescription
from ipmininet.router.config import OpenrRouterConfig
from ipmininet.tests.utils import assert_connectivity


from . import require_root


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
        log_dir = '/var/tmp/log'
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
        tmp_dir = '/tmp'
        with tempfile.NamedTemporaryFile(dir=tmp_dir) as f:
            file_base_name = os.path.basename(f.name)
            host_tmp_dir_content = os.listdir(tmp_dir)
            assert file_base_name in host_tmp_dir_content
            for i in range(1, 4):
                node_tmp_dir_content = net[f'r{i}'].cmd('ls /tmp').split()
                assert not file_base_name in node_tmp_dir_content
        net.stop()
    finally:
        cleanup()
