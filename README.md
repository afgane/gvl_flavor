Genomics Virtual Lab (GVL) flavor for CloudBioLinux
===================================================

About
-----
This is a [CloudBioLinux][1] (CBL) flavor intended to be used when building
CBL images on the [NeCTAR cloud][2] as part of the [Genomics Virtual Laboratory][3].

Installation
------------
To install, first clone CBL from [its Git repository][4] (if you have already
done that). Then, change into ``cloudbiolinux/contrib/flavor/`` directory and
clone this flavor:

    $ cd <project_home>
    $ git clone https://github.com/chapmanb/cloudbiolinux.git
    $ cd cloudbiolinux/contrib/flavor
    $ git clone https://github.com/afgane/gvl_flavor.git gvl

The two repositories will be kept separate (depending on the contents of
your ``.gitignore`` file in the cloudbiolinux repository root directory
(i.e., ``<project_home>``), git may mark ``contrib/flavor/gvl`` as
untracked files, but no need to worry about that - you can add that
directory to your ``.gitignore`` or leave it as is. However, do not add/commit
gvl flavor files into the cloudbiolinux repository).

The reason for having separate repositories is because ``gvl_flavor`` code
depends on CBL, but CBL code does not depend on the ``gvl_flavor`` code.
As a result, having these two repositories separate and independently versioned,
it allows them to be managed independently (i.e., ``gvl_flavor`` can be versioned
but does not have to become part of the main CBL source).

Use
---
The flavor is used as part of invoking CBL scripts. To adjust the settings the flavor defines,
edit the following files (all in ``<project_home>/cloudbiolinux/contrib/flavor/gvl`` directory):

* ``main.yaml`` - to define the list of meta-packages to be
  installed
* ``packages.yaml`` - to define the exact list of system packages to be
  installed (this is in part defined by the list from ``main.yaml``)
* ``*-libs.yaml`` - to define specific language libraries to be installed
  (this is in part defined by the list from ``main.yaml``)
* ``fabricrc.txt`` - to define the paths where software should be installed on
  the remote system

Once all the configuration has been done, rewrite the default ``*.yaml`` files
in CBL with the custom ones: copy
``<project_home>/cloudbiolinux/contrib/flavor/gvl/*.yaml`` to
``<project_home>/config/.`` and run the CBL scripts. The invocation
of these scripts may depend a bit on what you are trying to achieve, but should
look something like this (take a look at the [CBL documentation][4] for more
about the available scripts and options; also, to actually use the custom
``fabricrc.txt``, specify it with
``-c <project_home>/cloudbiolinux/contrib/flavor/gvl/fabricrc.txt``):

    $ fab -i <key> -H ubuntu@<IP> install_biolinux:target=packages,flavor=gvl
    $ fab -i <key> -H ubuntu@<IP> install_biolinux:target=libraries,flavor=gvl
    $ fab -i <key> -H ubuntu@<IP> install_biolinux:target=post_install,flavor=gvl


Once all the packages and libraries have been installed, clean the image and
then create a snapshot from it via the cloud console:

    $ fab -i <key> -H ubuntu@<IP> install_biolinux:target=cleanup


[1]: http://cloudbiolinux.org/
[2]: http://nectar.org.au/research-cloud
[3]: https://genome.edu.au/wiki/GVL
[4]: https://github.com/chapmanb/cloudbiolinux
