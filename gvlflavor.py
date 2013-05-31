
from fabric.api import run
from cloudbio.flavor import Flavor
from cloudbio.custom.shared import _get_install
from fabric.api import *
from fabric.contrib.files import *

from cloudbio.flavor import Flavor

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
        
        run("cd $INSTALL_DIR")
        
        vars = {'DBNAME': 'scfdb', 'USERNAME': 'scfuser','PASSWORD' : 'scfgv7', 'DEST_DIR': 'www'}
        run("sudo sed -i 's/max_execution_time = 30$/max_execution_time = 600/g' /etc/php5/fpm/php.ini")
        run("sudo sed -i 's/;request_terminate_timeout = 0$/request_terminate_timeout = 600/g' /etc/php5/fpm/pool.d/www.conf")
        run("sed -i 's/www-data/galaxy/g' /etc/php5/fpm/pool.d/www.conf")
        run("mkdir -p %(DEST_DIR)s " % vars)
        with cd(vars['DEST_DIR']) :
            run("rm -rf gvl-scf")
            run("git clone git://github.com/Traksewt/gvl-scf.git")
            run("wget https://s3-ap-southeast-2.amazonaws.com/gvl-scf/createDB.sh")
            run("wget https://s3-ap-southeast-2.amazonaws.com/gvl-scf/fix-permissions.sh")
            run("chmod +x createDB.sh")
            run("chmod +x fix-permissions.sh")
            run("sudo ./fix-permissions.sh --drupal_path=$DEST_DIR/gvl-scf --drupal_user=ubuntu")
            run("cp gvl-scf/sites/default/default.settings.php gvl-scf/sites/default/settings.php")
            run("sed -i 's/\[DATABASE\]/$DBNAME/g'  $DEST_DIR/gvl-scf/sites/default/settings.php")
            run("sed -i 's/\[USERNAME\]/$USERNAME/g'  $DEST_DIR/gvl-scf/sites/default/settings.php")
            run("sed -i 's/\[PASSWORD\]/$PASSWORD/g'  $DEST_DIR/gvl-scf/sites/default/settings.php")
            run("chmod 770 gvl-scf/sites/default/settings.php")
            run("dropdb -U postgres $DBNAME")
            run("psql -U postgres    -c \" DROP ROLE $USERNAME;\"")
        #echo "Dropped old database"
            run("psql -U postgres -c \" CREATE ROLE $USERNAME LOGIN PASSWORD '$PASSWORD';\"")
            run("createdb -U postgres --encoding=UTF8 --owner=$USERNAME $DBNAME")
        #echo "Created new database: $DBNAME"
        
        #/etc/php5/fpm/pool.d/www.conf change user/group to galaxy/galaxy from www-data/www-data
        run("sudo /etc/init.d/php5-fpm restart")
        run("drush cc all")
        run("sudo killall nginx")
        run("sudo /opt/galaxy/sbin/nginx");
        with cd("%(DEST_DIR)s/gvl-scf" % vars) :
            run("drush site-install scf_vm --yes --account-name=admin --account-pass=$PASSWORD --db-url=pgsql://$USERNAME:$PASSWORD@localhost/$DBNAME --site-name=$SITE_NAME")
        

env.flavor = GVLFlavor(env)
