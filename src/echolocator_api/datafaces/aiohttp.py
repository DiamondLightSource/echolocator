import logging

# Class for an aiohttp client.
from echolocator_api.aiohttp_client import AiohttpClient

# Dataface protocolj things.
from echolocator_api.datafaces.constants import Commands, Keywords

logger = logging.getLogger(__name__)


# ------------------------------------------------------------------------------------------
class Aiohttp:
    """
    Object implementing client side API for talking to the echolocator_dataface server.
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
    async def query(self, sql, subs=None, why=None):
        """"""
        return await self.__send_protocolj("query", sql, subs=subs, why=why)

    # ----------------------------------------------------------------------------------------
    async def execute(self, sql, subs=None, why=None):
        """"""
        return await self.__send_protocolj("execute", sql, subs=subs, why=why)

    # ----------------------------------------------------------------------------------------
    async def insert(self, table_name, records, why=None):
        """"""
        return await self.__send_protocolj("insert", table_name, records, why=why)

    # ----------------------------------------------------------------------------------------
    async def update(self, table_name, record, where, subs=None, why=None):
        """"""
        return await self.__send_protocolj(
            "update", table_name, record, where, subs=subs, why=why
        )

    # ----------------------------------------------------------------------------------------
    async def update_image(self, record, why=None):
        """"""

        return await self.__send_protocolj("update_image", record, why=why)

    # ----------------------------------------------------------------------------------------
    async def report_health(self):
        """"""
        return await self.__send_protocolj("report_health")

    # ----------------------------------------------------------------------------------------
    async def set_cookie(self, cookie_dict):
        """ """
        return await self.__send_protocolj("set_cookie", cookie_dict)

    # ----------------------------------------------------------------------------------------
    async def get_cookie(self, cookie_uuid):
        """
        Get single cookie from its uuid.
        Returns database record format.
        """
        return await self.__send_protocolj("get_cookie", cookie_uuid)

    # ----------------------------------------------------------------------------------------
    async def update_cookie(self, row):
        """"""
        return await self.__send_protocolj("update_cookie", row)

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
