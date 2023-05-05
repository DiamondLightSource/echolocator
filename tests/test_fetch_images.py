import logging
from pathlib import Path

from bs4 import BeautifulSoup

# API constants.
from dls_servbase_api.constants import Keywords as ProtocoljKeywords
from dls_servbase_lib.datafaces.context import Context as DlsServbaseDatafaceContext

# Utilities.
from dls_utilpack.describe import describe

# Things xchembku provides.
from xchembku_api.datafaces.context import Context as XchembkuDatafaceClientContext
from xchembku_api.datafaces.datafaces import xchembku_datafaces_get_default

# Client context creator.
from echolocator_api.guis.context import Context as GuiClientContext

# GUI constants.
from echolocator_lib.guis.constants import Commands, Cookies, Keywords

# Server context creator.
from echolocator_lib.guis.context import Context as GuiServerContext

# Object managing gui
from echolocator_lib.guis.guis import echolocator_guis_get_default

# Base class for the tester.
from tests.base import Base

logger = logging.getLogger(__name__)


# ----------------------------------------------------------------------------------------
class TestFetchImages:
    def test(self, constants, logging_setup, output_directory):
        """ """

        configuration_file = "tests/configurations/service.yaml"
        FetchImagesTester().main(
            constants,
            configuration_file,
            output_directory,
        )


# ----------------------------------------------------------------------------------------
class FetchImagesTester(Base):
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

        # Make the xchembku client context, expected to be direct (no server).
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

        # Start the client context for the direct access to the xchembku.
        async with xchembku_client_context:
            # Start the dataface the gui uses for cookies.
            async with servbase_dataface_context:
                # Start the gui client context.
                async with gui_client_context:
                    # And the gui server context which starts the coro.
                    async with gui_server_context:
                        await self.__run_part1(constants, output_directory)

    # ----------------------------------------------------------------------------------------

    async def __run_part1(self, constants, output_directory):
        """ """
        # Reference the xchembku object which the context has set up as the default.
        xchembku = xchembku_datafaces_get_default()

        await self.__request_initial()

        crystal_wells = []

        # Inject some wells.
        crystal_wells.append(await self.inject(xchembku, False, False))
        crystal_wells.append(await self.inject(xchembku, True, True))
        crystal_wells.append(await self.inject(xchembku, True, False))
        crystal_wells.append(await self.inject(xchembku, True, True))
        crystal_wells.append(await self.inject(xchembku, True, True))
        crystal_wells.append(await self.inject(xchembku, True, False))

        await self.__request_all(crystal_wells)

    # ----------------------------------------------------------------------------------------

    async def __request_initial(self):
        """ """

        request = {
            ProtocoljKeywords.ENABLE_COOKIES: [
                Cookies.IMAGE_LIST_UX,
            ],
            Keywords.COMMAND: Commands.FETCH_IMAGE_LIST,
        }

        response = await echolocator_guis_get_default().client_protocolj(
            request, cookies={}
        )

        logger.debug(describe("first fetch_image response", response))

        soup = BeautifulSoup(response["html"], "html.parser")

        # Find the table element.
        table = soup.find("table")

        # Count the number of rows in the table.
        row_count = len(table.find_all("tr"))

        # The table contains only the header and no data rows.
        assert row_count == 1 + 0

    # ----------------------------------------------------------------------------------------

    async def __request_all(self, crystal_wells):
        """ """

        request = {
            ProtocoljKeywords.ENABLE_COOKIES: [
                Cookies.IMAGE_LIST_UX,
            ],
            Keywords.COMMAND: Commands.FETCH_IMAGE_LIST,
        }

        response = await echolocator_guis_get_default().client_protocolj(
            request, cookies={}
        )

        logger.debug(describe("fetch_image response", response))

        soup = BeautifulSoup(response["html"], "html.parser")

        # Find the table element.
        table = soup.find("table")

        # Count the number of rows in the table.
        rows = table.find_all("tr")

        # Assert that the row count is equal to the expected value.
        assert len(rows) == 1 + 5

        # Check the first row's filename.
        # Remember fiels are injected with increasing crystal counts,
        # so default sorting is in reverse order.
        row = rows[1]
        columns = row.find_all(class_="T_filename")
        assert len(columns) == 1
        assert columns[0].get_text() == Path(crystal_wells[5].filename).stem

        # Check the last row's filename.
        row = rows[5]
        columns = row.find_all(class_="T_filename")
        assert len(columns) == 1
        assert columns[0].get_text() == Path(crystal_wells[1].filename).stem
