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
class TestGui:
    def test(self, constants, logging_setup, output_directory):
        """ """

        configuration_file = "tests/configurations/laptop.yaml"
        GuiTester().main(constants, configuration_file, output_directory)


# ----------------------------------------------------------------------------------------
class GuiTester(BaseContextTester):
    """
    Class to test the gui.
    """

    async def _main_coroutine(self, constants, output_directory):
        """ """

        configurator = self.get_configurator()
        context_configuration = await configurator.load()

        gui_specification = context_configuration["echolocator_gui_specification"]
        type_specific_tbd = gui_specification["type_specific_tbd"]
        aiohttp_specification = type_specific_tbd["aiohttp_specification"]
        aiohttp_specification["search_paths"] = [output_directory]

        context = Contexts().build_object(context_configuration)

        async with context:

            # --------------------------------------------------------------------
            # Use protocolj to fetch a request from the dataface.
            # Simulates what javascript would do by ajax.

            # Load tabs, of which there are none at the start.
            # This establishes the cookie though.
            load_tabs_request = {
                Keywords.COMMAND: Commands.LOAD_TABS,
                ProtocoljKeywords.ENABLE_COOKIES: [Cookies.TABS_MANAGER],
            }

            response = await echolocator_guis_get_default().client_protocolj(
                load_tabs_request, cookies={}
            )

            # The response is json, with the last saved tab_id.
            assert Keywords.TAB_ID in response
            assert response[Keywords.TAB_ID] is None

            # We should also have cookies back.
            assert "__cookies" in response
            cookies = response["__cookies"]
            assert Cookies.TABS_MANAGER in cookies

            # Use the cookie name in the next requests.
            cookie_uuid = cookies[Cookies.TABS_MANAGER]

            # --------------------------------------------------------------------
            # Select a tab.
            # The response is json, but nothing really to see in it.

            select_tab_request = {
                Keywords.COMMAND: Commands.SELECT_TAB,
                ProtocoljKeywords.ENABLE_COOKIES: [Cookies.TABS_MANAGER],
                Keywords.TAB_ID: "123",
            }

            response = await echolocator_guis_get_default().client_protocolj(
                select_tab_request, cookies={Cookies.TABS_MANAGER: cookie_uuid}
            )

            # --------------------------------------------------------------------
            # Load tabs again, this time we should get the saved tab_id.
            response = await echolocator_guis_get_default().client_protocolj(
                load_tabs_request, cookies={Cookies.TABS_MANAGER: cookie_uuid}
            )

            logger.debug(describe("second load_tabs response", response))
            assert Keywords.TAB_ID in response
            assert response[Keywords.TAB_ID] == "123"

            # --------------------------------------------------------------------
            # Write a text file and fetch it through the http server.
            filename = "test.html"
            contents = "some test html"
            with open(f"{output_directory}/{filename}", "wt") as file:
                file.write(contents)
            await echolocator_guis_get_default().client_get_file(filename)
            # assert text == contents

            # Write a binary file and fetch it through the http server.
            filename = "test.exe"
            contents = "some test binary"
            with open(f"{output_directory}/{filename}", "wt") as file:
                file.write(contents)
            binary = await echolocator_guis_get_default().client_get_file(filename)
            # Binary comes back as bytes due to suffix of url filename.
            assert binary == contents.encode()
