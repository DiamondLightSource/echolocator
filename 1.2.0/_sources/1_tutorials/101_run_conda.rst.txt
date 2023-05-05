Run under conda
======================================================================================================

This tutorial takes you through the steps to run the echolocator back-end and gui from a conda environment.

1. start the conda environment

    ::

        module purge (or even better, start with a new login shell)
        module load xchem/echolocator/edge/conda

    you should see something like this::

        Echolocator is loaded.  Components are...
        {
            "versions": {
                "echolocator_cli": "1.4.1",
                "echolocator_lib": "1.4.1",
                ... and more
            }
        }

#. get tutorial configuration file

    ::

        cd <some_scratch_directory>
        curl --silent https://gitlab.diamond.ac.uk/xchem/echolocator/-/raw/main/configurations/tutorial.yaml >tutorial.yaml

#. start the services

    ::

        export ECHOLOCATOR_CONFIGFILE=tutorial.yaml
        echolocator_start

    you should see something like this

    ::

        <some lines about database files>
        starting web gui, please browse to http://<hostname>:<port>/index.html
        

#. display the gui

    ::

        browse to <the url just given>
        you should intially see the Image List tab with an empty list
        click AUTO toggle in the upper left (so there is no strike-through on the text)
        now it will update when new images arrive

#. provide some images to be automatically collected

    ::

        open another shell window
        cp -rv /dls_sw/apps/xchem/example_data/echolocator/example_images <some_scratch_directory> (the same as above)

#. view an image

    Click on one of those in the list and the Image Details tab will open.

    Click anywhere in the image to set the target location and advance to the next image.

    Right-click to mark the image unusable, and advance to the next image.

    Use the Next and Previous buttons on the page to traverse through the list.

#. stop the services

    Type control-C in the shell window to stop the services

