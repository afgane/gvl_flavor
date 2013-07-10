import os
from fabric.api import run, cd, settings, env, put
from cloudbio.flavor import Flavor
from cloudbio.custom.shared import _get_install, _add_to_profiles

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
        # self._install_postgres()
        # comment out SCF GVL for the moment
        #  self._install_php()
        self._setup_env()

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
            with cd('gvl-scf/sites/all/modules/custom'):
                run("git clone git://github.com/Traksewt/journalstream.git")
            run("wget https://s3-ap-southeast-2.amazonaws.com/gvl-scf/fix-permissions.sh")
            run("chmod +x fix-permissions.sh")
            run("sudo ./fix-permissions.sh --drupal_path=gvl-scf --drupal_user=ubuntu")
            run("cp gvl-scf/sites/default/default.settings.php gvl-scf/sites/default/settings.php")
            run("sed -i 's/\[DATABASE\]/%(DBNAME)s/g'  gvl-scf/sites/default/settings.php" % vars)
            run("sed -i 's/\[USERNAME\]/%(USERNAME)s/g'  gvl-scf/sites/default/settings.php" % vars)
            run("sed -i 's/\[PASSWORD\]/%(PASSWORD)s/g'  gvl-scf/sites/default/settings.php" % vars)
#            run("sudo sed -i 's/\#write_enable=YES/write_enable=YES/g'  /etc/vsftpd.conf" )
            
            
            
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

        with settings(warn_only=True):
            run("sudo killall nginx")
            run("sudo mkdir -p %(nginx_upload_store_path)s" % env)
        run("sudo /opt/galaxy/sbin/nginx")
        with cd("%(DEST_DIR)s/gvl-scf" % vars):
            run("drush site-install scf_vm --yes --account-name=admin --account-pass=%(PASSWORD)s --db-url=pgsql://%(USERNAME)s:%(PASSWORD)s@localhost/%(DBNAME)s --site-name=%(SITE_NAME)s" % vars)
            run("drush cc all")
        run("rm ~/.pgpass")
        with cd(vars['DEST_DIR']):
            run("sudo /etc/init.d/php5-fpm restart")
            run("rm fix-permissions.sh")
        run("sudo chown -R ubuntu:galaxy %(DEST_DIR)s " % vars)

    def _setup_env(self):
        """
        Setup a custom user-level env
        """
        # Add commond directories to PATH
        path_additions = ("export PATH=/usr/lib/postgresql/9.1/bin:" +
            "/usr/nginx/sbin:/mnt/galaxy/tools/bin:$PATH")
        env.logger.debug("Amending the PATH with {0}".format(path_additions))
        _add_to_profiles(path_additions, ['/etc/bash.bashrc'])
        # Seed the history with frequently used commands
        env.logger.debug("Setting bash history")
        local = os.path.join(env.config_dir, os.pardir, "installed_files",
            "bash_history")
        remote = os.path.join('/home', 'ubuntu', '.bash_history')
        put(local, remote, mode=0660, use_sudo=True)
        # Install ipython profiles
        users = ['ubuntu', 'galaxy']
        for user in users:
            env.logger.debug("Setting installing ipython profile for user {0}"
                .format(user))
            env.safe_sudo("su - {0} -c 'ipython profile create'".format(user))
            local = os.path.join(env.config_dir, os.pardir, "installed_files",
                "ipython_config.py")
            remote = os.path.join('/home', user, '.ipython', 'profile_default',
                "ipython_config.py")
            put(local, remote, mode=0644, use_sudo=True)
            env.safe_sudo("chown {0}:{0} {1}".format(user, remote))

env.flavor = GVLFlavor(env)
