import logging

# API constants.
from dls_servbase_api.constants import Keywords as ProtocoljKeywords

# Utilities.
from dls_utilpack.describe import describe

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

        context = Contexts().build_object(context_configuration)

        async with context:

            # --------------------------------------------------------------------
            # Do what the Image Details tab does when it loads.

            # json_object[this.ENABLE_COOKIES] = [this.COOKIE_NAME, "IMAGE_LIST_UX"]
            # json_object[this.COMMAND] = this.FETCH_IMAGE;
            # json_object["autoid"] = this.#autoid;
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
