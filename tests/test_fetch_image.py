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

        # Inject some wells.
        crystal_wells.append(await self.__inject(xchembku, False, False))
        crystal_wells.append(await self.__inject(xchembku, True, True))
        crystal_wells.append(await self.__inject(xchembku, True, False))
        crystal_wells.append(await self.__inject(xchembku, True, True))
        crystal_wells.append(await self.__inject(xchembku, True, True))
        crystal_wells.append(await self.__inject(xchembku, True, False))

        await self.__request_initial(crystal_wells)
        await self.__request_anchor(crystal_wells)
        await self.__request_forward(crystal_wells)
        await self.__request_forward_undecided(crystal_wells)

    # ----------------------------------------------------------------------------------------

    async def __request_initial(self, crystal_wells):
        """ """

        # --------------------------------------------------------------------
        # Do what the Image Details tab does when it loads.

        # json_object[this.ENABLE_COOKIES] = [this.COOKIE_NAME, "IMAGE_LIST_UX"]
        # json_object[this.COMMAND] = this.FETCH_IMAGE;
        # json_object["uuid"] = this.#uuid;
        # json_object["direction"] = direction;

        request = {
            ProtocoljKeywords.ENABLE_COOKIES: [
                Cookies.IMAGE_EDIT_UX,
                Cookies.IMAGE_LIST_UX,
            ],
            Keywords.COMMAND: Commands.FETCH_IMAGE,
        }

        response = await echolocator_guis_get_default().client_protocolj(
            request, cookies={}
        )

        logger.debug(describe("first fetch_image response", response))

        record = response["record"]
        assert record is None

    # ----------------------------------------------------------------------------------------

    async def __request_anchor(self, crystal_wells):
        """ """

        request = {
            ProtocoljKeywords.ENABLE_COOKIES: [
                Cookies.IMAGE_EDIT_UX,
                Cookies.IMAGE_LIST_UX,
            ],
            Keywords.COMMAND: Commands.FETCH_IMAGE,
            "uuid": crystal_wells[2].uuid,
        }

        response = await echolocator_guis_get_default().client_protocolj(
            request, cookies={}
        )

        logger.debug(describe("first fetch_image response", response))

        record = response["record"]
        assert record["uuid"] == crystal_wells[2].uuid

    # ----------------------------------------------------------------------------------------

    async def __request_forward(self, crystal_wells):
        """ """

        request = {
            ProtocoljKeywords.ENABLE_COOKIES: [
                Cookies.IMAGE_EDIT_UX,
                Cookies.IMAGE_LIST_UX,
            ],
            Keywords.COMMAND: Commands.FETCH_IMAGE,
            "uuid": crystal_wells[2].uuid,
            "direction": 1,
        }

        response = await echolocator_guis_get_default().client_protocolj(
            request, cookies={}
        )

        logger.debug(describe("fetch_image response", response))

        record = response["record"]
        assert record["uuid"] == crystal_wells[3].uuid
        assert record["confirmed_target_position_x"] is not None

        # -------------------------------------------------------------------------------------
        # Same query again, but rely on cookies for values.
        request.pop("uuid")

        response = await echolocator_guis_get_default().client_protocolj(
            request, cookies=response["__cookies"]
        )

        logger.debug(describe("fetch_image response", response))

        record = response["record"]
        assert record["uuid"] == crystal_wells[3].uuid
        assert record["confirmed_target_position_x"] is not None

    # ----------------------------------------------------------------------------------------

    async def __request_forward_undecided(self, crystal_wells):
        """ """

        request = {
            ProtocoljKeywords.ENABLE_COOKIES: [
                Cookies.IMAGE_EDIT_UX,
                Cookies.IMAGE_LIST_UX,
            ],
            Keywords.COMMAND: Commands.FETCH_IMAGE,
            "uuid": crystal_wells[2].uuid,
            "direction": 1,
            "should_show_only_undecided": True,
        }

        response = await echolocator_guis_get_default().client_protocolj(
            request, cookies={}
        )

        logger.debug(describe("fetch_image response", response))

        record = response["record"]
        assert record["uuid"] == crystal_wells[5].uuid
        assert record["confirmed_target_position_x"] is None

        # -------------------------------------------------------------------------------------
        # Same query again, but rely on cookies for values.
        request.pop("uuid")
        request.pop("should_show_only_undecided")

        response = await echolocator_guis_get_default().client_protocolj(
            request, cookies=response["__cookies"]
        )

        logger.debug(describe("fetch_image response", response))

        record = response["record"]
        assert record["uuid"] == crystal_wells[5].uuid
        assert record["confirmed_target_position_x"] is None

    # ----------------------------------------------------------------------------------------

    async def __inject(self, xchembku, autolocation: bool, droplocation: bool):
        """ """
        if not hasattr(self, "injected_count"):
            self.injected_count = 0

        filename = "/tmp/%03d.jpg" % (self.injected_count)

        # Write well record.
        m = CrystalWellModel(
            filename=filename, crystal_plate_uuid=self.__crystal_plate_uuid
        )

        await xchembku.upsert_crystal_wells([m])

        if autolocation:
            # Add a crystal well autolocation.
            t = CrystalWellAutolocationModel(
                crystal_well_uuid=m.uuid,
                number_of_crystals=self.injected_count,
                auto_target_position_x=self.injected_count * 10 + 1,
                auto_target_position_y=self.injected_count * 10 + 2,
            )

            await xchembku.originate_crystal_well_autolocations([t])

        if droplocation:
            # Add a crystal well droplocation.
            t = CrystalWellDroplocationModel(
                crystal_well_uuid=m.uuid,
                confirmed_target_position_x=self.injected_count * 10 + 3,
                confirmed_target_position_y=self.injected_count * 10 + 4,
            )

            await xchembku.originate_crystal_well_droplocations([t])

        self.injected_count += 1

        return m
