from .base import Daemon

class OpenrDaemon(Daemon):
    """The base class for the OpenR daemon"""

    NAME = 'openr'

    @property
    def STARTUP_LINE_EXTRA(self):
        # Add options to the standard startup line
        return ''

    @property
    def startup_line(self):
        return '{name} {cfg} {extra}'\
                .format(name=self.NAME,
                        cfg=self.cfg_filename,
                        extra=self.STARTUP_LINE_EXTRA)

    def build(self):
        cfg = super(OpenrDaemon, self).build()
        cfg.debug = self.options.debug
        return cfg

    def set_defaults(self, defaults):
        """:param debug: the set of debug events that should be logged"""
        defaults.debug = ()
        super(OpenrDaemon, self).set_defaults(defaults)

    @property
    def dry_run(self):
        # The OpenR dryrun runs the daemon and does not shutdown the daemon
        # TODO: Replace with a config parser or shutdown the daemon after few
        # seconds
        return '{name} --version'\
               .format(name=self.NAME)
