import csv
import logging
from pathlib import Path

from bs4 import BeautifulSoup

# API constants.
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
class TestExport:
    def test(self, constants, logging_setup, output_directory):
        """ """

        configuration_file = "tests/configurations/service.yaml"
        ExportTester().main(
            constants,
            configuration_file,
            output_directory,
        )


# ----------------------------------------------------------------------------------------
class ExportTester(Base):
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

        self.__output_directory = output_directory

        await self.inject_plate(xchembku)

        self.__crystal_targets_directory = (
            Path(self.__output_directory) / "exports/crystal-targets"
        )

        self.__crystal_targets_directory.mkdir(parents=True)

        await self.__export_initial()

        crystal_wells = []

        # Inject some wells.
        crystal_wells.append(await self.inject(xchembku, False, False))
        crystal_wells.append(await self.inject(xchembku, True, True))
        crystal_wells.append(await self.inject(xchembku, True, False))
        crystal_wells.append(await self.inject(xchembku, True, True))
        crystal_wells.append(await self.inject(xchembku, True, True))
        crystal_wells.append(await self.inject(xchembku, True, False))

        await self.__export_wells(crystal_wells)

    # ----------------------------------------------------------------------------------------

    async def __export_initial(self):
        """ """

        request = {
            Keywords.COMMAND: Commands.EXPORT,
            "visit": self.visit,
            "barcode_filter": self.barcode,
        }

        response = await echolocator_guis_get_default().client_protocolj(
            request, cookies={}
        )

        # Expect confirmation message in response.
        assert "confirmation" in response
        assert "exported 0" in response["confirmation"]

        # Check the csv file got written with no lines.
        csv = (
            self.__crystal_targets_directory
            / f"{self.rockminer_collected_stem}_targets.csv"
        )

        assert csv.exists()
        assert csv.stat().st_size == 0

    # ----------------------------------------------------------------------------------------

    async def __export_wells(self, crystal_wells):
        """ """

        request = {
            Keywords.COMMAND: Commands.EXPORT,
            "visit": self.visit,
            "barcode_filter": self.barcode,
        }

        response = await echolocator_guis_get_default().client_protocolj(
            request, cookies={}
        )

        # Expect confirmation message in response.
        assert "confirmation" in response
        assert "exported 3" in response["confirmation"]

        # Check the csv file got written.
        csv_path = (
            self.__crystal_targets_directory
            / f"{self.rockminer_collected_stem}_targets.csv"
        )
        assert csv_path.exists()

        # Read the csv file into an array.
        rows = []
        with open(csv_path, "r", newline="") as csv_file:
            reader = csv.reader(csv_file)
            for row in reader:
                rows.append(row)

        # Check row count we read.
        assert len(rows) == 3

        # Check each row has 3 parts.
        for row in rows:
            assert len(row) == 3

        # Check the well positions are those that are considered "confirmed".
        assert rows[0][0] == "02A_1"
        assert int(rows[0][1]) == -198
        assert int(rows[0][2]) == -297
        assert rows[1][0] == "04A_1"
        assert int(rows[1][1]) == 2
        assert int(rows[1][2]) == -97
        assert rows[2][0] == "05A_1"
        assert int(rows[2][1]) == 102
        assert int(rows[2][2]) == 3
