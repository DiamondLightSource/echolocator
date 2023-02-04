import logging

# Contexts.
from dls_servbase_lib.datafaces.context import Context as DlsServbaseDatafaceContext
from dls_utilpack.callsign import callsign

# Utilities.
from dls_utilpack.explain import explain

from echolocator_lib.collectors.context import Context as CollectorContext

# Base class which maps flask requests to methods.
from echolocator_lib.contexts.base import Base
from echolocator_lib.datafaces.context import Context as DatafaceContext
from echolocator_lib.guis.context import Context as GuiContext

logger = logging.getLogger(__name__)


thing_type = "echolocator_lib.echolocator_contexts.classic"


class Classic(Base):
    """
    Object representing all the possible contexts.
    """

    # ----------------------------------------------------------------------------------------
    def __init__(self, specification):
        Base.__init__(self, thing_type, specification)

        self.__dls_servbase_dataface = None
        self.__dataface = None
        self.__collector = None
        self.__gui = None

    # ----------------------------------------------------------------------------------------
    async def __dead_or_alive(self, context, dead, alive):

        if context is not None:
            try:
                # A server was defined for this context?
                if await context.is_process_started():
                    if await context.is_process_alive():
                        alive.append(context)
                    else:
                        dead.append(context)
            except Exception:
                raise RuntimeError(
                    f"unable to determine dead or alive for context {callsign(context)}"
                )

    # ----------------------------------------------------------------------------------------
    async def __dead_or_alive_all(self):
        """
        Return two lists, one for dead and one for alive processes.
        TODO: Parallelize context process alive/dead checking.
        """

        dead = []
        alive = []

        await self.__dead_or_alive(self.__dls_servbase_dataface, dead, alive)
        await self.__dead_or_alive(self.__dataface, dead, alive)
        await self.__dead_or_alive(self.__collector, dead, alive)
        await self.__dead_or_alive(self.__gui, dead, alive)

        return dead, alive

    # ----------------------------------------------------------------------------------------
    async def is_any_process_alive(self):
        """
        Check all configured processes, return if any alive.
        """
        dead, alive = await self.__dead_or_alive_all()

        # logger.debug(f"[PIDAL] {len(dead)} processes are dead, {len(alive)} are alive")

        return len(alive) > 0

    # ----------------------------------------------------------------------------------------
    async def is_any_process_dead(self):
        """
        Check all configured processes, return if any alive.
        """
        dead, alive = await self.__dead_or_alive_all()

        return len(dead) > 0

    # ----------------------------------------------------------------------------------------
    async def __aenter__(self):
        """ """
        logger.debug(f"entering {callsign(self)} context")

        try:

            try:
                specification = self.specification().get(
                    "dls_servbase_dataface_specification"
                )
                if specification is not None:
                    logger.debug(
                        f"at entering position {callsign(self)} DLS_BILLY DATAFACE"
                    )
                    self.__dls_servbase_dataface = DlsServbaseDatafaceContext(
                        specification
                    )
                    await self.__dls_servbase_dataface.aenter()
                else:
                    logger.debug(
                        f"no specification in {callsign(self)} for DLS_BILLY DATAFACE"
                    )
            except Exception as exception:
                raise RuntimeError(
                    explain(
                        exception,
                        f"creating {callsign(self)} dls_servbase_dataface context",
                    )
                )

            try:
                specification = self.specification().get(
                    "echolocator_dataface_specification"
                )
                if specification is not None:
                    logger.debug(
                        f"at entering position {callsign(self)} ECHOLOCATOR DATAFACE"
                    )
                    self.__dataface = DatafaceContext(specification)
                    await self.__dataface.aenter()
            except Exception as exception:
                raise RuntimeError(
                    explain(exception, f"creating {callsign(self)} dataface context")
                )

            try:
                specification = self.specification().get(
                    "echolocator_collector_specification"
                )
                if specification is not None:
                    logger.debug(f"at entering position {callsign(self)} COLLECTOR")
                    self.__collector = CollectorContext(specification)
                    await self.__collector.aenter()
            except Exception as exception:
                raise RuntimeError(
                    explain(exception, f"creating {callsign(self)} collector context")
                )

            try:
                specification = self.specification().get(
                    "echolocator_gui_specification"
                )
                if specification is not None:
                    logger.debug(f"at entering position {callsign(self)} GUI")
                    self.__gui = GuiContext(specification)
                    await self.__gui.aenter()
            except Exception as exception:
                raise RuntimeError(
                    explain(exception, f"creating {callsign(self)} gui context")
                )

        except Exception as exception:
            await self.aexit()
            raise RuntimeError(explain(exception, f"entering {callsign(self)} context"))

        logger.debug(f"entered {callsign(self)} context")

    # ----------------------------------------------------------------------------------------
    async def __aexit__(self, type, value, traceback):
        """ """

        await self.aexit()

    # ----------------------------------------------------------------------------------------
    async def aexit(self):
        """ """

        logger.debug(f"exiting {callsign(self)} context")

        if self.__gui is not None:
            logger.debug(f"at exiting position {callsign(self)} GUI")
            try:
                await self.__gui.aexit()
            except Exception as exception:
                logger.error(
                    explain(exception, f"exiting {callsign(self.__gui)} context"),
                    exc_info=exception,
                )
            self.__gui = None

        if self.__collector is not None:
            logger.debug(f"at exiting position {callsign(self)} COLLECTOR")
            try:
                await self.__collector.aexit()
            except Exception as exception:
                logger.error(
                    explain(exception, f"exiting {callsign(self.__collector)} context"),
                    exc_info=exception,
                )
            self.__collector = None

        if self.__dataface is not None:
            logger.debug(f"at exiting position {callsign(self)} DATAFACE")
            try:
                await self.__dataface.aexit()
            except Exception as exception:
                logger.error(
                    explain(exception, f"exiting {callsign(self.__dataface)} context"),
                    exc_info=exception,
                )
            self.__dataface = None

        if self.__dls_servbase_dataface is not None:
            logger.debug(f"at exiting position {callsign(self)} DLS_BILLY DATAFACE")
            try:
                await self.__dls_servbase_dataface.aexit()
            except Exception as exception:
                logger.error(
                    explain(
                        exception,
                        f"exiting {callsign(self.__dls_servbase_dataface)} context",
                    ),
                    exc_info=exception,
                )
            self.__datafa__dls_servbase_datafacece = None

        logger.debug(f"exited {callsign(self)} context")
