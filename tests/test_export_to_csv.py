import csv
import logging
from pathlib import Path

# API constants.
from dls_servbase_lib.datafaces.context import Context as DlsServbaseDatafaceContext
from dls_utilpack.visit import get_xchem_subdirectory

# Things xchembku provides.
from xchembku_api.datafaces.context import Context as XchembkuDatafaceClientContext
from xchembku_api.datafaces.datafaces import xchembku_datafaces_get_default
from xchembku_lib.datafaces.context import Context as XchembkuDatafaceServerContext

# Client context creator.
from echolocator_api.guis.context import Context as GuiClientContext

# Object managing gui
from echolocator_api.guis.guis import echolocator_guis_get_default

# GUI constants.
from echolocator_lib.guis.constants import Commands, Keywords

# Server context creator.
from echolocator_lib.guis.context import Context as GuiServerContext

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
                            await self.__run_part1(constants, output_directory)

    # ----------------------------------------------------------------------------------------

    async def __run_part1(self, constants, output_directory):
        """ """

        # Reference the xchembku object which the context has set up as the default.
        self.__xchembku = xchembku_datafaces_get_default()

        self.__output_directory = output_directory

        self.__visit_directory = (
            Path(self.__output_directory)
            / "labxchem"
            / get_xchem_subdirectory(self.visit)
        )

        self.__crystal_targets_directory = (
            self.__visit_directory / "processing/lab36/crystal-targets"
        )

        self.__crystal_targets_directory.mkdir(parents=True)

        # ----------------------------------------------------------------

        crystal_wells = []

        # Inject first plate.
        await self.inject_plate(self.__xchembku)

        # Inject some wells on the first plate.
        crystal_wells.append(await self.inject(self.__xchembku, False, False))
        crystal_wells.append(await self.inject(self.__xchembku, True, True))
        crystal_wells.append(await self.inject(self.__xchembku, True, False))
        crystal_wells.append(await self.inject(self.__xchembku, True, True))
        crystal_wells.append(await self.inject(self.__xchembku, True, True))
        crystal_wells.append(await self.inject(self.__xchembku, True, False))

        # Inject second plate.
        await self.inject_plate(self.__xchembku)

        # Inject some more wells on the second plate.
        crystal_wells.append(await self.inject(self.__xchembku, False, False))
        crystal_wells.append(await self.inject(self.__xchembku, True, True))
        crystal_wells.append(await self.inject(self.__xchembku, True, False))
        crystal_wells.append(await self.inject(self.__xchembku, True, True))
        crystal_wells.append(await self.inject(self.__xchembku, True, True))
        crystal_wells.append(await self.inject(self.__xchembku, True, False))

        await self.__export_wells(crystal_wells)

    # ----------------------------------------------------------------------------------------

    async def __export_wells(self, crystal_wells):
        """ """

        request = {
            Keywords.COMMAND: Commands.EXPORT_TO_CSV,
            "visit_filter": self.visit,
        }

        response = await echolocator_guis_get_default().client_protocolj(
            request, cookies={}
        )

        # Expect confirmation message in response.
        assert "confirmation" in response
        # There will be two of "exported 3" since there are two plates.
        assert "exported 3" in response["confirmation"]
        # The confirmation should say what files got written.
        assert (
            self.crystal_plate_models[0].rockminer_collected_stem
            in response["confirmation"]
        )
        assert (
            self.crystal_plate_models[1].rockminer_collected_stem
            in response["confirmation"]
        )

        # Check the first csv file got written.
        csv_path = (
            self.__crystal_targets_directory
            / f"{self.crystal_plate_models[0].rockminer_collected_stem}_targets.csv"
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
        # The position constants are fromt the Swiss3 microns computation.
        # Note the order here: row_first_position gives get all letters in row 01 before any letters in row 02.
        assert rows[0][0] == "B01a"
        assert int(rows[0][1]) == 6
        assert int(rows[0][2]) == -274

        assert rows[1][0] == "A02a"
        assert int(rows[1][1]) == -561
        assert int(rows[1][2]) == -842

        assert rows[2][0] == "B02a"
        assert int(rows[2][1]) == 289
        assert int(rows[2][2]) == 9

        # ----------------------------------------------------------------------
        # Check the second csv file got written.
        csv_path = (
            self.__crystal_targets_directory
            / f"{self.crystal_plate_models[1].rockminer_collected_stem}_targets.csv"
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
