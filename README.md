NeCTAR flavor for CBL
=====================

About
-----
This is a [CloudBioLinux][1] (CBL) flavor intended to be used when building 
CBL images on the [NeCTAR cloud][2] as part of the [Genomics Virtual Laboratory][3].

Installation
------------
To install, first clone CBL from [its Git repository][4] (if you do not already 
have it). Then, change into ``cloudbiolinux/contrib/flavor/`` directory and 
clone this flavor:

    $ cd <project_home>
    $ git clone https://github.com/chapmanb/cloudbiolinux.git
    $ cd cloudbiolinux/contrib/flavor
    $ git clone https://github.com/afgane/nectar_flavor.git nectar

The two repositories will be kept separate (depending on the contents of
your ``.gitignore`` file in the cloudbiolinux repository root directory
(i.e., ``<project_home>``), git may mark ``contrib/flavor/nectar`` as
untracked files, but no need to worry about that - you can add that
directory to your ``.gitignore`` or leave it as it. However, do not add/commit
those files into the cloudbiolinux repostory).

The reason for having separate repositories is because ``nectar_flavor`` code
depends on CBL, but CBL code does not depend on the ``nectar_flavor`` code.
As a result, having these two repositories separate and independently versioned, 
it allows them to be managed independenty (i.e., ``nectar_flavor`` can be versioned
but does not have to become part of the main CBL source).

Use
---
The flavor is used as part of invoking CBL scripts. To adjust the settings the flavor defines, 
edit the following files (all in ``<project_home>/cloudbiolinux/contrib/flavor/nectar`` directory):
 
* ``main.yaml`` - to define the list of meta-packages to be
  installed
* ``packages.yaml`` - to define the exact list of packages to be
  installed (this is in part defined by the list from ``main.yaml``)
* ``fabricrc_nectar.txt`` - to define the paths of where stuff
  should be installed on the remote system

Once all the configuration has been done, run the CBL scripts. The invocation
of these scritps may depend a bit on what you are trying to achieve, but should
look something like this (take a look at the [CBL documentation][4] for more
about the available scripts and options):

    $ fab -f fabfile.py -u ubuntu -i <key> -H <IP> \
      -c ./contrib/flavor/nectar/fabricrc_nectar.txt \
      install_biolinux:target=packages,packagelist=./contrib/flavor/nectar/main.yaml,\
      flavor=nectar,pkg_config_file_path=./contrib/flavor/nectar/packages.yaml

[1]: http://cloudbiolinux.org/
[2]: http://nectar.org.au/research-cloud
[3]: https://www.nectar.org.au/genomics-virtual-laboratory
[4]: https://github.com/chapmanb/cloudbiolinux
