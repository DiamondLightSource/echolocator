# Use standard logging in this module.
import logging

# Exceptions.
from echolocator_api.exceptions import NotFound

# Class managing list of things.
from echolocator_api.things import Things

logger = logging.getLogger(__name__)


# -----------------------------------------------------------------------------------------


class Datafaces(Things):
    """
    List of available echolocator_datafaces.
    """

    # ----------------------------------------------------------------------------------------
    def __init__(self, name=None):
        Things.__init__(self, name)

    # ----------------------------------------------------------------------------------------
    def build_object(self, specification):
        """"""

        echolocator_dataface_class = self.lookup_class(specification["type"])

        try:
            echolocator_dataface_object = echolocator_dataface_class(specification)
        except Exception as exception:
            raise RuntimeError(
                "unable to build echolocator_dataface object for type %s"
                % (echolocator_dataface_class)
            ) from exception

        return echolocator_dataface_object

    # ----------------------------------------------------------------------------------------
    def lookup_class(self, class_type):
        """"""

        if class_type == "echolocator_lib.echolocator_datafaces.aiohttp":
            from echolocator_lib.datafaces.aiohttp import Aiohttp

            return Aiohttp

        elif class_type == "echolocator_lib.echolocator_datafaces.aiosqlite":
            from echolocator_lib.datafaces.aiosqlite import Aiosqlite

            return Aiosqlite

        raise NotFound(
            "unable to get echolocator_dataface class for type %s" % (class_type)
        )
