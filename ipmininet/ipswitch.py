"""This modules defines the IPSwitch class allowing to better support STP
   and to create hubs"""
from typing import Optional, Callable

from mininet.link import Intf
from mininet.nodelib import LinuxBridge
from ipmininet.utils import require_cmd


class IPBridge(LinuxBridge):
    """
    Linux Bridge (with optional spanning tree) and callback functions when that
    allow configuration on startup
    """

    def __init__(self, name: str, stp=False,
                 prio: Optional[int] = None, **kwargs):
        """:param name: the name of the node
           :param stp: whether to use spanning tree protocol
           :param prio: optional explicit bridge priority for STP"""
        super().__init__(name, stp=stp, prio=prio, **kwargs)

    def start(self, _controllers,
              br_init: Callable[['IPSwitch'], None] = lambda _: None,
              intf_init: Callable[['IPSwitch', Intf], None] = lambda _x,_y: None):
        """
        Start Linux bridge without STP

        :param _controllers: A parameter defined in LinuxBridge that actually
            does nothing
        :param br_init: callback to initialize the bridge on startup
        :param intf_init: callback to initialize the bridge interfaces on
            startup
        """
        require_cmd("brctl", help_str="You need brctl to use %s objects"
                                      % self.__class__)

        self.cmd('ifconfig', self, 'down')
        self.cmd('brctl delbr', self)
        self.cmd('brctl addbr', self)

        br_init(self) # Bridge initializer callback
        for i in self.intfList():
            if self.name in i.name:
                self.cmd('brctl addif', self, i)
                intf_init(self, i) # Intf initializer callback

        self.cmd('ifconfig', self, 'up')

class IPSwitch(IPBridge):
    """
    IPBridge (with optional spanning tree) and default callbacks for stp if
    enabled
    """

    def __init__(self, name: str, stp=True,
                 prio: Optional[int] = None,
                 **kwargs):
        super().__init__(name, stp=stp, prio=prio, **kwargs)

    def start(self, _controllers):
        """
        Start Linux bridge with default callbacks to setup STP on startup

        :param _controllers: A parameter defined in LinuxBridge that actually
            does nothing
        """
        if self.stp:
            def br_init(o):
                o.cmd('brctl setbridgeprio', o, o.prio)
                o.cmd('brctl stp', o, 'on')

            def intf_init(switch, intf):
                switch.cmd('brctl setpathcost'
                           ' %s %s %d' % (switch.name, intf.name,
                                          intf.params.get('stp_cost', 1)))
        else:
            br_init = lambda _: None
            intf_init = lambda _x,_y: None

        super().start(_controllers,
                      br_init=br_init,
                      intf_init=intf_init)


class Hub(IPBridge):
    """
    A IPBridge with spanning tree disabled and ageing set to 0
    """
    def __init__(self, name: str,
                 prio: Optional[int] = None,
                 **kwargs):
        kwargs.pop('stp', None)
        super().__init__(name, stp=False, prio=prio, **kwargs)

    def start(self, _controllers):
        """
        Start Hub

        :param _controllers: A parameter defined in LinuxBridge that actually
            does nothing
        """
        def br_init(hub):
            hub.cmd('brctl setageing 0', hub)
            hub.cmd( 'brctl stp', hub, 'off')

        super().start(_controllers, br_init=br_init)
