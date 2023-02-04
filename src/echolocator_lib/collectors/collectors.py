# Use standard logging in this module.
import logging

# Exceptions.
from echolocator_api.exceptions import NotFound

# Class managing list of things.
from echolocator_api.things import Things

logger = logging.getLogger(__name__)

# -----------------------------------------------------------------------------------------
__default_collector = None


def collectors_set_default(collector):
    global __default_collector
    __default_collector = collector


def collectors_get_default():
    global __default_collector
    if __default_collector is None:
        raise RuntimeError("collectors_get_default instance is None")
    return __default_collector


class Collectors(Things):
    """
    List of available collectors.
    """

    # ----------------------------------------------------------------------------------------
    def __init__(self, name="collectors"):
        Things.__init__(self, name)

    # ----------------------------------------------------------------------------------------
    def build_object(self, specification, predefined_uuid=None):
        """"""

        collector_class = self.lookup_class(specification["type"])

        try:
            collector_object = collector_class(
                specification, predefined_uuid=predefined_uuid
            )
        except Exception as exception:
            raise RuntimeError(
                "unable to build collector object of class %s"
                % (collector_class.__name__)
            ) from exception

        return collector_object

    # ----------------------------------------------------------------------------------------
    def lookup_class(self, class_type):
        """"""

        if class_type == "dls_echolocator_lib.echolocator_collectors.aiohttp":
            from echolocator_lib.collectors.aiohttp import Aiohttp

            return Aiohttp

        elif class_type == "dls_echolocator_lib.echolocator_collectors.manual":
            from echolocator_lib.collectors.manual import Manual

            return Manual

        elif (
            class_type
            == "dls_echolocator_lib.echolocator_collectors.scrape_to_database"
        ):
            from echolocator_lib.collectors.scrape_to_database import ScrapeToDatabase

            return ScrapeToDatabase

        else:
            try:
                RuntimeClass = Things.lookup_class(self, class_type)
                return RuntimeClass
            except NotFound:
                raise NotFound("unable to get collector class for %s" % (class_type))
