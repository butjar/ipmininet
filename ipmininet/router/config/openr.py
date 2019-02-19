"""Base classes to configure an OpenR daemon"""
from ipaddress import ip_interface

from ipmininet.iptopo import Overlay
from ipmininet.utils import otherIntf, L3Router, realIntfList
from .utils import ConfigDict
from .openrd import OpenrDaemon


class OpenrDomain(Overlay):
    """An overlay to group OpenR links and routers by domain"""

    def __init__(self, domain, routers=(), links=(), **props):
        """:param domain: the domain for this overlay
        :param routers: the set of routers for which all their interfaces
                        belong to that area
        :param links: individual links belonging to this area"""
        super(OpenrDomain, self).__init__(nodes=routers, links=links,
                                          nprops=props)
        self.domain = domain

    @property
    def domain(self):
        return self.link_properties['openr_domain']

    @domain.setter
    def domain(self, x):
        self.link_properties['openr_domain'] = x

    def apply(self, topo):
        # Add all links for the routers
        for r in self.nodes:
            self.add_link(*topo.g[r])
        super(OpenrDomain, self).apply(topo)

    def __str__(self):
        return '<OpenR domain %s>' % self.domain


class Openr(OpenrDaemon):
    """This class provides a simple configuration for an OpenR daemon."""
    NAME = 'openr'
    DEPENDS = (OpenrDeamon,)
    KILL_PATTERNS = (NAME,)

    def __init__(self, node, *args, **kwargs):
        super(Openr, self).__init__(node=node, *args, **kwargs)

    def build(self):
        cfg = super(Openr, self).build()
        cfg.redistribute = self.options.redistribute
        interfaces = [itf
                      for itf in realIntfList(self._node)]
        cfg.interfaces = self._build_interfaces(interfaces)
        cfg.networks = self._build_networks(interfaces)
        return cfg

    def _build_networks(self, interfaces):
        """Return the list of OpenR networks to advertize from the list of
        active OpenR interfaces"""
        # Check that we have at least one IPv4 network on that interface ...
        return [OpenrNetwork(domain=ip_interface(
            u'%s/%s' % (i.ip, i.prefixLen))) for i in interfaces if i.ip]

    def _build_interfaces(self, interfaces):
        """Return the list of OpenR interface properties from the list of
        active interfaces"""
        return [ConfigDict(description=i.describe,
                           name=i.name,
                           # Is the interface between two routers?
                           active=self.is_active_interface(i),
                           spark_hold_time_s=i.get('openr_spark_hold_time_s',
                                          self.options.priority),
                           spark_keepalive_time_s=i.get('openr_spark_keepalive_time_s',
                                          self.options.dead_int),
                for i in interfaces]

    def set_defaults(self, defaults):
        """:spark_hold_time_s: Dead interval timer
        :param spark_keepalive_time_s: Hello interval timer
        :param prefixes: set of Prefixes"""
        defaults.spark_hold_time_s = 30
        defaults.spark_keepalive_time_s = 3
        defaults.prefixes = []
        super(Openr, self).set_defaults(defaults)

    def is_active_interface(self, itf):
        """Return whether an interface is active or not for the OpenR daemon"""
        return L3Router.is_l3router_intf(otherIntf(itf))


class OpenrNetwork(object):
    """A class holding an OpenR network properties"""

    def __init__(self, domain, area):
        self.domain = domain


class OpenrPrefixes(object):
    """A class representing a prefix type in OpenR"""

    def __init__(self, prefixes):
        self.prefixes = prefixes
