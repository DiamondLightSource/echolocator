import logging

# Base class for an asyncio server context.
from dls_utilpack.server_context_base import ServerContextBase

# Things created in the context.
from echolocator_lib.guis.guis import Guis

logger = logging.getLogger(__name__)


thing_type = "echolocator_lib.echolocator_guis.context"


class Context(ServerContextBase):
    """
    Object representing an event echolocator_dataface connection.
    """

    # ----------------------------------------------------------------------------------------
    def __init__(self, specification):
        ServerContextBase.__init__(self, thing_type, specification)

    # ----------------------------------------------------------------------------------------
    async def aenter(self):
        """ """

        self.server = Guis().build_object(self.specification())

        if self.context_specification.get("start_as") == "coro":
            await self.server.activate_coro()

        elif self.context_specification.get("start_as") == "thread":
            await self.server.start_thread()

        elif self.context_specification.get("start_as") == "process":
            logger.debug("starting gui context")
            await self.server.start_process()

    # ----------------------------------------------------------------------------------------
    async def aexit(self, type, value, traceback):
        """ """
        logger.debug(f"[DISSHU] {thing_type} aexit")

        if self.server is not None:
            if self.context_specification.get("start_as") == "process":
                logger.debug(f"[DISSHU] {thing_type} calling client_shutdown")
                # Put in request to shutdown the server.
                await self.server.client_shutdown()

            if self.context_specification.get("start_as") == "coro":
                await self.server.direct_shutdown()
