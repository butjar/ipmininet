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
    DEPENDS = (OpenrDaemon,)
    KILL_PATTERNS = (NAME,)

    def __init__(self, node, *args, **kwargs):
        super(Openr, self).__init__(node=node, *args, **kwargs)

    def build(self):
        cfg = super(Openr, self).build()
        for key in self._default_config().keys():
            cfg[key] = self.options[key]

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
                                          self.options.spark_hold_time_s),
                           spark_keepalive_time_s=i.get('openr_spark_keepalive_time_s',
                                          self.options.spark_keepalive_time_s)) for i in interfaces]

    def set_defaults(self, defaults):
        for k, v in self._default_config().iteritems():
            defaults[k] = v
        super(Openr, self).set_defaults(defaults)

    def _default_config(self):
        """See https://github.com/facebook/openr/blob/master/openr/docs/Runbook.md"""
        return ConfigDict(alloc_prefix_len=128,
                          assume_drained=False,
                          config_store_filepath="/tmp/aq_persistent_config_store.bin",
                          decision_debounce_max_ms=250,
                          decision_debounce_min_ms=10,
                          decision_rep_port=60004,
                          domain="openr",
                          dryrun=False,
                          enable_subnet_validation=True,
                          enable_fib_sync=False,
                          enable_health_checker=False,
                          enable_legacy_flooding=True,
                          enable_lfa=False,
                          enable_netlink_fib_handler=True,
                          enable_netlink_system_handler=True,
                          enable_old_decision_module=False,
                          enable_perf_measurement=True,
                          enable_prefix_alloc=False,
                          enable_rtt_metric=True,
                          enable_secure_thrift_server=False,
                          enable_segment_routing=False,
                          enable_spark=True,
                          enable_v4=False,
                          enable_watchdog=True,
                          fib_handler_port=60100,
                          fib_rep_port=60009,
                          health_checker_ping_interval_s=3,
                          health_checker_rep_port=60012,
                          iface_prefixes="terra,nic1,nic2",
                          iface_regex_exclude="",
                          iface_regex_include="",
                          ip_tos=192,
                          key_prefix_filters="",
                          kvstore_flood_msg_per_sec=0,
                          kvstore_flood_msg_burst_size=0,
                          kvstore_ttl_decrement_ms=1,
                          kvstore_zmq_hwm=65536,
                          link_flap_initial_backoff_ms=1000,
                          link_flap_max_backoff_ms=60000,
                          link_monitor_cmd_port=60006,
                          loopback_iface="lo",
                          memory_limit_mb=300,
                          min_log_level=0,
                          override_loopback_addr=False,
                          prefix_manager_cmd_port=60011,
                          prefixes="",
                          redistribute_ifaces="lo1",
                          seed_prefix="",
                          set_leaf_node=False,
                          set_loopback_addr=False,
                          spark_fastinit_keepalive_time_ms=100,
                          spark_hold_time_s=30,
                          spark_keepalive_time_s=3,
                          static_prefix_alloc=False,
                          tls_acceptable_peers="",
                          tls_ecc_curve_name="prime256v1",
                          tls_ticket_seed_path="",
                          verbosity=1,
                          x509_ca_path="",
                          x509_cert_path="",
                          x509_key_path="")


    def is_active_interface(self, itf):
        """Return whether an interface is active or not for the OpenR daemon"""
        return L3Router.is_l3router_intf(otherIntf(itf))


class OpenrNetwork(object):
    """A class holding an OpenR network properties"""

    def __init__(self, domain):
        self.domain = domain


class OpenrPrefixes(object):
    """A class representing a prefix type in OpenR"""

    def __init__(self, prefixes):
        self.prefixes = prefixes
