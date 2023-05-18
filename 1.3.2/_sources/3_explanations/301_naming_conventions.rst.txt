Naming conventions
==============================

This package uses the following naming conventions.

variables
    lowercase, underscores ``my_variable = 0``

symbolic constants 
    uppercase, underscores ``COMMAND = "something"``

    Seeing all uppercase in the code quickly indicates this is a constant.

python class names
    camelcase ``class MyClass()``

    Seeing camelcase in the code quickly identifies a class.

python module names (filenames)
    lowercase, underscores, named after the primary class contained within ``my_class.py``

    Having the file named after the class it contains reduces searching for the file.  
    At the same time, it self-documents the file.

python package names (directories)
    lowercase, underscores, ``echolocator_lib``

    Using the same package names as what will be ultimately deployed reduces the amount of mental mapping needed..
    Furthermore, it doesn't require name remapping in setup.py.

imports 
    fully dotted package name and desired symbol, ``from echolocator_lib.contexts.base import Base``

    This explicit importing style means you can always tell exactly what symbols are coming from what packages.


