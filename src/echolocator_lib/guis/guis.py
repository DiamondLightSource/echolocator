# Use standard logging in this module.
import logging

# Class managing list of things.
from dls_utilpack.things import Things

# Exceptions.
from echolocator_api.exceptions import NotFound

# Types.
from echolocator_api.guis.constants import Types

logger = logging.getLogger(__name__)

# -----------------------------------------------------------------------------------------


class Guis(Things):
    """
    List of available echolocator_guis.
    """

    # ----------------------------------------------------------------------------------------
    def __init__(self, name=None):
        Things.__init__(self, name)

    # ----------------------------------------------------------------------------------------
    def build_object(self, specification):
        """"""

        echolocator_gui_class = self.lookup_class(specification["type"])

        try:
            echolocator_gui_object = echolocator_gui_class(specification)
        except Exception as exception:
            raise RuntimeError(
                "unable to build echolocator_gui object for type %s"
                % (echolocator_gui_class)
            ) from exception

        return echolocator_gui_object

    # ----------------------------------------------------------------------------------------
    def lookup_class(self, class_type):
        """"""

        if class_type == Types.AIOHTTP:
            from echolocator_lib.guis.aiohttp import Aiohttp

            return Aiohttp

        raise NotFound("unable to get echolocator_gui class for type %s" % (class_type))
