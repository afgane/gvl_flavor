For the time being, there's only a single playbook here and it is used for
creating a package for installing a custom version of nginx. Once the package
is built, copy it where you want to install it and install it with as any
other `.deb` (eg, `dpkg -i <package_name>`).

To run the playbook, install Ansible into a virtualenv:

    virtualenv .
    source bin/activate
    pip install ansible

Then, edit `hosts` file to point to the instance you would like to build the
package on and run the script with the following command:

    ansible-playbook nginx_cm.yml --sudo -i hosts --private-key <path to PK>

Instead of using the private key for authentication, you can also use a
password:

    ansible-playbook nginx_cm.yml --sudo -i hosts -k -c paramiko

Once the playbook has finished running, a `.deb.` file will be created in
`/tmp/nginx` (or whatevr you set in `nginx_cm.yml` file).
