
from fabric.api import run, cd, settings, env
from cloudbio.flavor import Flavor
from cloudbio.custom.shared import _get_install
#from fabric.api import *
#from fabric.contrib.files import *


class GVLFlavor(Flavor):
    def __init__(self, env):
        print "-> In GVLFlavor"
        Flavor.__init__(self, env)
        self.name = "GVL Flavor"

    def rewrite_config_items(self, name, packages):
        #pass
        # if name == 'packages':
        #     packages += ['nfs-common']
        # for package in packages:
        #   env.logger.info("Selected: "+name+" "+package)
        return packages

    def post_install(self):
        self.env.logger.info("Starting post-install")
        self._install_postgres()
        self._install_php()

    def _install_postgres_configure_make(self, env):
        run('./configure --prefix=/usr/lib/postgresql/8.4 --with-pgport=5840 --with-python')
        run('make')
        env.safe_sudo('make install')

    def _install_postgres(self):
        """
        Install PostgreSQL from source; this defaults to Postgres
        version 8.4 and is added for backward compatibility.
        """
        version = "8.4.15"
        url = ("http://ftp.postgresql.org/pub/source/" +
              "v{0}/postgresql-{0}.tar.gz").format(version)
        _get_install(url, self.env, self._install_postgres_configure_make)

    def _install_php(self):
        """
        Install Php and adapters for nginx and postgres
        """
        vars = {'DBNAME': self.env.scf_dbname, 'USERNAME': self.env.scf_username,
                'PASSWORD': self.env.scf_password, 'DEST_DIR': self.env.scf_dest_dir,
                'SITE_NAME': self.env.scf_site_name}
        run("sudo sed -i 's/max_execution_time = 30$/max_execution_time = 600/g' /etc/php5/fpm/php.ini")
        run("sudo sed -i 's/;request_terminate_timeout = 0$/request_terminate_timeout = 600/g' /etc/php5/fpm/pool.d/www.conf")
        run("sudo sed -i 's/www-data/galaxy/g' /etc/php5/fpm/pool.d/www.conf")
        run("sudo sed -i 's/local   all             postgres                                peer/local   all             postgres                                trust/g' /etc/postgresql/9.1/main/pg_hba.conf")
        
        if env.has_key("scf_standalone"):
            env.nginx_upload_store_path = env.nginx_upload_store_path_SCF_standalone
        run("mkdir -p %(DEST_DIR)s " % vars)
        with cd(vars['DEST_DIR']):
            run("sudo rm -rf gvl-scf")
            run("git clone git://github.com/Traksewt/gvl-scf.git")
            run("wget https://s3-ap-southeast-2.amazonaws.com/gvl-scf/fix-permissions.sh")
            run("chmod +x fix-permissions.sh")
            run("sudo ./fix-permissions.sh --drupal_path=gvl-scf --drupal_user=ubuntu")
            run("cp gvl-scf/sites/default/default.settings.php gvl-scf/sites/default/settings.php")
            run("sed -i 's/\[DATABASE\]/%(DBNAME)s/g'  gvl-scf/sites/default/settings.php" % vars)
            run("sed -i 's/\[USERNAME\]/%(USERNAME)s/g'  gvl-scf/sites/default/settings.php" % vars)
            run("sed -i 's/\[PASSWORD\]/%(PASSWORD)s/g'  gvl-scf/sites/default/settings.php" % vars)
            run("sudo sed -i 's/cgi\.fix_pathinfo=0/cgi\.fix_pathinfo=1/g'  /etc/php5/fpm/php.ini")

            run("chmod 770 gvl-scf/sites/default/settings.php")
            run("sudo chown ubuntu:galaxy gvl-scf/sites/default/settings.php")
            run("echo \"localhost:5432:*:%(USERNAME)s:%(PASSWORD)s\" > ~/.pgpass" % vars)
            run("chmod 600 ~/.pgpass")
            run("sudo /etc/init.d/postgresql reload")
            with settings(warn_only=True):
                run("dropdb -U postgres %(DBNAME)s" % vars)
                run("psql -U postgres    -c \" DROP ROLE %(USERNAME)s;\"" % vars)
        #echo "Dropped old database"
            run("psql -U postgres -c \" CREATE ROLE %(USERNAME)s LOGIN CREATEDB PASSWORD '%(PASSWORD)s';\""
                % vars)
            run("createdb -U postgres --encoding=UTF8 --owner=%(USERNAME)s %(DBNAME)s" % vars)
        #echo "Created new database: $DBNAME"

            run("sudo /etc/init.d/php5-fpm restart")
            run("drush cc all")
        with settings(warn_only=True):
            run("sudo killall nginx")
            run("sudo mkdir -p %(nginx_upload_store_path)s" % env)
        run("sudo /opt/galaxy/sbin/nginx")
        with cd("%(DEST_DIR)s/gvl-scf" % vars):
            run("drush site-install scf_vm --yes --account-name=admin --account-pass=%(PASSWORD)s --db-url=pgsql://%(USERNAME)s:%(PASSWORD)s@localhost/%(DBNAME)s --site-name=%(SITE_NAME)s" % vars)
        run("rm ~/.pgpass")
        with cd(vars['DEST_DIR']):
            run("rm fix-permissions.sh")
        run("sudo chown -R ubuntu:galaxy %(DEST_DIR)s " % vars)

env.flavor = GVLFlavor(env)
