import logging

logger = logging.getLogger(__name__)


class ContextBase:
    """ """

    # ----------------------------------------------------------------------------------------
    def __init__(self, specification):
        self.__specification = specification
        self.__interface = None

    # ----------------------------------------------------------------------------------------
    def get_interface(self):
        return self.__interface

    def set_interface(self, interface):
        self.__interface = interface

    interface = property(get_interface, set_interface)

    # ----------------------------------------------------------------------------------------
    async def __aenter__(self):
        """ """

        await self.aenter()

        return self.interface

    # ----------------------------------------------------------------------------------------
    async def __aexit__(self, type, value, traceback):
        """ """

        await self.aexit()
