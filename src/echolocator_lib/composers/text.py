import logging

# Base class for generic things.
from echolocator_api.thing import Thing

# Class to do the work using prettytable.
from echolocator_lib.composers.prettyhelper import PrettyHelper

logger = logging.getLogger(__name__)

thing_type = "echolocator_lib.echolocator_composers.text"


class Text(Thing):
    """ """

    # ----------------------------------------------------------------------------------------
    def __init__(self, specification=None):
        Thing.__init__(self, thing_type, specification)

        self.__prettyhelper = PrettyHelper()
