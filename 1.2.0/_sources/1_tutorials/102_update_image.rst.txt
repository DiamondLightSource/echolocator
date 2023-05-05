Update an image
=========================================================================================

This tutorial takes you through the steps to programmatically update an image record in the database.

This is an operation typically carried out when new information is discovered about an image, such as its crystal locations.


1. first, follow all the steps from the first tutorial to get the services and gui up and running


#. make a small python program, called tutorial2.py::
        
        # This tutorial program shows you how to update an image record.

        import json
        import asyncio
        from echolocator_api.datafaces.context import Context
        from echolocator_api.datafaces.constants import Types
        from echolocator_api.databases.constants import ImageFieldnames

        # Specify the client type and remote endpoint.
        client_specification = {
            "type": Types.AIOHTTP,
            "type_specific_tbd": {
                "aiohttp_specification": {"client": "http://localhost:27621"}
            },
        }


        async def tutorial():
            async with Context(client_specification) as client_interface:
                # This is the request which is sent to update the image.
                request = {
                    "filename": ".*/example_images/1.jpg", 
                    ImageFieldnames.CRYSTAL_PROBABILITY: 0.9}

                # Send the request to the server and get the response.
                response = await client_interface.update_image(request)

                # Show the response, which is None if success, otherwise a dict with errors in it.
                print(json.dumps(response, indent=4))


        asyncio.run(tutorial())

#. execute your program

    ::

        python3 tutorial2.py

    you should see::

            {
                "count": 1
            }

#. verify in the gui::

        Click on the Image List tab.
        
        You should see the 0.9 in the crystal probability column for 1.jpg.