import logging
from pathlib import Path

# API constants.
from dls_servbase_lib.datafaces.context import Context as DlsServbaseDatafaceContext
from dls_utilpack.visit import get_xchem_subdirectory

# Soakdb3 database.
from soakdb3_api.databases.constants import Tablenames

# Client for direct access to the soakdb3 database for seeding it.
from soakdb3_api.datafaces.context import Context as Soakdb3DatafaceClientContext
from soakdb3_api.datafaces.datafaces import (
    datafaces_get_default as soakdb3_datafaces_get_default,
)

# The service process startup/teardown context.
from soakdb3_lib.datafaces.context import Context as Soakdb3DatafaceServerContext

# Things xchembku provides.
from xchembku_api.datafaces.context import Context as XchembkuDatafaceClientContext
from xchembku_api.datafaces.datafaces import xchembku_datafaces_get_default
from xchembku_api.models.crystal_well_filter_model import CrystalWellFilterModel
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
class TestExportToSoakdb3:
    def test(self, constants, logging_setup, output_directory):
        """ """

        configuration_file = "tests/configurations/service.yaml"
        ExportToSoakdb3Tester().main(
            constants,
            configuration_file,
            output_directory,
        )


# ----------------------------------------------------------------------------------------
class ExportToSoakdb3Tester(Base):
    """
    Class to test the gui fetch_image endpoint.
    """

    async def _main_coroutine(self, constants, output_directory):
        """ """

        multiconf = self.get_multiconf()
        multiconf_dict = await multiconf.load()

        # Reference the dict entry for the soakdb3 dataface.
        soakdb3_dataface_specification = multiconf_dict[
            "soakdb3_dataface_specification"
        ]

        # Make the soakdb3 server context.
        soakdb3_server_context = Soakdb3DatafaceServerContext(
            soakdb3_dataface_specification
        )

        # Make the soakdb3 CLIENT context.
        soakdb3_client_context = Soakdb3DatafaceClientContext(
            soakdb3_dataface_specification
        )

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

        # Start the soakdb3 server context which includes the direct or network-addressable service.
        async with soakdb3_server_context:
            # Client for direct access to the soakdb3 database for seeding it.
            async with soakdb3_client_context:
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
                                    await self.__run_the_test(
                                        constants, output_directory
                                    )

    # ----------------------------------------------------------------------------------------

    async def __run_the_test(self, constants, output_directory):
        """ """

        # Reference the soakdb3 dataface object which the context has set up as the default.
        soakdb3_dataface = soakdb3_datafaces_get_default()

        # Reference the xchembku object which the context has set up as the default.
        self.__xchembku = xchembku_datafaces_get_default()

        self.__output_directory = output_directory

        await self.inject_plate(self.__xchembku)

        self.__visit_directory = (
            Path(self.__output_directory)
            / "labxchem"
            / get_xchem_subdirectory(self.visit)
        )

        # Soakdb3 expects visitid to be a visit directory with processing tacked onto the end.
        # This is because of how the soadkb3 VBA in the Excel works.
        visitid = str(self.__visit_directory / "processing")

        (Path(visitid)).mkdir(parents=True)

        # ----------------------------------------------------------------
        # Seed the necessary fields in the head table.

        protein = "P1"
        drop_volume = 3.1

        head_record = {
            "Protein": protein,
            "DropVolume": drop_volume,
        }

        # Insert these fields as the (single) row in the soakdb3 database's head table.
        await soakdb3_dataface.insert(  # type: ignore
            visitid,
            Tablenames.HEAD,
            [head_record],
        )

        # ----------------------------------------------------------------

        crystal_wells = []

        # Inject some wells.
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
            Keywords.COMMAND: Commands.EXPORT_TO_SOAKDB3,
            "visit_filter": self.visit,
        }

        response = await echolocator_guis_get_default().client_protocolj(
            request, cookies={}
        )

        # Expect confirmation message in response.
        assert "confirmation" in response
        assert "exported" in response["confirmation"]

        # Check the results stored in soakdbb3, there should be no change to the first ones.
        queried_models = await self.__xchembku.fetch_soakdb3_crystal_wells(
            str(self.__visit_directory / "processing")
        )
        assert len(queried_models) == 3

        # The position constants are fromt the Swiss3 microns computation.
        # Note the order here: row_first_position gives get all letters in row 01 before any letters in row 02.
        assert queried_models[0].CrystalWell == "B01a"
        assert int(queried_models[0].EchoX) == 6
        assert int(queried_models[0].EchoY) == -274

        assert queried_models[1].CrystalWell == "A02a"
        assert int(queried_models[1].EchoX) == -561
        assert int(queried_models[1].EchoY) == -842

        assert queried_models[2].CrystalWell == "B02a"
        assert int(queried_models[2].EchoX) == 289
        assert int(queried_models[2].EchoY) == 9

        # Check the results stored in xchembku, the exported flag should be set.
        crystal_well_models = (
            await self.__xchembku.fetch_crystal_wells_needing_droplocation(
                CrystalWellFilterModel(is_exported_to_soakdb3=True)
            )
        )
        assert len(crystal_well_models) == 3
