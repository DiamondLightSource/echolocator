import logging

import pytest

# API constants.
from dls_servbase_api.constants import Keywords as ProtocoljKeywords
from dls_servbase_lib.datafaces.context import Context as DlsServbaseDatafaceContext

# Utilities.
from dls_utilpack.exceptions import EndOfList, ProgrammingFault

# Things xchembku provides.
from xchembku_api.datafaces.context import Context as XchembkuDatafaceClientContext
from xchembku_api.datafaces.datafaces import xchembku_datafaces_get_default
from xchembku_lib.datafaces.context import Context as XchembkuDatafaceServerContext

# Client context creator.
from echolocator_api.guis.context import Context as GuiClientContext

# Object managing gui
from echolocator_api.guis.guis import echolocator_guis_get_default

# GUI constants.
from echolocator_lib.guis.constants import Commands, Cookies, Keywords

# Server context creator.
from echolocator_lib.guis.context import Context as GuiServerContext

# Base class for the tester.
from tests.base import Base

logger = logging.getLogger(__name__)


# ----------------------------------------------------------------------------------------
class TestFetchImage:
    def test(self, constants, logging_setup, output_directory):
        """ """

        configuration_file = "tests/configurations/service.yaml"
        FetchImageTester().main(
            constants,
            configuration_file,
            output_directory,
        )


# ----------------------------------------------------------------------------------------
class FetchImageTester(Base):
    """
    Class to test the gui fetch_image endpoint.
    """

    async def _main_coroutine(self, constants, output_directory):
        """ """

        multiconf = self.get_multiconf()
        multiconf_dict = await multiconf.load()

        # Reference the dict entry for the xchembku dataface.
        xchembku_dataface_specification = multiconf_dict[
            "xchembku_dataface_specification"
        ]

        # Make the xchembku server context.
        xchembku_server_context = XchembkuDatafaceServerContext(
            xchembku_dataface_specification
        )
        # Make the xchembku client context.
        xchembku_client_context = XchembkuDatafaceClientContext(
            xchembku_dataface_specification
        )

        servbase_dataface_specification = multiconf_dict[
            "dls_servbase_dataface_specification"
        ]
        servbase_dataface_context = DlsServbaseDatafaceContext(
            servbase_dataface_specification
        )

        gui_specification = multiconf_dict["echolocator_gui_specification"]
        # Make the server context.
        gui_server_context = GuiServerContext(gui_specification)

        # Make the client context.
        gui_client_context = GuiClientContext(gui_specification)

        # Start the client context for the remote access to the xchembku.
        async with xchembku_client_context:
            # Start the server context xchembku which starts the process.
            async with xchembku_server_context:
                # Start the dataface the gui uses for cookies.
                async with servbase_dataface_context:
                    # Start the gui client context.
                    async with gui_client_context:
                        # And the gui server context which starts the coro.
                        async with gui_server_context:
                            await self.__run_the_test(constants, output_directory)

    # ----------------------------------------------------------------------------------------

    async def __run_the_test(self, constants, output_directory):
        """ """
        # Reference the xchembku object which the context has set up as the default.
        xchembku = xchembku_datafaces_get_default()

        self.__cookies = {}

        # Error when no index given in the request.
        # await self.__request_error_no_index()

        # Query for a list, which will be zero length because there are no wells injected yet.
        # await self.__fetch_image_list()

        # Error when requesting from empty list.
        # await self.__request_from_empty_list()

        crystal_wells = []

        # Inject some wells.
        crystal_wells.append(await self.inject(xchembku, False, False))
        crystal_wells.append(await self.inject(xchembku, True, True))
        crystal_wells.append(await self.inject(xchembku, True, False))
        crystal_wells.append(await self.inject(xchembku, True, True))
        crystal_wells.append(await self.inject(xchembku, True, True))
        crystal_wells.append(await self.inject(xchembku, True, False))

        # Make a list which is no longer empty.
        await self.__fetch_image_list()

        await self.__request_anchor(crystal_wells)

    # ----------------------------------------------------------------------------------------

    async def __request_error_no_index(self):
        """ """

        request = {
            ProtocoljKeywords.ENABLE_COOKIES: [
                Cookies.IMAGE_EDIT_UX,
                Cookies.IMAGE_LIST_UX,
            ],
            Keywords.COMMAND: Commands.FETCH_IMAGE,
        }

        with pytest.raises(ProgrammingFault) as excinfo:
            await echolocator_guis_get_default().client_protocolj(
                request,
                cookies=self.__cookies,
            )

        assert f"no value for {Keywords.CRYSTAL_WELL_INDEX}" in str(excinfo.value)

    # ----------------------------------------------------------------------------------------

    async def __request_from_empty_list(self):
        """ """

        request = {
            ProtocoljKeywords.ENABLE_COOKIES: [
                Cookies.IMAGE_EDIT_UX,
                Cookies.IMAGE_LIST_UX,
            ],
            Keywords.COMMAND: Commands.FETCH_IMAGE,
            Keywords.CRYSTAL_WELL_INDEX: 1,
        }

        with pytest.raises(EndOfList):
            await echolocator_guis_get_default().client_protocolj(
                request,
                cookies=self.__cookies,
            )

    # ----------------------------------------------------------------------------------------

    async def __fetch_image_list(self):
        """ """

        logger.debug("[AT] ----------------- requesting image list -----------------")

        request = {
            ProtocoljKeywords.ENABLE_COOKIES: [
                Cookies.IMAGE_LIST_UX,
            ],
            Keywords.COMMAND: Commands.FETCH_IMAGE_LIST,
            "visit_filter": self.visit,
        }

        response = await echolocator_guis_get_default().client_protocolj(
            request, cookies=self.__cookies
        )

        # Pick up the cookies established by the list query.
        self.__cookies = response["__cookies"]

    # ----------------------------------------------------------------------------------------

    async def __request_anchor(self, crystal_wells):
        """ """

        logger.debug("[AT] ----------------- requesting anchor -----------------")
        request = {
            ProtocoljKeywords.ENABLE_COOKIES: [
                Cookies.IMAGE_EDIT_UX,
                Cookies.IMAGE_LIST_UX,
            ],
            Keywords.COMMAND: Commands.FETCH_IMAGE,
            Keywords.CRYSTAL_WELL_INDEX: 2,  # B01a
        }

        response = await echolocator_guis_get_default().client_protocolj(
            request,
            cookies=self.__cookies,
        )

        # Keep now we have both cookies.
        self.__cookies = response["__cookies"]

        record = response["record"]
        assert record is not None
        assert record["position"] == "B01a"

        # -------------------------------------------------------------------------------------
        # Same query again, but rely on cookie for index.
        request.pop(Keywords.CRYSTAL_WELL_INDEX)

        response = await echolocator_guis_get_default().client_protocolj(
            request,
            cookies=self.__cookies,
        )

        record = response["record"]
        assert record["position"] == "B01a"
