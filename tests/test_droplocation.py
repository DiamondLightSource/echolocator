import logging

# API constants.
from dls_servbase_api.constants import Keywords as ProtocoljKeywords
from dls_servbase_lib.datafaces.context import Context as DlsServbaseDatafaceContext

# Utilities.
from dls_utilpack.describe import describe

# Things xchembku provides.
from xchembku_api.datafaces.context import Context as XchembkuDatafaceClientContext
from xchembku_api.datafaces.datafaces import xchembku_datafaces_get_default
from xchembku_api.models.crystal_plate_model import CrystalPlateModel
from xchembku_api.models.crystal_well_autolocation_model import (
    CrystalWellAutolocationModel,
)
from xchembku_api.models.crystal_well_droplocation_model import (
    CrystalWellDroplocationModel,
)
from xchembku_api.models.crystal_well_filter_model import CrystalWellFilterModel
from xchembku_api.models.crystal_well_model import CrystalWellModel

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
class TestDroplocation:
    def test(self, constants, logging_setup, output_directory):
        """ """

        configuration_file = "tests/configurations/service.yaml"
        DroplocationTester().main(
            constants,
            configuration_file,
            output_directory,
        )


# ----------------------------------------------------------------------------------------
class DroplocationTester(Base):
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
                        logger.debug(
                            "[ECHDON] finished running __run_part1, so gui_server_context going out of scope"
                        )

    # ----------------------------------------------------------------------------------------

    async def __run_part1(self, constants, output_directory):
        """ """
        # Reference the xchembku object which the context has set up as the default.
        xchembku = xchembku_datafaces_get_default()

        # Make the plate on which the wells reside.
        visit = "cm00001-1"
        crystal_plate_model = CrystalPlateModel(
            formulatrix__plate__id=10,
            barcode="98ab",
            visit=visit,
        )

        await xchembku.upsert_crystal_plates([crystal_plate_model])
        self.__crystal_plate_uuid = crystal_plate_model.uuid

        crystal_wells = []

        self.__cookies = {}
        # Inject some wells.
        crystal_wells.append(await self.__inject(xchembku, True, False))
        crystal_wells.append(await self.__inject(xchembku, True, False))
        crystal_wells.append(await self.__inject(xchembku, True, False))

        await self.__set_confirmed_target(xchembku, crystal_wells, 0, 1)
        await self.__set_confirmed_target(xchembku, crystal_wells, 1, 2)
        await self.__set_confirmed_target(xchembku, crystal_wells, 2, None)

        await self.__set_is_usable(xchembku, crystal_wells, 0, False)
        await self.__set_is_usable(xchembku, crystal_wells, 0, True)

    # ----------------------------------------------------------------------------------------

    async def __set_confirmed_target(
        self, xchembku, crystal_well_models, index1, index2
    ):
        """ """

        x = 100 + index1
        y = 200 + index1
        request = {
            ProtocoljKeywords.ENABLE_COOKIES: [
                Cookies.IMAGE_EDIT_UX,
                Cookies.IMAGE_LIST_UX,
            ],
            Keywords.COMMAND: Commands.UPDATE,
            Keywords.SHOULD_ADVANCE: True,
            "crystal_well_droplocation_model": {
                "crystal_well_uuid": crystal_well_models[index1].uuid,
                "confirmed_target_x": x,
                "confirmed_target_y": y,
                "is_usable": True,
            },
        }

        response = await echolocator_guis_get_default().client_protocolj(
            request, cookies=self.__cookies
        )

        self.__cookies = response["__cookies"]

        logger.debug(describe("first set_target response", response))

        assert "record" in response
        record = response["record"]
        assert "confirmation" in response
        assert "has been updated" in response["confirmation"]
        if index2 is not None:
            assert record is not None, f"index {index1}"
            assert record["uuid"] == crystal_well_models[index2].uuid, f"index {index1}"
            assert "advanced" in response["confirmation"]
        else:
            assert record is None
            assert "no more images" in response["confirmation"]

        # Fetch the record which should have been updated.
        fetched_models = await xchembku.fetch_crystal_wells_needing_droplocation(
            CrystalWellFilterModel(anchor=crystal_well_models[index1].uuid)
        )

        assert fetched_models[0].confirmed_target_x == x, f"index {index1}"
        assert fetched_models[0].confirmed_target_y == y, f"index {index1}"
        assert fetched_models[0].is_usable is True, f"index {index1}"

    # ----------------------------------------------------------------------------------------

    async def __set_is_usable(
        self,
        xchembku,
        crystal_well_models,
        index1,
        is_usable,
    ):
        """ """

        # Build the request to change only the is_usable field.
        request = {
            ProtocoljKeywords.ENABLE_COOKIES: [
                Cookies.IMAGE_EDIT_UX,
                Cookies.IMAGE_LIST_UX,
            ],
            Keywords.COMMAND: Commands.UPDATE,
            Keywords.SHOULD_ADVANCE: False,
            "crystal_well_droplocation_model": {
                "crystal_well_uuid": crystal_well_models[index1].uuid,
                "is_usable": is_usable,
            },
        }

        # Send the ajax request to the gui.
        response = await echolocator_guis_get_default().client_protocolj(
            request, cookies=self.__cookies
        )

        assert "record" not in response
        assert "confirmation" in response
        assert "has been updated" in response["confirmation"]

        # Fetch the record which should have been updated.
        fetched_models = await xchembku.fetch_crystal_wells_needing_droplocation(
            CrystalWellFilterModel(anchor=crystal_well_models[index1].uuid)
        )

        # These should remain changed from when we set them previously in the test.
        x = 100 + index1
        y = 200 + index1

        assert fetched_models[0].confirmed_target_x == x, f"index {index1}"
        assert fetched_models[0].confirmed_target_y == y, f"index {index1}"
        assert fetched_models[0].is_usable is is_usable, f"index {index1}"

    # ----------------------------------------------------------------------------------------

    async def __inject(self, xchembku, autolocation: bool, droplocation: bool):
        """ """
        if not hasattr(self, "injected_count"):
            self.injected_count = 0

        self.injected_count += 1

        filename = "/tmp/%03d.jpg" % (self.injected_count)

        # Write well record.
        m = CrystalWellModel(
            position="%2dA_1" % (self.injected_count),
            filename=filename,
            crystal_plate_uuid=self.__crystal_plate_uuid,
        )

        await xchembku.upsert_crystal_wells([m])

        if autolocation:
            # Add a crystal well autolocation.
            t = CrystalWellAutolocationModel(
                crystal_well_uuid=m.uuid,
                number_of_crystals=self.injected_count,
                auto_target_x=self.injected_count * 10 + 0,
                auto_target_y=self.injected_count * 10 + 1,
            )

            await xchembku.originate_crystal_well_autolocations([t])

        if droplocation:
            # Add a crystal well droplocation.
            t = CrystalWellDroplocationModel(
                crystal_well_uuid=m.uuid,
                confirmed_target_x=self.injected_count * 10 + 2,
                confirmed_target_y=self.injected_count * 10 + 3,
            )

            await xchembku.originate_crystal_well_droplocations([t])

        return m
