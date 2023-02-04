import logging
import os
import tempfile

# Utilities.
from dls_utilpack.visit import get_visit_year

# Configurator.
from echolocator_lib.configurators.configurators import (
    Configurators,
    echolocator_configurators_set_default,
)

logger = logging.getLogger(__name__)


class Base:
    """
    Base class for femtocheck subcommands.  Handles details like configuration.
    """

    def __init__(self, args):
        self._args = args

        self.__temporary_directory = None

    # ----------------------------------------------------------------------------------------
    def get_configurator(self):

        echolocator_configurator = Configurators().build_object_from_environment()

        # For convenience, make a temporary directory for this test.
        self.__temporary_directory = tempfile.TemporaryDirectory()

        # Make the temporary directory available to the configurator.
        echolocator_configurator.substitute(
            {"temporary_directory": self.__temporary_directory.name}
        )

        substitutions = {
            "CWD": os.getcwd(),
            "HOME": os.environ.get("HOME", "HOME"),
            "USER": os.environ.get("USER", "USER"),
            "PATH": os.environ.get("PATH", "PATH"),
            "PYTHONPATH": os.environ.get("PYTHONPATH", "PYTHONPATH"),
        }

        if hasattr(self._args, "visit") and self._args.visit != "VISIT":
            BEAMLINE = os.environ.get("BEAMLINE")
            if BEAMLINE is None:
                raise RuntimeError("BEAMLINE environment variable is not defined")
            year = get_visit_year(BEAMLINE, self._args.visit)
            substitutions["BEAMLINE"] = BEAMLINE
            substitutions["VISIT"] = self._args.visit
            substitutions["YEAR"] = year

        echolocator_configurator.substitute(substitutions)

        # Set this as the default configurator so it is available everywhere.
        echolocator_configurators_set_default(echolocator_configurator)

        return echolocator_configurator
