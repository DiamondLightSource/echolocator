import logging

# Class for an aiohttp client.
from echolocator_api.aiohttp_client import AiohttpClient

# Dataface protocolj things.
from echolocator_api.guis.constants import Commands, Keywords

logger = logging.getLogger(__name__)


# ------------------------------------------------------------------------------------------
class Aiohttp:
    """
    Object implementing client side API for talking to the echolocator_gui server.
    Please see doctopic [A01].
    """

    # ----------------------------------------------------------------------------------------
    def __init__(self, specification=None):
        self.__specification = specification

        self.__aiohttp_client = AiohttpClient(
            specification["type_specific_tbd"]["aiohttp_specification"],
        )

    # ----------------------------------------------------------------------------------------
    def specification(self):
        return self.__specification

    # ----------------------------------------------------------------------------------------
    async def report_health(self):
        """"""
        return await self.__send_protocolj("report_health")

    # ----------------------------------------------------------------------------------------
    async def __send_protocolj(self, function, *args, **kwargs):
        """"""

        return await self.__aiohttp_client.client_protocolj(
            {
                Keywords.COMMAND: Commands.EXECUTE,
                Keywords.PAYLOAD: {
                    "function": function,
                    "args": args,
                    "kwargs": kwargs,
                },
            },
        )

    # ----------------------------------------------------------------------------------------
    async def close_client_session(self):
        """"""

        if self.__aiohttp_client is not None:
            await self.__aiohttp_client.close_client_session()

    # ----------------------------------------------------------------------------------------
    async def client_report_health(self):
        """"""

        return await self.__aiohttp_client.client_report_health()
