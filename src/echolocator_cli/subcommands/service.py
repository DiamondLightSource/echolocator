import asyncio

# Use standard logging in this module.
import logging

# Servbase context creator.
from dls_servbase_lib.datafaces.context import Context as DlsServbaseDatafaceContext

# Xchembku client context.
from xchembku_api.datafaces.context import Context as XchembkuDatafacesContext

# Things created in the context.
from echolocator_api.guis.guis import echolocator_guis_get_default

# Base class for cli subcommands.
from echolocator_cli.subcommands.base import ArgKeywords, Base

# Rockingest context creator.
from echolocator_lib.guis.context import Context as GuiContext

logger = logging.getLogger()


# --------------------------------------------------------------
class Service(Base):
    """
    Start single service and keep running until ^C or remotely requested shutdown.
    """

    def __init__(self, args, mainiac):
        super().__init__(args)

    # ----------------------------------------------------------------------------------------
    def run(self):
        """ """

        # Run in asyncio event loop.
        asyncio.run(self.__run_coro())

    # ----------------------------------------------------------
    async def __run_coro(self):
        """"""

        # Load the configuration.
        multiconf = self.get_multiconf(vars(self._args))
        configuration = await multiconf.load()

        async with XchembkuDatafacesContext(
            configuration["xchembku_dataface_specification"]
        ):
            # Make the servbase service context from the specification in the configuration.
            servbase_context = DlsServbaseDatafaceContext(
                configuration["dls_servbase_dataface_specification"]
            )

            # Open the servbase context which starts the service process.
            async with servbase_context:
                # Make the echolocator service context from the specification in the configuration.
                gui_context = GuiContext(configuration["echolocator_gui_specification"])

                # Open the echolocator context which starts the service process.
                async with gui_context:
                    logger.info(
                        f"starting web gui, please browse to {echolocator_guis_get_default().client_url()}/index.html"
                    )

                    # Wait for it to finish.
                    await gui_context.server.wait_for_shutdown()

    # ----------------------------------------------------------
    def add_arguments(parser):

        parser.add_argument(
            "--configuration",
            "-c",
            help="Configuration file.",
            type=str,
            metavar="yaml filename",
            default=None,
            dest=ArgKeywords.CONFIGURATION,
        )

        return parser
