
from fabric.api import run
from cloudbio.flavor import Flavor
from cloudbio.custom.shared import _get_install


class GVLFlavor(Flavor):
    def __init__(self, env):
        print "-> In GVLFlavor"
        Flavor.__init__(self, env)
        self.name = "GVL Flavor"

    def rewrite_config_items(self, name, packages):
        pass
        # if name == 'packages':
        #     packages += ['nfs-common']
        # for package in packages:
        #   env.logger.info("Selected: "+name+" "+package)
        # return packages

    def post_install(self):
        self.env.logger.info("Starting post-install")
        self._install_postgres()

    def _install_postgres_configure_make(self):
        run('./configure --prefix=/usr/lib/postgresql/8.4 --with-pgport=5840 --with-python')
        run('make')
        self.env.safe_sudo('make install')

    def _install_postgres(self):
        """
        Install PostgreSQL from source; this defaults to Postgres
        version 8.4 and is added for backward compatibility.
        """
        version = "8.4.15"
        url = ("http://ftp.postgresql.org/pub/source/" +
              "v{0}/postgresql-{0}.tar.gz").format(version)
        _get_install(url, self.env, self._install_postgres_configure_make)

env.flavor = GVLFlavor(env)
