# Use standard logging in this module.
import logging

# Types.
from echolocator_api.datafaces.constants import Types

# Exceptions.
from echolocator_api.exceptions import NotFound

# Class managing list of things.
from echolocator_api.things import Things

logger = logging.getLogger(__name__)

# -----------------------------------------------------------------------------------------
__default_echolocator_dataface = None


def echolocator_datafaces_set_default(echolocator_dataface):
    global __default_echolocator_dataface
    __default_echolocator_dataface = echolocator_dataface


def echolocator_datafaces_get_default():
    global __default_echolocator_dataface
    if __default_echolocator_dataface is None:
        raise RuntimeError("echolocator_datafaces_get_default instance is None")
    return __default_echolocator_dataface


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

        if class_type == Types.AIOHTTP:
            from echolocator_api.datafaces.aiohttp import Aiohttp

            return Aiohttp

        raise NotFound(
            "unable to get echolocator_dataface class for type %s" % (class_type)
        )
