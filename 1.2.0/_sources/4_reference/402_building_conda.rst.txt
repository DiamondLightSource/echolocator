Building the conda environment
==============================

Use the commands below to build the conda environment.



1. bump version
    ::

        cd ~/27/echolocator
        make bump-minor

#. build docs
    ::

        cd ~/27/echolocator
        make build_docs

#. copy files to shared drive
    This is only necessary if you edit files anywhere but on the /home mount.

    ::

        cd /drives/c/27/echolocator
        make rsync

#. build the conda environment
    ::

        cd ~/27/echolocator
        make build_conda_environment

#. update the edge module
    ::

        cd ~/27/echolocator
        make deploy_modules

#. publish docs
    ::

        cd ~/27/echolocator
        make publish_docs