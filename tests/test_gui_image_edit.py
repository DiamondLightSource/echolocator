import logging

# API constants.
from dls_servbase_api.constants import Keywords as ProtocoljKeywords

# Utilities.
from dls_utilpack.describe import describe

# Things xchembku provides.
from xchembku_api.datafaces.context import Context as XchembkuDatafaceClientContext
from xchembku_api.datafaces.datafaces import xchembku_datafaces_get_default
from xchembku_api.models.crystal_well_autolocation_model import (
    CrystalWellAutolocationModel,
)
from xchembku_api.models.crystal_well_droplocation_model import (
    CrystalWellDroplocationModel,
)
from xchembku_api.models.crystal_well_filter_model import CrystalWellFilterModel
from xchembku_api.models.crystal_well_model import CrystalWellModel

# Context creator.
from echolocator_lib.contexts.contexts import Contexts
from echolocator_lib.guis.constants import Commands, Cookies, Keywords

# Object managing gui
from echolocator_lib.guis.guis import echolocator_guis_get_default

# Base class for the tester.
from tests.base_context_tester import BaseContextTester

logger = logging.getLogger(__name__)


# ----------------------------------------------------------------------------------------
class TestGuiImageEdit:
    def test(self, constants, logging_setup, output_directory):
        """ """

        configuration_file = "tests/configurations/laptop.yaml"
        GuiImageEditTester().main(constants, configuration_file, output_directory)


# ----------------------------------------------------------------------------------------
class GuiImageEditTester(BaseContextTester):
    """
    Class to test the gui.
    """

    async def _main_coroutine(self, constants, output_directory):
        """ """

        configurator = self.get_configurator()
        context_configuration = await configurator.load()

        # Reference the dict entry for the xchembku dataface.
        xchembku_dataface_specification = context_configuration[
            "xchembku_dataface_specification"
        ]

        # Make the xchembku client context, expected to be direct (no server).
        xchembku_client_context = XchembkuDatafaceClientContext(
            xchembku_dataface_specification
        )

        echolocator_contexts = Contexts().build_object(context_configuration)

        # Start the client context for the direct access to the xchembku.
        async with xchembku_client_context:
            # Reference the dataface object which the context has set up as the default.
            dataface = xchembku_datafaces_get_default()

            # Inject a well.
            crystal_well_model = await self.__inject(dataface, True, False)

            async with echolocator_contexts:

                # --------------------------------------------------------------------
                # Do what the Image Details tab does when it loads.

                # json_object[this.ENABLE_COOKIES] = [this.COOKIE_NAME, "IMAGE_LIST_UX"]
                # json_object[this.COMMAND] = this.FETCH_IMAGE;
                # json_object["uuid"] = this.#uuid;
                # json_object["direction"] = direction;

                # request = {
                #     ProtocoljKeywords.ENABLE_COOKIES: [
                #         Cookies.IMAGE_EDIT_UX,
                #         Cookies.IMAGE_LIST_UX,
                #     ],
                #     Keywords.COMMAND: Commands.FETCH_IMAGE,
                # }

                # response = await echolocator_guis_get_default().client_protocolj(
                #     request, cookies={}
                # )

                # logger.debug(describe("first fetch_image response", response))

                request = {
                    ProtocoljKeywords.ENABLE_COOKIES: [
                        Cookies.IMAGE_EDIT_UX,
                        Cookies.IMAGE_LIST_UX,
                    ],
                    Keywords.COMMAND: Commands.FETCH_IMAGE,
                    "uuid": crystal_well_model.uuid,
                }

                response = await echolocator_guis_get_default().client_protocolj(
                    request, cookies={}
                )

                logger.debug(describe("first fetch_image response", response))

    # ----------------------------------------------------------------------------------------

    async def __inject(self, dataface, autolocation: bool, droplocation: bool):
        """ """
        if not hasattr(self, "__injected_count"):
            self.__injected_count = 0

        filename = "%03d.jpg" % (self.__injected_count)
        self.__injected_count += 1

        # Write well record.
        m = CrystalWellModel(filename=filename)

        await dataface.originate_crystal_wells([m])

        if autolocation:
            # Add a crystal well autolocation.
            t = CrystalWellAutolocationModel(
                crystal_well_uuid=m.uuid,
                number_of_crystals=10,
            )

            await dataface.originate_crystal_well_autolocations([t])

        if droplocation:
            # Add a crystal well droplocation.
            t = CrystalWellDroplocationModel(
                crystal_well_uuid=m.uuid,
                confirmed_target_position_x=10,
                confirmed_target_position_y=11,
            )

            await dataface.originate_crystal_well_droplocations([t])

        return m
