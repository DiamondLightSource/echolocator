import logging
import multiprocessing
import threading

# Utilities.
from dls_utilpack.callsign import callsign
from dls_utilpack.explain import explain
from dls_utilpack.require import require

# Dataface protocolj things.
from echolocator_api.datafaces.constants import Commands, Keywords

# Basic things.
from echolocator_api.thing import Thing

# Base class for an aiohttp server.
from echolocator_lib.base_aiohttp import BaseAiohttp

# Types of echolocator_dataface.
# Global echolocator_dataface.
from echolocator_lib.datafaces.datafaces import Datafaces

logger = logging.getLogger(__name__)

thing_type = "echolocator_lib.echolocator_datafaces.aiohttp"


# ------------------------------------------------------------------------------------------
class Aiohttp(Thing, BaseAiohttp):
    """
    Object implementing remote procedure calls for echolocator_dataface methods.
    """

    # ----------------------------------------------------------------------------------------
    def __init__(self, specification=None):
        Thing.__init__(self, thing_type, specification)
        BaseAiohttp.__init__(
            self,
            specification["type_specific_tbd"]["aiohttp_specification"],
        )

        self.__actual_echolocator_dataface = None

    # ----------------------------------------------------------------------------------------
    def callsign(self):
        """"""
        return "%s %s" % ("Dataface.Aiohttp", BaseAiohttp.callsign(self))

    # ----------------------------------------------------------------------------------------
    def activate_process(self):
        """"""

        try:
            multiprocessing.current_process().name = "dataface"

            self.activate_process_base()

        except Exception as exception:
            logger.exception(
                f"unable to start {callsign(self)} process", exc_info=exception
            )

    # ----------------------------------------------------------------------------------------
    def activate_thread(self, loop):
        """
        Called from inside a newly created thread.
        """

        try:
            threading.current_thread().name = "echolocator_dataface"

            self.activate_thread_base(loop)

        except Exception as exception:
            logger.exception(
                f"unable to start {callsign(self)} thread", exc_info=exception
            )

    # ----------------------------------------------------------------------------------------
    async def activate_coro(self):
        """"""
        try:
            # No special routes, we will use protocolj dispathcing only
            route_tuples = []

            # Build a local echolocator_dataface for our back-end.
            self.__actual_echolocator_dataface = Datafaces().build_object(
                self.specification()["type_specific_tbd"][
                    "actual_echolocator_dataface_specification"
                ]
            )

            # Get the local implementation started.
            await self.__actual_echolocator_dataface.start()

            await self.activate_coro_base(route_tuples)

        except Exception:
            raise RuntimeError(f"unable to start {callsign(self)} server coro")

    # ----------------------------------------------------------------------------------------
    async def direct_shutdown(self):
        """"""
        try:
            # Disconnect our local dataface connection, i.e. the one which holds the database connection.
            await self.__actual_echolocator_dataface.disconnect()

        except Exception as exception:
            raise RuntimeError(
                callsign(
                    self,
                    explain(exception, "disconnecting local echolocator_dataface"),
                )
            )

        # Let the base class stop the server listener.
        await self.base_direct_shutdown()

    # ----------------------------------------------------------------------------------------
    async def __do_actually(self, function, args, kwargs):
        """"""

        # logger.info(describe("function", function))
        # logger.info(describe("args", args))
        # logger.info(describe("kwargs", kwargs))

        function = getattr(self.__actual_echolocator_dataface, function)

        response = await function(*args, **kwargs)

        return response

    # ----------------------------------------------------------------------------------------
    async def dispatch(self, request_dict, opaque):
        """"""

        # logger.debug(describe(f"{callsign(self)} request", request_dict))

        command = require("request json", request_dict, Keywords.COMMAND)

        if command == Commands.EXECUTE:
            payload = require("request json", request_dict, Keywords.PAYLOAD)
            response = await self.__do_actually(
                payload["function"], payload["args"], payload["kwargs"]
            )
        else:
            raise RuntimeError("invalid command %s" % (command))

        return response
