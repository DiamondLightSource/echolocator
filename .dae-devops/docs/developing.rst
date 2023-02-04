.. # ********** Please don't edit this file!
.. # ********** It has been generated automatically by dae_devops version 0.5.1.
.. # ********** For repository_name echolocator

Developing
=======================================================================

If you plan to make change to the code in this repository, you can use the steps below.

Clone the repository::

    $ git clone https://gitlab.diamond.ac.uk/xchem/echolocator.git

It is recommended that you install into a virtual environment so this
installation will not interfere with any existing Python software.
Make sure to have at least python version 3.9 then::

    $ python3 -m venv /scratch/$USER/myvenv
    $ source /scratch/$USER/myvenv/bin/activate
    $ pip install --upgrade pip

Install the package in edit mode which will also install all its dependencies::

    $ cd echolocator
    $ export PIP_FIND_LINKS=/dls_sw/apps/bxflow/artifacts
    $ pip install -e .[dev]

Now you may begin modifying the code.

|

If you plan to modify the docs, you will need to::

    $ pip install -e .[docs]

    


.. # dae_devops_fingerprint c3acd7bd04d4c567174c7ba12f90efb0
