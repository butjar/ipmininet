from .base import Daemon

class OpenrDaemon(Daemon):
    """The base class for the OpenR daemon"""

    # Additional parameters to pass when starting the daemon
    STARTUP_LINE_EXTRA = ''
    STARTUP_SCRIPT = 'run_openr.sh'

    @property
    def startup_line(self):
        return '{startup_script}'\
                .format(startup_script=self.STARTUP_SCRIPT,
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
        return '{name} {cfg} --dryrun=true'\
               .format(name=self.NAME,
                       cfg=self.cfg_filename)
