Process
==============================

The source images come from the Formulatrix Rockmaker device.  
The Formulatrix makes images of wells which are molded onto crystallization plates, with several hundred wells to a plate.
An example plate looks like this.

    .. image:: ../images/swiss3.png
        :width: 400
        :alt: Example crystal plate.


Each source image is of one well in which crystals should be present.
The filename of the image represents the plate and the well location.

The Chimp software is able to use ML techniques to automatically determine the target drop point.
These are sent to theis echolocator database before human viewing.

The human operator uses this gui to verify the desired dispenser location.
They can manually override what Chimp has proposed.

The final locations are exported for later reading by soakdb and eventually transmitted to the Echo device.

The gui has two tabs which look like this:

The Image List tab.

    .. image:: ../images/image_list.png
        :width: 400
        :alt: Image list tab.

The Image Details tab.

    .. image:: ../images/image_details.png
        :width: 400
        :alt: Image edit tab.
