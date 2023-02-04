# Use standard logging in this module.
import logging
import os

# Utilities.
from dls_utilpack.callsign import callsign
from dls_utilpack.require import require

# Exceptions.
from echolocator_api.exceptions import NotFound

# Class managing list of things.
from echolocator_api.things import Things

# Environment variables with some extra functionality.
from echolocator_lib.envvar import Envvar

logger = logging.getLogger(__name__)

# -----------------------------------------------------------------------------------------
__default_echolocator_configurator = None


def echolocator_configurators_set_default(echolocator_configurator):
    global __default_echolocator_configurator
    __default_echolocator_configurator = echolocator_configurator


def echolocator_configurators_get_default():
    global __default_echolocator_configurator
    if __default_echolocator_configurator is None:
        raise RuntimeError("echolocator_configurators_get_default instance is None")
    return __default_echolocator_configurator


def echolocator_configurators_has_default():
    global __default_echolocator_configurator
    return __default_echolocator_configurator is not None


# -----------------------------------------------------------------------------------------


class Configurators(Things):
    """
    Configuration loader.
    """

    # ----------------------------------------------------------------------------------------
    def __init__(self, name=None):
        Things.__init__(self, name)

    # ----------------------------------------------------------------------------------------
    def build_object(self, specification):
        """"""

        echolocator_configurator_class = self.lookup_class(
            require(f"{callsign(self)} specification", specification, "type")
        )

        try:
            echolocator_configurator_object = echolocator_configurator_class(
                specification
            )
        except Exception as exception:
            raise RuntimeError(
                "unable to instantiate echolocator_configurator object from module %s"
                % (echolocator_configurator_class.__module__)
            ) from exception

        return echolocator_configurator_object

    # ----------------------------------------------------------------------------------------
    def lookup_class(self, class_type):
        """"""

        if class_type == "echolocator_lib.echolocator_configurators.yaml":
            from echolocator_lib.configurators.yaml import Yaml

            return Yaml

        raise NotFound(
            "unable to get echolocator_configurator class for type %s" % (class_type)
        )

    # ----------------------------------------------------------------------------------------
    def build_object_from_environment(self, environ=None):

        # Get the explicit name of the config file.
        echolocator_configfile = Envvar(Envvar.ECHOLOCATOR_CONFIGFILE, environ=environ)

        # Config file is explicitly named?
        if echolocator_configfile.is_set:
            # Make sure the path exists.
            configurator_filename = echolocator_configfile.value
            if not os.path.exists(configurator_filename):
                raise RuntimeError(
                    f"unable to find {Envvar.ECHOLOCATOR_CONFIGFILE} {configurator_filename}"
                )
        # Config file is not explicitly named?
        else:
            raise RuntimeError(
                f"environment variable {Envvar.ECHOLOCATOR_CONFIGFILE} is not set"
            )

        echolocator_configurator = self.build_object(
            {
                "type": "echolocator_lib.echolocator_configurators.yaml",
                "type_specific_tbd": {"filename": configurator_filename},
            }
        )

        echolocator_configurator.substitute(
            {"configurator_directory": os.path.dirname(configurator_filename)}
        )

        return echolocator_configurator
