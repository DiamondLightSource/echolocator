# Use standard logging in this module.
import logging

import yaml

# Exceptions.
from echolocator_api.exceptions import NotFound

# Class managing list of things.
from echolocator_api.things import Things

logger = logging.getLogger(__name__)

# -----------------------------------------------------------------------------------------


class Contexts(Things):
    """
    Context loader.
    """

    # ----------------------------------------------------------------------------------------
    def __init__(self, name=None):
        Things.__init__(self, name)

    # ----------------------------------------------------------------------------------------
    def build_object(self, specification):
        """"""

        if not isinstance(specification, dict):
            with open(specification, "r") as yaml_stream:
                specification = yaml.safe_load(yaml_stream)

        echolocator_context_class = self.lookup_class(specification["type"])

        try:
            echolocator_context_object = echolocator_context_class(specification)
        except Exception as exception:
            raise RuntimeError(
                "unable to build echolocator_context object for type %s"
                % (echolocator_context_class)
            ) from exception

        return echolocator_context_object

    # ----------------------------------------------------------------------------------------
    def lookup_class(self, class_type):
        """"""

        if class_type == "echolocator_lib.echolocator_contexts.classic":
            from echolocator_lib.contexts.classic import Classic

            return Classic

        raise NotFound(
            "unable to get echolocator_context class for type %s" % (class_type)
        )
