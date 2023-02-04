Add fields to the database
=========================================================================================

This section describes the actions you must take to add new a new field to the database.

Let's say you want to add a new field called ``myfield`` to the ``rockmaker_images`` table.

1. first, follow all the steps from the first tutorial to get the services and gui up and running

#. edit ``src/echolocator_api/databases/constants.py``

    Add a new field, following the pattern in the ``ImageFieldnames`` class.

#. edit ``src/echolocator_lib/databases/table_definitions.py``

    Add a new field, following the pattern in the ``RockmakerImagesTable`` class.

#. edit ``src/echolocator_lib/databases/database_definition.py``

    If you want to dynamically migrate this change to existing databases on the fly, 
    you can add code to the ``apply_revision`` method and change the ``self.LATEST_REVISION`` constant.

    If you don't add this dynamic code, you will have to delete your old databases.

#. edit ``src/echolocator_lib/composers/html.py``

    Add the column to the display, following the pattern.

#. change the json you send when updating the image

    Add ``"my_field": "something"`` to the json.



